#!/usr/bin/env python3
"""Measure supported source, run explicit checks, and compare refactor snapshots."""

import argparse
import ast
from collections import Counter
from datetime import datetime, timezone
import fnmatch
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import shutil
import signal
import subprocess
import sys
import tempfile

try:
    import lizard
    from lizard_languages import get_reader_for
except ImportError:
    lizard = None


SCHEMA = 1
DEFAULT_DIRS = frozenset({
    ".git", ".hg", ".svn", ".refactor", ".venv", "venv", "__pycache__",
    "node_modules", "vendor", "dist", "build", "target", ".next", ".tools",
})
NON_SOURCE = frozenset("""
md rst txt json jsonl yaml yml toml ini cfg conf lock csv tsv xml html htm css scss
sass less svg png jpg jpeg gif webp ico pdf zip gz tar bz2 xz 7z mp3 mp4 wav webm
woff woff2 ttf eot otf map pyc pyo so dll dylib exe o a class jar sqlite db log
ipynb sum mod props targets csproj sln pbxproj plist resx sqlproj editorconfig
""".split())
# Detection labels are deliberately separate from installed analyzer support.
EXTENSIONS = {
    "Python": "py pyw pyi", "C/C++": "c cpp cc cxx h hh hpp hxx",
    "Java": "java", "C#": "cs", "JavaScript": "js cjs mjs jsx",
    "TypeScript": "ts tsx mts cts", "Objective-C": "m mm", "TTCN": "ttcn ttcnpp",
    "Ruby": "rb", "PHP": "php", "Swift": "swift", "Scala": "scala",
    "GDScript": "gd", "Go": "go", "Lua": "lua", "Rust": "rs",
    "Fortran": "f70 f90 f95 f03 f08 f for ftn fpp", "Kotlin": "kt kts",
    "Solidity": "sol", "Erlang": "erl hrl es escript", "Zig": "zig",
    "Vue": "vue", "Perl": "pl pm", "Structured Text": "st", "R": "r",
    "SQL": "sql pks pkb pls plb pck", "COBOL": "cbl cob cobol", "Dart": "dart",
    "Elixir": "ex exs", "Haskell": "hs lhs", "Shell": "sh bash zsh fish",
    "Clojure": "clj cljs cljc edn", "F#": "fs fsx fsi", "OCaml": "ml mli",
    "Julia": "jl", "Svelte": "svelte", "PowerShell": "ps1 psm1",
    "Assembly": "asm s", "Visual Basic": "vb", "Lisp": "lisp lsp cl",
}
LABELS = {"." + ext: name for name, exts in EXTENSIONS.items() for ext in exts.split()}
DEFAULT_CONFIG = {"max_complexity": None, "exclude": [], "extensions": {},
                  "checks": [], "max_file_bytes": 2_000_000}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def validate_config(config):
    if not isinstance(config, dict) or set(config) - set(DEFAULT_CONFIG):
        raise ValueError("Config must be an object with only documented keys")
    result = {**DEFAULT_CONFIG, **config}
    limit = result["max_complexity"]
    if limit is not None and (type(limit) is not int or limit < 1):
        raise ValueError("max_complexity must be a positive integer")
    if type(result["max_file_bytes"]) is not int or result["max_file_bytes"] < 1:
        raise ValueError("max_file_bytes must be a positive integer")
    if not isinstance(result["exclude"], list) or not all(
            isinstance(x, str) and x for x in result["exclude"]):
        raise ValueError("exclude must be an array of glob strings")
    if not isinstance(result["extensions"], dict) or not all(
            isinstance(k, str) and k.startswith(".") and isinstance(v, str) and v
            for k, v in result["extensions"].items()):
        raise ValueError("extensions must map dotted extensions to language names")
    if not isinstance(result["checks"], list):
        raise ValueError("checks must be an array")
    names = set()
    for check in result["checks"]:
        if not isinstance(check, dict) or set(check) - {
                "name", "command", "languages", "timeout_seconds", "version_command"}:
            raise ValueError("Unknown check option")
        if not isinstance(check.get("name"), str) or not check["name"] or check["name"] in names:
            raise ValueError("Each check needs a unique name")
        names.add(check["name"])
        for key in ["command"] + (["version_command"] if "version_command" in check else []):
            argv = check.get(key)
            if not isinstance(argv, list) or not argv or not all(
                    isinstance(x, str) and "\0" not in x for x in argv) or not argv[0]:
                raise ValueError(f"{key} must be a nonempty argv array, not a shell string")
        if "languages" in check and (not isinstance(check["languages"], list) or not all(
                isinstance(x, str) and x for x in check["languages"])):
            raise ValueError("check languages must be an array of language names")
        timeout = check.get("timeout_seconds", 60)
        if type(timeout) not in (int, float) or not 0 < timeout <= 3600:
            raise ValueError("timeout_seconds must be between 0 and 3600")
    return result


