# Commits

- Make one coherent, behavior-preserving change per commit. Keep coupled contract and caller changes together.
- Run relevant checks before committing; keep each commit buildable.
- Inspect Git status, stage only task-owned paths or hunks, and review the exact commit diff. Preserve unrelated staged and unstaged work.
- Follow repository message conventions. Otherwise, use the format below with a short, imperative subject describing the structural change.
- Honor hooks. Report commit blockers without bypassing checks or changing Git configuration. Push or rewrite history only when separately authorized.
- Report commit hashes and any work left uncommitted.

```text
refactor(<scope>): <structural change>

Why: <reason for the change>
Checks: <checks run and results>
```

Example subject: `refactor(cart): extract pricing rules`.
