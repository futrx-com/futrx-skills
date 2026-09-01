# Frontend refactoring reference

Read this reference completely for browser or client UI, component, view-state, frontend service, store, context, API, or client-transport refactors. Preserve the framework and repository's valid idioms; adapt the names below while keeping state, business logic, effects, presentation, and boundary ownership explicit.

In this reference, **hook** names the presentation-adapter role. In React and Preact, implement it as a custom hook. In another frontend framework, use its established equivalent—such as a composable, facade, controller, presenter, binding, or view model—and name the folder accordingly. Preserve the boundary; do not impose React terminology on another framework.

## Target ownership

Organize frontend code so a maintainer can tell presentation, presentation adapters, business workflows, client state, server communication, and protocol mechanics apart. Layer folders, feature folders, or a hybrid can all work. Within a feature, keep the same responsibility seams visible rather than turning the feature directory into one vertical god module.

Each unit should answer one primary question:

- **`ui/` — presentation.** Render inputs and emit user intent. Presentational components receive data and callbacks as props or their platform equivalent. Screen/container components may call hooks, but no UI component imports a store, context, or service directly. UI owns only ephemeral interaction details that do not need wider coordination.
- **`hooks/` — presentation adapters.** This is the only UI-facing gateway to services and shared state. A hook obtains dependencies from context, subscribes to narrow store selectors, exposes render-ready data, and translates user intent into a service call. It may bind framework lifecycle and reactivity, but it must not own business rules, call raw API/transport code, duplicate store state, or become a general utility layer.
- **`services/` — frontend business logic.** Like backend services, own application decisions and workflows: validate an intent, coordinate API operations, apply domain rules, and update state through narrow store contracts. Keep services framework-agnostic: no components, hooks, contexts, DOM, or framework lifecycle APIs. A service must not expose raw transport or server DTO details to its hook.
- **`state/stores/` — reactive client data.** Own the current client-side source of truth, selectors, and invariant-preserving state mutations. Treat stores as the frontend data layer, not the business layer: they do not call APIs or services and do not decide multi-step workflows. Avoid generic setters that let callers create invalid states.
- **`state/context/` — scoped access and injection.** Provide already-constructed stores and services to the relevant UI subtree and prevent prop drilling. Context owns scoping and access, not business logic or a second copy of state. UI code does not consume raw context; hooks or the framework-equivalent adapter do. Providers are assembled at the app composition boundary.
- **`api/` — server-facing application calls.** Expose domain-meaningful operations, select endpoints, validate/map request and response DTOs, and translate server errors into frontend-facing results. Do not own rendering or transport mechanics.
- **`transport/` — client wire mechanics.** Own generic HTTP, WebSocket, RPC, serialization, request cancellation, reconnect, and protocol-level authentication behavior. It must not know screen or business meaning.
- **`model/` — frontend-owned data definitions.** Organize domain, application, API, and persistence models by context as defined in [modeling.md](modeling.md).
- **`port/` — behavioral contracts.** Define narrow service dependencies, including API and store capabilities, as described in [modeling.md](modeling.md).
- **`app/` — composition.** Construct transports, APIs, services, and stores; inject narrow dependencies; assemble routes and context providers; and connect them to screens. Keep construction out of hooks, services, stores, and components.
- **`config/` — public constants and runtime settings.** Centralize constants, catalogs, defaults, flags, and validated public environment values as defined in [configuration.md](configuration.md). Construction remains in `app/`.
- **`shared/` — dependency-light frontend utilities.** Hold genuinely reusable pure helpers and primitives. It must not become a dumping ground for feature state, API calls, or components with hidden application dependencies.

Skip folders with no current responsibility. Small frontends may colocate these roles; ownership and dependency direction matter more than directory count.

## Dependency and data flow

The interaction flow is normally:

```text
read:   store -> hook/presentation adapter -> UI
intent: UI -> hook/presentation adapter -> service -> API -> transport -> server
                                           service -> store contract -> store
wiring: app composition -> transport + API + services + stores -> context/provider
```

Treat this as responsibility flow, not an absolute import DAG. API code may import shared contract types, and concrete stores may implement service-owned state ports. What must remain true:

- UI reaches a service, store, or context only through a hook or the framework's equivalent presentation adapter.
- Hooks expose narrow, view-specific data and intent operations; they do not absorb business logic or become another store.
- Services own frontend business workflows and may coordinate APIs with stores through narrow injected contracts; they never import hooks or UI.
- Stores own state and mutations but do not call services, APIs, or transport.
- Context scopes constructed dependencies but does not become a global service locator or state dumping ground.
- API modules expose meaningful operations rather than generic `request()` calls to components.
- Transport remains protocol-generic and free of domain or screen decisions.
- One semantic owner controls each state transition and invariant.