def run_command(argv, root, timeout=60):
    """Avoid a shell, bound captured output, and terminate timed-out process groups."""
    with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
        try:
            process = subprocess.Popen(argv, cwd=root, stdout=stdout, stderr=stderr,
                                       stdin=subprocess.DEVNULL, start_new_session=True)
        except OSError as exc:
            return {"status": "unavailable", "reason": str(exc)}
        try:
            code = process.wait(timeout=timeout)
            status = "passed" if code == 0 else "failed"
        except subprocess.TimeoutExpired:
            if os.name == "posix":
                os.killpg(process.pid, signal.SIGKILL)
            else:
                process.kill()
            process.wait()
            code, status = None, "timeout"
        result = {"status": status, "exit_code": code}
        for name, stream in [("stdout", stdout), ("stderr", stderr)]:
            size = stream.tell()
            stream.seek(0)
            result[name] = stream.read(8192).decode("utf-8", errors="replace")
            result[name + "_truncated"] = size > 8192
        return result


def tool_identity(argv, root):
    executable = argv[0]
    if os.path.dirname(executable):
        path = (root / executable).resolve()
    else:
        resolved = shutil.which(executable)
        path = Path(resolved).resolve() if resolved else None
    result = {"executable": str(path) if path else None}
    try:
        result["sha256"] = digest(path.read_bytes()) if path else None
    except OSError:
        result["sha256"] = None
    return result


def tool_metadata(config, root, detected_languages):
    versions = {}
    for package in ("lizard", "pathspec", "Pygments"):
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            versions[package] = None
    checks = {}
    for check in config["checks"]:
        if "languages" in check and not set(check["languages"]) & detected_languages:
            checks[check["name"]] = {"status": "skipped"}
            continue
        meta = tool_identity(check["command"], root)
        if "version_command" in check:
            meta["version_tool"] = tool_identity(check["version_command"], root)
            meta["version"] = run_command(check["version_command"], root,
                                          check.get("timeout_seconds", 60))
        checks[check["name"]] = meta
    return {"python": platform.python_version(), "packages": versions,
            "analyzer_available": lizard is not None,
            "runner_sha256": digest(Path(__file__).read_bytes()), "checks": checks}


def excluded(relative, config):
    return any(fnmatch.fnmatchcase(relative, pattern) or
               fnmatch.fnmatchcase(relative + "/", pattern)
               for pattern in config["exclude"])


def collect_files(scope, root, session, config):
    skipped, candidates, ignore_files = Counter(), [], {}
    def onerror(error):
        raise ValueError(f"Cannot enumerate source: {error}")
    if scope.is_file():
        candidates = [scope]
    else:
        for current, dirs, files in os.walk(scope, followlinks=False, onerror=onerror):
            base = Path(current)
            kept = []
            for name in dirs:
                path = base / name
                if path.is_symlink() or path.resolve() == session or name in DEFAULT_DIRS:
                    skipped["excluded_directories"] += 1
                elif excluded(path.relative_to(root).as_posix(), config):
                    skipped["excluded_directories"] += 1
                else:
                    kept.append(name)
            dirs[:] = sorted(kept)
            for name in sorted(files):
                path = base / name
                if name == ".gitignore":
                    ignore_files[str(path)] = digest(path.read_bytes())
                if path.is_symlink():
                    skipped["symlinks"] += 1
                elif excluded(path.relative_to(root).as_posix(), config):
                    skipped["excluded_files"] += 1
                else:
                    candidates.append(path)
    git_status = "not_a_git_repository"
    git = shutil.which("git")
    if git:
        probe = subprocess.run([git, "rev-parse", "--show-toplevel"], cwd=root,
                               capture_output=True, timeout=10)
        if probe.returncode == 0:
            # --no-index makes ignore behavior consistent for tracked/untracked source.
            payload = b"\0".join(os.fsencode(str(p)) for p in candidates) + b"\0"
            ignored = set()
            if candidates:
                result = subprocess.run([git, "check-ignore", "--no-index", "-z", "--stdin"],
                                        cwd=root, input=payload, capture_output=True, timeout=30)
                if result.returncode not in (0, 1):
                    raise ValueError("git check-ignore failed; cannot establish analysis scope")
                ignored = set(result.stdout.split(b"\0"))
            candidates = [p for p in candidates if os.fsencode(str(p)) not in ignored]
            skipped["gitignored_files"] = len(ignored - {b""})
            git_status = "respected_including_tracked_files"
            git_root = Path(os.fsdecode(probe.stdout).strip())
            for parent in [root, *root.parents]:
                file = parent / ".gitignore"
                if file.is_file():
                    ignore_files[str(file)] = digest(file.read_bytes())
                if parent == git_root:
                    break
            for command in ([git, "rev-parse", "--git-path", "info/exclude"],
                            [git, "config", "--path", "--get", "core.excludesFile"]):
                setting = subprocess.run(command, cwd=root, capture_output=True, timeout=10)
                if setting.returncode == 0 and setting.stdout.strip():
                    file = (root / os.fsdecode(setting.stdout).strip()).expanduser().resolve()
                    ignore_files[str(file)] = digest(file.read_bytes()) if file.is_file() else None
            # Git uses this default even when core.excludesFile is unset.
            default_ignore = Path(os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))) / "git/ignore"
            if default_ignore.is_file():
                ignore_files[str(default_ignore)] = digest(default_ignore.read_bytes())
    else:
        git_status = "git_unavailable"
    return sorted(candidates), dict(skipped), {"gitignore": git_status,
                                              "ignore_files": ignore_files}


