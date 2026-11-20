---
name: code-refactorer
description: "Refactor code snippet or codebase that already exists and works. Use for architecture reviews, separating responsibilities, and structural cleanup across software types. Improve its structure aggressively while preserving every observable behavior."
---

# Code Architecture

Follow the following steps for your end to end flow:

## 1. Understand the current design

1. Read the code in scope, its callers, and relevant tests.
2. Identify each part's job, its dependencies, and how it handles data, state, and side effects.
3. Record each structural problem in scope with `file:line`, the responsibility involved, and why it is a problem.
4. Inspect Git history - only if needed - to collect more evidence on the current design rationale.
5. Record current behavior, existing test failures, and the checks you'll use to verify behavior stays the same, under `{codebase main's directory}/.refactor/session_{timestamp}`. Run the [structural checks](references/structural-checks.md) before editing and save the baseline in that session.
6. If you discover a bug or missing feature, record it without folding the fix into the refactor, then report it.
7. If a correctness change is unavoidable, stop and make the behavior change an explicit, separately authorized task.


## 2. Choose the layers

1. After completing step 1, read [SOLID](references/foundations/solid.md), [Main layers](references/foundations/main-layers.md), and [Lean design](references/foundations/lean-design.md).
2. Use the findings from step 1 and the subset table in Main layers to choose the layers each part needs. Mixed software can use different subsets for different parts.
3. Read a matching reference in `references/software-types/` only when needed to resolve a remaining design question. Do not automatically open every linked file.
4. Apply SOLID and lean design to the chosen structure and briefly explain the layer choices.

## 3. Plan the refactor

1. Map each responsibility to its current and intended owner in the chosen layers, showing affected files and dependency direction.
2. Identify the relevant layer or SOLID principle and the smallest structural change that resolves each problem. Order changes into small steps with behavior checks.
3. Use the shared folder names from Main layers. Consult the matching software-type reference when needed, and include a small tree of affected files, folders, and moves in the plan.
4. Save the map and plan as `plan.md` in the same `.refactor/session_{timestamp}/` folder used in step 1.

## 4. Implement

1. Follow the session plan, one responsibility at a time. Preserve outputs, side effects, errors, ordering, and observable timing.
2. Before each change, read only the implementation references that apply below. Skip unrelated references.
3. Update callers and dependency setup, remove superseded code, and run focused behavior checks after each move.
4. Commit each coherent, verified change following [Commits](references/implementation/commits.md).

| When changing | Read |
|---|---|
| Names of variables, functions, types, or modules | [Naming](references/implementation/naming.md) |
| Data types, their methods, or contracts | [Modelling](references/implementation/modelling.md) |
| Responsibility ownership, dependencies, or resource lifecycle | [Ownership and boundaries](references/implementation/ownership-and-boundaries.md) |
| Files, packages, modules, namespaces, imports, or exports | [Module structure](references/implementation/module-structure.md) |
| Error handling, translation, retries, fallbacks, or failure logging | [Errors and failures](references/implementation/errors-and-failures.md) |
| Async or concurrent code, locks, transactions, cancellation, or timeouts | [Concurrency and transactions](references/implementation/concurrency-and-transactions.md) |
| Constants, catalogs, defaults, flags, or runtime settings | [Configuration](references/implementation/configuration.md) |
| Extractions, moves, renames, or contract migrations | [Safe moves](references/implementation/safe-moves.md) |

## 5. Review and report

1. Run all tests and fix any issue arises.
2. Rerun the [structural checks](references/structural-checks.md) against the same scope and session. Review the comparison and report unsupported or incomplete checks.
3. Report back what have you done in a concise way.
