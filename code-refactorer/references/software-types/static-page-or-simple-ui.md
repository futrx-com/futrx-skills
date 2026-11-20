# Static page or simple UI

Use this reference for static pages and small interactions such as menus or counters.

## Which layers to use

- **Static page:** presentation only. Components or templates show the content.
- **Menu or counter:** presentation and state. Keep temporary interaction state with the component that owns it.

```text
User input -> component -> local state -> updated UI
```

Use services for business rules, calculations, and coordinated operations, and stores for shared UI state. Ordinary display logic and temporary interaction state can stay in the component.

## Suggested folder structure

```text
src/
  presentation/   # Pages, components, and local interaction state
  services/       # Business rules, calculations, and coordinated actions, when needed
  stores/         # Shared UI state, when needed
  persistence/    # Saved preferences or drafts, when needed
  integrations/   # API or device calls, when needed
```

A static page may use only `presentation/`. Add other folders as their responsibilities appear, keeping these names. Images and styles follow the framework's asset conventions.

When the UI also needs calculations, shared data, persistence, or outside services, choose the additional layers from Main layers. Read the [Interactive app](interactive-app.md) reference only when more guidance is needed.