def identify(path, config):
    suffix = path.suffix.lower()
    override = config["extensions"].get(suffix)
    if override:
        representative = EXTENSIONS.get(override, "").split()
        return override, "source." + representative[0] if representative else "source.unsupported"
    if suffix in LABELS:
        return LABELS[suffix], path.name
    if lizard:
        reader = get_reader_for(path.name)
        if reader:
            return reader.__name__.removesuffix("Reader"), path.name
    if suffix.lstrip(".") in NON_SOURCE or path.name.startswith(".") or path.name in {
            "LICENSE", "COPYING", "NOTICE", "Makefile", "Dockerfile", "Gemfile"}:
        return None, path.name
    if suffix:
        return "Unknown (" + suffix + ")", path.name
    try:
        with path.open("rb") as stream:
            first_line = stream.read(200).split(b"\n")[0].decode("utf-8", errors="replace")
        if first_line.startswith("#!"):
            for token, name, filename in [("python", "Python", "source.py"),
                                           ("ruby", "Ruby", "source.rb"),
                                           ("node", "JavaScript", "source.js"),
                                           ("sh", "Shell", "source.sh"),
                                           ("perl", "Perl", "source.pl")]:
                if token in first_line:
                    return name, filename
            return "Unknown (shebang)", path.name
    except OSError:
        return "Unknown (unreadable)", path.name
    return None, path.name


def measure_file(path, relative, language, analyzer_name, config):
    result = {"path": relative, "language": language, "functions": []}
    try:
        if path.stat().st_size > config["max_file_bytes"]:
            return {**result, "status": "skipped", "reason": "Exceeds max_file_bytes"}
        data = path.read_bytes()
        result["sha256"] = digest(data)
        if b"\0" in data:
            return {**result, "status": "unsupported", "reason": "Binary or non-UTF-8 source"}
        source = data.decode("utf-8-sig")
        if not lizard:
            return {**result, "status": "unavailable", "reason": "Install scripts/requirements.txt"}
        if get_reader_for(analyzer_name) is None:
            return {**result, "status": "unsupported", "reason": "Installed Lizard has no reader for this source"}
        if language == "Python":
            ast.parse(source, filename=relative)
        info = lizard.analyze_file.analyze_source_code(analyzer_name, source)
        result["nloc"] = info.nloc
        result["functions"] = [{
            "name": f.name, "line": f.start_line, "end_line": f.end_line,
            "cyclomatic_complexity": f.cyclomatic_complexity,
            "nloc": f.nloc, "parameters": f.parameter_count,
        } for f in info.function_list]
        result["status"] = "measured" if result["functions"] else "no_functions"
        if not result["functions"]:
            result["reason"] = "No functions recognized; no function metrics available"
        return result
    except (OSError, UnicodeError, SyntaxError) as exc:
        return {**result, "status": "error", "reason": str(exc)}
    except Exception as exc:
        return {**result, "status": "error", "reason": f"Analyzer error: {type(exc).__name__}: {exc}"}


