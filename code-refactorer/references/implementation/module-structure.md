# Module structure

Read when creating, moving, splitting, or merging files, packages, modules, or namespaces, or changing what they export.

- Reuse a valid existing layout. Otherwise use the layer folders from [Main layers](../foundations/main-layers.md) and group by business context inside each; a small codebase may stay flat.
- Avoid catch-all `utils`, `common`, `shared`, `helpers`, or `types` modules. A shared module needs one specific job and must not depend on feature code.
- Presentation calls services. Services own business logic and define contracts that persistence and integrations implement. Keep business rules independent of UI frameworks, storage, and transport implementations.
- Do not add import cycles. Break one by moving the shared piece to its owner, or by letting the inner module define a contract the outer module implements.
- Export only what other modules use. If a move forces a private name to become public, reconsider the move.
- Treat anything consumed outside the repository as a contract: package paths, exported names, namespaces, and entry points. When a move would break external callers, keep a deprecated alias or forwarding definition at the old location.
- Preserve initialization order and side effects when moving code that runs implicitly.
- Configuration placement follows [Configuration](configuration.md); model, behavior, and contract placement follows [Modelling](modelling.md).

| | Go | Java | Rust | TypeScript | C# |
|---|---|---|---|---|---|
| Layer and context path | `internal/services/<context>/` | `<base>.services.<context>` package | `src/services/<context>/` module | `src/services/<context>/` | `<Product>.Services.<Context>` namespace |
| Encapsulation unit | package (directory) | package; JPMS module | module; crate | file; package | assembly (project) |
| Keep private | lowercase name | package-private; unexported package | no `pub`; `pub(crate)` | no `export` | `internal`, `private` |
| Implicit initialization | package vars and `init()` at startup | static initializers on first use | none before `main`; `LazyLock` on first use | top-level code on first import | static constructors on first use; module initializers |
| Cycles | compile error between packages | allowed between packages; forbidden between modules | allowed within a crate; forbidden between crates | allowed, but can leave imports undefined at load | allowed within an assembly; forbidden between projects |
