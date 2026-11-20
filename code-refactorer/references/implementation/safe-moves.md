# Safe moves

Read before extracting, moving, renaming, or migrating code and contracts.

- Inspect Git status and preserve unrelated user changes. Work within the session plan's scope.
- **Extract:** move the responsibility to its new owner, temporarily delegate from the old location, verify, migrate callers, then remove the old implementation.
- **Change a contract:** introduce the new shape internally, migrate callers in small steps, and remove the old shape when unused. Preserve public compatibility.
- **Introduce a dependency contract:** derive the smallest contract from actual caller usage, make the concrete dependency satisfy it, and supply it where the application is assembled.
- **Replace conditional dispatch:** reproduce existing branches behind the replacement, move one branch at a time, and remove the conditional when all branches have moved.
- **Move or rename:** use language-aware tools when available. Update imports, exports, callers, dependency setup, and dynamic references; compiler errors do not reveal every runtime reference.
- Check behavior after each meaningful move. If it changes, correct the move before continuing.
- Remove temporary adapters, obsolete implementations, and unused exports once callers have migrated. Finish by resolving the identified structural problem.