def metrics(files):
    functions = [f for file in files for f in file["functions"]]
    complexity = [f["cyclomatic_complexity"] for f in functions]
    return {
        "files": len(files), "analyzed_files": sum(f["status"] == "measured" for f in files),
        "functions": len(functions), "max_cyclomatic_complexity": max(complexity, default=None),
        "mean_cyclomatic_complexity": round(sum(complexity) / len(complexity), 3) if complexity else None,
        "max_function_nloc": max((f["nloc"] for f in functions), default=None),
        "max_parameters": max((f["parameters"] for f in functions), default=None),
    }


def make_report(scope, root, session, config, phase):
    paths, skipped, selection = collect_files(scope, root, session, config)
    files = []
    for path in paths:
        language, analyzer_name = identify(path, config)
        if language is None:
            skipped["non_source_files"] = skipped.get("non_source_files", 0) + 1
            continue
        files.append(measure_file(path, path.relative_to(root).as_posix(), language,
                                  analyzer_name, config))
    groups = {}
    for language in sorted({f["language"] for f in files}):
        group = [f for f in files if f["language"] == language]
        states = {f["status"] for f in group}
        status = next(iter(states)) if len(states) == 1 else "partial"
        groups[language] = {**metrics(group), "status": status}
        reasons = sorted({f["reason"] for f in group if "reason" in f})
        if reasons:
            groups[language]["reason"] = "; ".join(reasons)
    # Tool metadata is captured before explicit checks so commands cannot silently
    # change which version is credited with producing this snapshot.
    tools = tool_metadata(config, root, set(groups))
    checks = []
    for check in config["checks"]:
        row = {"name": check["name"], "command": check["command"]}
        if "languages" in check and not set(check["languages"]) & set(groups):
            checks.append({**row, "status": "skipped", "reason": "No matching language in scope"})
        else:
            checks.append({**row, **run_command(check["command"], root,
                                               check.get("timeout_seconds", 60))})
    violations = []
    if config["max_complexity"] is not None:
        violations = [{"path": file["path"], **f, "limit": config["max_complexity"]}
                      for file in files for f in file["functions"]
                      if f["cyclomatic_complexity"] > config["max_complexity"]]
    incomplete = not files or any(f["status"] != "measured" for f in files)
    incomplete |= any(c["status"] not in {"passed", "failed", "skipped"} for c in checks)
    incomplete |= any("version" in c and c["version"]["status"] != "passed"
                      for c in tools["checks"].values())
    failed = bool(violations) or any(c["status"] == "failed" for c in checks)
    gated = config["max_complexity"] is not None or any(c["status"] == "passed" for c in checks)
    status = "failed" if failed else "incomplete" if incomplete else "passed" if gated else "measured"
    return {"schema_version": SCHEMA, "phase": phase, "created_at": timestamp(),
            "root": str(root), "scope": str(scope), "status": status,
            "coverage_complete": not incomplete, "config": config,
            "analysis": {"tools": tools, "selection": selection,
                         "default_excluded_directories": sorted(DEFAULT_DIRS),
                         "not_built_in": ["nesting", "dependency cycles", "layer boundaries"],
                         "limitation": "Lizard is a partial parser. Metrics do not prove syntax, SOLID, or behavior."},
            "metrics": metrics(files), "languages": groups, "files": files,
            "checks": checks, "violations": violations, "skipped": skipped}


def deltas(before, after):
    return {key: {"before": before.get(key), "after": after.get(key),
                  "delta": after[key] - before[key] if before.get(key) is not None and
                  after.get(key) is not None else None}
            for key in sorted(before.keys() | after.keys())}


def compare(before, after):
    reasons = [key + " changed" for key in ("schema_version", "root", "scope", "config")
               if before.get(key) != after.get(key)]
    for key in ("tools", "selection", "default_excluded_directories"):
        if before["analysis"].get(key) != after["analysis"].get(key):
            reasons.append(key + " changed")
    result = {"schema_version": SCHEMA, "status": "incompatible" if reasons else
              "comparable" if before["coverage_complete"] and after["coverage_complete"] else "partial",
              "reasons": reasons}
    if reasons:
        return result
    result["metrics"] = deltas(before["metrics"], after["metrics"])
    result["languages"] = {name: deltas(metrics([f for f in before["files"] if f["language"] == name]),
                                        metrics([f for f in after["files"] if f["language"] == name]))
                           for name in sorted(before["languages"].keys() | after["languages"].keys())}
    old, new = {f["path"] for f in before["files"]}, {f["path"] for f in after["files"]}
    result["files_added"], result["files_removed"] = sorted(new - old), sorted(old - new)
    return result


def save_json(path, value, immutable=False):
    data = json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if immutable:
        with path.open("x", encoding="utf-8") as stream:
            stream.write(data)
    else:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=".report-", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(data)
        temporary.replace(path)


