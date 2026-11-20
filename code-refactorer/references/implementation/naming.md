# Naming
A name is the cheapest documentation in the codebase. A name that lies or blurs intent is a defect — fixing it *is* the refactor, and beats a clarifying comment.

- **Does the name state intent, not mechanics or type?** `activeUsers`, not `filteredArray`; `retryWithBackoff`, not `doLoop`. Never encode the type (`userList`, `strName`).
- **Is length proportional to scope?** A loop index can be `i`; a widely-imported export must be fully descriptive.
- **Functions read as verbs, values as nouns?** `parseDate`, `loadUsers` vs. `itemCount`, `requestConfig`. A pure transform can be named for its result (`sortedByDate`).
- **Booleans are positive predicates?** `isEnabled`, `hasErrors`, `canRetry` — not `flag`/`status` or double negatives like `isNotReady`.
- **Honest about cost and effect?** A `get`/`compute` that hits the network or mutates is lying. Reserve `get` for cheap accessors; use `fetch`/`load`/`query` for I/O; make side effects audible (`commit`, `flush`, `invalidate`).
- **One term per concept, everywhere?** Don't mix `fetch`/`get`/`load` for one operation or `user`/`account`/`member` for one entity. Use the domain's word consistently.
- **Opposites symmetric?** `open`/`close`, `add`/`remove`, `start`/`stop` — never `open`/`dismiss`.
- **Stripped the noise words?** `Manager`, `Helper`, `Util`, `Data`, `Processor`, `handle`, `do`, `-Impl` usually mark a missing concept. Name the actual role.
- **Context redundant or missing?** Inside `class User`, the field is `name`, not `userName`. But a bare `timeout` at a boundary carries its unit: `timeoutMs`, `sizeBytes`.
