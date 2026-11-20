# CRUD backend

Use this reference for backends that create, read, update, or delete stored data through APIs or commands. Simpler request handlers can use a smaller subset.

## Which layers to use

| Layer | Use it for |
|---|---|
| Presentation | Routes, controllers, or commands that read input and return results. |
| Services | Operations, business rules, calculations, and allowed changes to business data. |
| State | In-memory data or caches, if the service needs them. |
| Persistence | Database access or file storage, including queries, mappings, storage schemas, and migrations. |
| Integrations | Calls to external APIs or other services. |

## Common subsets

- **Simple stored-data lookup:** presentation and persistence.
- **Calculation API:** presentation and services.
- **CRUD service with business rules:** presentation, services, and persistence.
- **Service that calls another API:** add integrations.

## Suggested folder structure

```text
src/
  presentation/   # Routes, controllers, and commands
  services/       # CRUD operations, business rules, and calculations
  stores/         # Shared in-memory state and caches
  persistence/    # Repositories, database access, and mappings
  integrations/   # External API clients
```

A simple lookup may use only `presentation/` and `persistence/`. Use `services/` for operations and business logic, and `stores/` for shared in-memory data. Keep saved data in `persistence/` and omit unused folders.

## Example flow

```text
Request -> order controller -> create-order service
                                -> order rules in services/
                                -> order repository -> database

Result <- order controller <- create-order service
```

The controller reads the request and formats the response. Services organize the operation, check permissions, validate the order, and calculate its total. The repository saves it.

Keep HTTP objects in controllers, SQL and ORM details in persistence, and provider SDKs in integrations. Services use small contracts for storage and external calls; application startup supplies their implementations.

The service decides which changes must succeed together. Persistence implements the database transaction. If an operation also calls an external service, define what happens when only part of it succeeds.

Translate database and provider errors into results the service understands. The controller turns those results into responses. The code that opens connections owns closing them.
