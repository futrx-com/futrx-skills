# Pure computational library

Use this reference for math, algorithms, parsers, and data transformations.

## Which layers to use

A pure computational library usually needs just **services** for its algorithms, calculations, and transformations. Its public functions are the entry point.

```text
Caller -> function in services/ -> result
```

For example, `polygonArea(points)` checks its inputs, runs the calculation, and returns the area. This single operation lives in `services/`. Reusable working data or caches can have an owner in `stores/`.

## Suggested folder structure

```text
src/
  presentation/   # CLI or API input/output, when exposed
  services/       # Algorithms, calculations, transformations, and their operations
  stores/         # Reusable working data or caches, when needed
  persistence/    # File or database access, when added
  integrations/   # External service or device access, when added
```

A small library can use a single file in `services/`. Services can be ordinary functions or modules; wrapper classes and I/O dependencies are unnecessary for pure calculations. Use `stores/` when shared state is needed, while keeping pure calculations independent of mutable state and I/O. Omit unused folders; public exports follow the language's package conventions.

## When to add another layer

| Layer | Add it when |
|---|---|
| Presentation | A CLI or API must translate input and format results. |
| State | A store owns reusable mutable state or a cache. Local variables alone do not need a store. |
| Persistence | It loads or saves files or database records. |
| Integrations | It calls an outside service or device. |

For example, an application can load points from a file and pass them to `polygonArea`. File access belongs in persistence; the calculation still accepts ordinary points and returns an area.

Keep algorithms independent of UI, storage, and network code. Ordinary helper functions can break down an algorithm without creating another layer.

Make the public function's promises clear: valid inputs, results, errors, and whether it changes the input data. Preserve numerical accuracy and other promised behavior when reorganizing the code. If the library keeps mutable state or allocates resources, make their owner and cleanup clear.
