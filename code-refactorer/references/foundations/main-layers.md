# The main layers

Layers separate code by its job. Use only the ones the software needs.

| Layer | Folder | Its job | Parts within the layer |
|---|---|---|---|
| **1. Presentation** | `presentation/` | Receive input and show or return results. | UI components; hooks or view models; API controllers; CLI commands; job handlers. |
| **2. Services** | `services/` | Hold business logic and carry out operations. | Business rules, calculations, algorithms, transformations, and workflows. |
| **3. State** | `stores/` | Hold changing data in memory and control updates. | Stores for shared state and caches. Local component state can stay with its component. |
| **4. Persistence** | `persistence/` | Read and write saved data. | Repositories, database queries, ORM mappings, storage schemas, migrations, file storage. |
| **5. Integrations** | `integrations/` | Communicate with outside systems. | API clients, network transport, provider and device adapters. |

Use these same folder names in every software type. The last column shows possible parts within each folder: a frontend may have components and hooks in `presentation/`, while a backend has controllers there.

Every software type can use `services/` for business logic and operations, and `stores/` for shared in-memory state. Services can be focused functions, modules, or classes. Keep pure calculations independent of state and I/O, within `services/`. Saved data belongs in `persistence/`.

A cart illustrates three different jobs: **state** holds the current cart, **services** calculate its total and run checkout, and **persistence** saves and loads it.

## How layers work together

A typical operation follows this flow. Services use whichever branches they need:

```text
Presentation -> Services
                  -> State
                  -> Persistence
                  -> Integrations
```

These arrows show calls. Services keep business logic independent of UI, database, and network implementations. A contract can be as simple as a function passed into a service.

- All database access goes through persistence. Storage structure belongs there; business rules belong in services.
- Give each piece of changing data an owner. Reuse an existing store or API cache instead of duplicating its data.
- Keep setup and cleanup with the code that creates and manages resources.

## Which subset does each kind of software need?

| Software | Typical subset |
|---|---|
| [Static page or simple UI](../software-types/static-page-or-simple-ui.md) | Presentation; state if needed. |
| [Interactive app](../software-types/interactive-app.md) | Presentation and state. Add services, persistence, or integrations as needed. |
| [CRUD backend](../software-types/crud-backend.md) | Presentation, services, persistence. |
| [Pure computational library](../software-types/pure-computational-library.md) | Services containing calculation functions; state if shared working data is needed. |
| [Background worker](../software-types/background-worker.md) | Presentation, services, and the layers its job needs. |
| [Data or media pipeline](../software-types/data-or-media-pipeline.md) | Services; presentation, persistence, state, or integrations as needed. |

Read a matching reference only when needed to resolve a remaining design question. Omit layers that have no work: a simple database lookup may need only a controller and persistence.

For mixed products, choose layers for each part separately. Give every required job a home, adding subdivisions where needed.

## Folder structure

- Use the five folder names above consistently. Services contain business logic, calculations, algorithms, and workflows; stores own shared state.
- Each software-type example shows the same available folders. Create only those with a responsibility to own. A service can be a plain function; add classes only when useful.
- Feature folders such as `orders/` may group the same five folders. Keep layer names fixed within each feature.
- Keep startup, dependency setup, and shutdown in the project's entry point. Preserve framework-required paths and public imports, and record how they map to the layers in the session plan.
- Adapt filenames and extensions to the language. Reorganize only code within the requested scope.