Avoid a cycle between services and stores. Prefer a consumer-owned store port passed into the service at composition time, or another narrow one-way contract already established by the repository. Do not let a service import a concrete store while that store imports the service.

## Placement questions

- Does it render data or emit raw user intent? Put it in UI.
- Does it adapt stores/services to framework rendering, lifecycle, or reactivity? Put it in a hook or equivalent presentation adapter.
- Does it apply a business rule or coordinate a workflow across API and state? Put it in a frontend service.
- Does it own reactive data, selectors, or invariant-preserving mutations? Put it in `state/stores/`.
- Does it scope and inject stores/services for a subtree to avoid prop drilling? Put it in `state/context/`; expose access through hooks.
- Does it name a backend operation or map a request/response? Put it in API.
- Is it protocol, cancellation, serialization, reconnect, or authentication mechanics? Put it in transport.
- Does it construct dependencies or assemble providers, routes, state owners, and screens? Put it at the app/composition boundary.
- Is it a data definition or behavioral contract? Classify it using [modeling.md](modeling.md).
- Is the state private to one component's interaction and irrelevant elsewhere? Keep it local instead of promoting it to a global store.
- Is it pure and reused across unrelated features? Put it in shared only when no feature or semantic owner is clearer.

If one component or hook answers several of these questions, split it along presentation-adapter, service, store, mapping, and transport boundaries.

## Example structure

```text
frontend/
  config/
  model/
  port/
  transport/
  api/
  services/
  state/
    stores/
    context/
  hooks/             # React/Preact name; rename to the framework's equivalent adapter role
  app/
  ui/
  shared/
```

Feature-oriented repositories may repeat these roles inside each feature. A recursive listing should still reveal where presentation, state, server calls, and transport live.

## Frontend-specific pressure tests

- Split a component because it has different owners or reasons to change, not because it crossed an arbitrary line count.
- Enforce the UI boundary in both directions: components do not import stores, contexts, or services; stores and services do not import components or hooks.
- Keep hooks thin. A hook selects state, binds lifecycle/reactivity, and delegates intent to a service; business branching belongs in the service and durable/shared state belongs in the store.
- Give each store a cohesive state responsibility and expose narrow selectors plus intent-level mutation methods. Do not create one application-wide mega-store or mirror the same source of truth across contexts and stores.
- Use context for dependency scope and prop-drilling relief. Do not put unrelated mutable values and operations into one global provider merely because they are widely accessible.
- Keep services independently usable and testable without mounting UI. Inject API and store contracts instead of importing framework globals or constructing concrete dependencies inside the service.
- Keep derived data derived. Do not mirror props, API cache data, or selectors into another mutable source of truth without a lifecycle reason.
- Keep each invariant under one state owner. Stores may expose intent-level operations; avoid raw setters that let callers construct invalid combinations.
- Separate effect creation from updates. Do not tear down and recreate sockets, observers, controllers, or expensive objects whenever ordinary data changes.
- Pair every subscription, listener, timer, observer, request, or socket with cancellation or disposal owned by the same lifecycle.
- Keep hooks and state modules framework-idiomatic and cohesive. Extract pure transforms when they are truly stateless; use a store, reducer, or object when shared state and transitions need one owner.
- Preserve component identity, key behavior, focus, selection, scroll, event propagation, and accessibility semantics during extraction.
- Keep loading, empty, success, stale, and failure states explicit. A refactor must not collapse distinct states or change which one renders first.
- Avoid UI wrappers that only rename props or forward every argument. A wrapper earns its place by enforcing a presentation boundary, composition policy, or reusable interaction.

## Frontend verification

In addition to the shared checks in `SKILL.md`, verify the relevant existing behavior around:

- rendered content, DOM semantics, accessibility attributes, focus, selection, and keyboard/pointer behavior;
- loading/error/empty transitions, optimistic updates, cache invalidation, and async ordering;
- effect setup/cleanup counts, request cancellation, socket reconnects, and absence of duplicate subscriptions;
- UI import boundaries and the hook-only access path to services, stores, and context;
- service workflows, store mutations/selectors, and context/provider scope without mounting presentation when existing tests allow it;
- API request shape, response mapping, and user-visible error text;
- component identity, memoization-sensitive behavior, route/provider composition, and build output.
