# Structural checks

Use [check-structure.py](../scripts/check-structure.py) before and after refactoring. It measures function complexity, size, and parameter counts for supported languages.

## Run

Use Python 3.9+ in a virtual environment. From this skill's directory:

```sh
python -m pip install -r scripts/requirements.txt
python scripts/check-structure.py /path/to/code \
  --session /path/to/code/.refactor/session_TIMESTAMP --phase before
```

After refactoring, repeat with `--phase after`. Use the same source path, session, tools, and configuration. The source can be a directory or one file; after runs inherit the baseline settings.

## Read the results

- The session contains immutable `before.json`, latest `after.json`, and `comparison.json`.
- Review per-language coverage and compatibility before interpreting changes. Unsupported, unavailable, or skipped analysis is incomplete.
- Metrics use partial parsing; they do not prove correct behavior or SOLID compliance. Keep behavior checks and inspect responsibilities. Do not split code merely to lower a score.
- Exit codes: `0` measured or passed; `1` a limit/check failed; `2` incomplete; `3` invalid configuration/invocation or incompatible comparison.

## Optional settings

- Add `--exclude GLOB` for additional exclusions. Common dependency/output folders and Git-ignored files are already excluded when Git is available.
- Use `--max-complexity N` only for an agreed repository limit.
- Use `--config FILE` for extra checks. Each entry in `checks` needs a `name` and a `command` argument array; optional fields are `languages`, `timeout_seconds`, and `version_command`. Commands run from the source directory (or file's parent), without a shell.
- Nesting, dependency cycles, and layer boundaries require suitable extra checks. Record their versions/configuration with `version_command`; the runner cannot detect every environment change.
- Files over 2 MB are skipped; override `max_file_bytes` in the config when needed.
