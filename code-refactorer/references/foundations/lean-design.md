# Lean design

- Always pick the shortest path, and the leanest way for any implementation.
- Reuse or extend an existing valid pattern when it makes the whole system smaller and clearer.
- Add a layer, interface, strategy, registry, flag, or hook only for an identified boundary or supported variation.
- Remove wrappers that only forward calls and provide no meaningful boundary.
- Repeated syntax alone does not require an abstraction. Repeated business decisions, lifecycle management, or branching may need one clear owner.
- Keep pure, stateless calculations simple. Follow the language and framework's conventions rather than forcing classes or functions everywhere.
- Remove dead code, obsolete comments, unused parameters, and temporary delegation left by the refactor, within the requested scope.
- Keep public APIs small. Do not expose more operations merely to make a move convenient.
- Use the [structural checks](../structural-checks.md) to identify excessive branching and large functions, then inspect their responsibilities. Compare before and after with the same tools and settings. Do not split code merely to lower a score; metrics do not prove good design or unchanged behavior.
