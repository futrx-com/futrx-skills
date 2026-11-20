# Background worker

Use this reference for jobs, scheduled programs, and event handlers.

## Which layers to use

| Layer | Use it for |
|---|---|
| Presentation | A job or event handler that reads input and reports the outcome to the job system. |
| Services | The job's steps, workflows, rules, calculations, and transformations. |
| State | Progress or working data held in memory. |
| Persistence | Saved results, job progress, or records used to detect repeated jobs. |
| Integrations | Calls to providers, queues, or devices. |

## Common subsets

- **Scheduled calculation:** services, with a small entry point to start it.
- **Job that updates stored data:** presentation, services, and persistence.
- **Job that calls a provider:** add integrations.
- **Job that must resume after a restart:** add saved progress in persistence.

## Suggested folder structure

```text
src/
  presentation/   # Job and event handlers
  services/       # Job steps, workflows, rules, rendering, and transformations
  stores/         # In-memory progress and shared working data
  persistence/    # Output files and saved job progress
  integrations/   # Queue clients and provider clients
```

Use `services/` for job coordination and business logic, and `stores/` for shared working state. Persist restartable progress in `persistence/`. Omit unused folders; a pipeline started by the worker uses the same layer names.

## Example flow

```text
Job -> export handler -> export service
                           -> rendering functions in services/
                           -> file persistence
                           -> job record persistence

Outcome -> export handler -> job system
```

The handler understands the job system. Services organize the export steps and produce the output; persistence saves the file and completion record.

Keep queue and scheduler details out of services. The export service decides what successful completion means. The handler reports success or failure to the job system.

If a job can arrive twice, define how repeating it avoids unintended duplicate effects. Decide which failures can be retried and what progress must survive a crash. The worker startup code owns concurrency limits and shutdown.

For an export with several processing stages, also use the [Data or media pipeline](data-or-media-pipeline.md) reference when needed. The worker owns the overall job outcome; the pipeline organizes its processing stages.
