# Data or media pipeline

Use this reference when data passes through several processing steps, such as an import or video export.

## Which layers to use

| Layer | Use it for |
|---|---|
| Presentation | A command, API, or job handler that starts processing and reports results. Omit it for a directly called function. |
| Services | Processing stages and their order: parsing, validation, transformations, calculations, and encoding. |
| State | Buffers, accumulated results, or progress held in memory. |
| Persistence | File or database input/output and saved progress. |
| Integrations | External data sources, destinations, or services used during processing. |

## Common subsets

- **Small in-memory transformation:** services only; ordinary function calls can connect its steps.
- **File import:** services and persistence; presentation if exposed as a command or API.
- **Live stream processor:** services, state, and integrations; persistence if results or progress must be saved.

## Suggested folder structure

```text
src/
  presentation/   # Commands, API controllers, or job handlers
  services/       # Processing stages, stage order, and cancellation
  stores/         # Shared buffers, working data, and in-memory progress
  persistence/    # File and database reads, writes, and saved progress
  integrations/   # External sources or destinations
```

Use `services/` for processing stages and their coordination, and `stores/` to own shared buffers or progress. Pure stages can be functions in `services/` that receive data and return results. A small transformation can stay in one file; omit unused folders.

## Example flow

```text
Import command -> import service

Read CSV file -> parse rows -> validate products -> save products
 persistence      services         services          persistence
```

The import service runs the stages in order and reports the outcome. Each stage has a clear input and output. File and database access stay in persistence; parsing and product rules stay in services.

Keep format conversion separate from storage or network access. A parser can accept text or bytes without opening a file itself. Use small contracts for any external operations a stage needs.

The import service decides whether invalid records stop the import or appear in a rejection report. It also controls cancellation, ordering, and how much work runs at once. For live streams, define what happens when input arrives faster than it can be processed.

Add saved progress only when restarting from the beginning is unsuitable. Close files and release other resources on completion, failure, or cancellation. If a worker starts the pipeline, return the outcome to that worker so it can finish the job.