def validate_baseline(before):
    """Reject incomplete/corrupted snapshots before using them as configuration."""
    try:
        if not isinstance(before, dict) or before.get("schema_version") != SCHEMA:
            raise ValueError("Baseline schema is incompatible")
        for key in ("config", "analysis", "metrics", "languages"):
            if not isinstance(before[key], dict):
                raise ValueError("Malformed baseline: " + key)
        for key in ("root", "scope"):
            if not isinstance(before[key], str):
                raise ValueError("Malformed baseline: " + key)
        if type(before["coverage_complete"]) is not bool or not isinstance(before["files"], list):
            raise ValueError("Malformed baseline coverage/files")
        if set(before["metrics"]) != set(metrics([])) or not all(
                value is None or type(value) in (int, float) for value in before["metrics"].values()):
            raise ValueError("Malformed baseline metrics")
        for file in before["files"]:
            if not all(isinstance(file[key], str) for key in ("path", "language", "status")):
                raise ValueError("Malformed baseline file")
            if not isinstance(file["functions"], list):
                raise ValueError("Malformed baseline functions")
            for function in file["functions"]:
                if not all(type(function[key]) is int for key in ("cyclomatic_complexity", "nloc", "parameters")):
                    raise ValueError("Malformed baseline function metrics")
    except (KeyError, TypeError) as exc:
        raise ValueError("Malformed baseline: missing or invalid report fields") from exc


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise ValueError(message)


def main():
    parser = Parser(description=__doc__)
    parser.add_argument("path", type=Path, help="Source directory or single file")
    parser.add_argument("--phase", choices=("before", "after"), required=True)
    parser.add_argument("--session", type=Path, help="Same .refactor/session_* folder for both phases")
    parser.add_argument("--config", type=Path, help="Explicit JSON config; commands run without a shell")
    parser.add_argument("--max-complexity", type=int, default=None, help="Optional repository threshold")
    parser.add_argument("--exclude", action="append", default=None, help="Relative glob; repeatable")
    args = parser.parse_args()
    scope = args.path.resolve(strict=True)
    if not (scope.is_dir() or scope.is_file()):
        raise ValueError("Source must be a regular file or directory")
    root = scope if scope.is_dir() else scope.parent
    if args.phase == "after" and args.session is None:
        raise ValueError("after requires --session with an existing before.json")
    session = args.session.resolve() if args.session else root / ".refactor" / (
        "session_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ"))
    baseline_path = session / "before.json"
    before = None
    if args.phase == "before" and baseline_path.exists():
        raise ValueError("before.json already exists; use another session to keep the baseline")
    if args.phase == "after":
        if not baseline_path.is_file():
            raise ValueError("No before.json in this session")
        before = json.loads(baseline_path.read_text(encoding="utf-8"))
        validate_baseline(before)
    config = before["config"] if before else {}
    if args.config:
        config = json.loads(args.config.read_text(encoding="utf-8"))
    if not isinstance(config, dict):
        raise ValueError("Config must be a JSON object")
    config = dict(config)
    if args.max_complexity is not None:
        config["max_complexity"] = args.max_complexity
    if args.exclude is not None:
        config["exclude"] = args.exclude
    config = validate_config(config)
    session.mkdir(parents=True, exist_ok=True)
    if before and (before["config"] != config or before["scope"] != str(scope)):
        save_json(session / "comparison.json", {"schema_version": SCHEMA,
                  "status": "incompatible", "reasons": ["Source scope or configuration changed"]})
        raise ValueError("Source scope or configuration changed; start a new baseline")
    report = make_report(scope, root, session, config, args.phase)
    output = session / (args.phase + ".json")
    save_json(output, report, immutable=args.phase == "before")
    print(f"{report['status'].upper()}: {len(report['files'])} source files, "
          f"{report['metrics']['functions']} recognized functions")
    for name, group in report["languages"].items():
        print(f"  {name}: {group['status']}; {group['analyzed_files']}/{group['files']} files measured")
    print(f"Report: {output}")
    if before:
        comparison = compare(before, report)
        save_json(session / "comparison.json", comparison)
        print(f"Comparison: {comparison['status']}")
        if comparison["status"] == "incompatible":
            print("  " + "; ".join(comparison["reasons"]))
            return 3
        change = comparison["metrics"]["max_cyclomatic_complexity"]
        print(f"  Maximum complexity: {change['before']} -> {change['after']} (delta {change['delta']})")
    return {"measured": 0, "passed": 0, "failed": 1, "incomplete": 2}[report["status"]]


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(3)
