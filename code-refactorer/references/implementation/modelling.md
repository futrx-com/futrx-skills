# Modelling

Read when creating or moving data types, the behavior attached to them, or contracts.

Place them inside the layer folders from [Main layers](../foundations/main-layers.md), grouped by business context:

```text
src/
  presentation/<context>/   # Controllers, handlers, components
    dto/                    # Request and response shapes, with their mappers
  services/<context>/       # Business logic and operations
    model/                  # Entities, values, enums, events, commands, queries, results, read models
    rules/                  # Rules and calculations that span several models
    port/                   # Contracts the services call: repositories, clients, clock
  stores/<context>/         # Stores and the state shapes they own
  persistence/<context>/    # Repository implementations
    record/                 # Rows, documents, ORM entities, with their mappers
  integrations/<context>/   # Client implementations
    dto/                    # Provider shapes, with their mappers
```

- Put behavior that uses only one type's data in the same file as the type. Rules across models go in `services/<context>/rules/`; services coordinate I/O through their dependency contracts.
- A contract lives in the `port/` of its caller; its implementation lives in `persistence/` or `integrations/`.
- Services never import `dto/` or `record/` types. Mappers sit beside the outer shape they convert.
- Create `dto/` or `record/` only when the shape differs from the model. Omit empty folders.
- Moving a type must not change its serialized shape.

| | Go | Java | Rust | TypeScript | C# |
|---|---|---|---|---|---|
| Data | `struct` | `record`, class | `struct`, `enum` | `type`, `interface`, `class` | `record`, `class`, `struct` |
| Behavior in the same file | receiver methods | class methods | `impl` block | class methods or functions | class methods |
| Contract in `port/` | `interface` | `interface` | `trait` | `interface` | `interface` |
