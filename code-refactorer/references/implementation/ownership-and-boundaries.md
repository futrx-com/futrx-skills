# Ownership and boundaries
Read when moving responsibilities, dependencies, state ownership, or resource lifecycle.

- **Is ownership obvious?** If not, move the code to the place with the clearest responsibility.
- **Does the structure explain the system?** Each piece should sit where its role is obvious, not where it first landed by convenience.
- **Can invalid states be represented?** If yes, tighten the types or split the state so the bad state can't be constructed.
- **Is the public surface necessary?** Keep contracts small and stable; don't widen an API just because a refactor made it convenient.
