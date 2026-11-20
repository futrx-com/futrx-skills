# Interactive app

Use this reference for interactive apps that combine user input with calculations, shared data, or external operations.

## Which layers to use

| Layer | Use it for |
|---|---|
| Presentation | Components that render the UI; hooks, presenters, or view models that connect it to data and actions. |
| Services | Operations such as checkout, including rules and calculations independent of the UI framework. |
| State | Local interaction state, shared stores, and cached API data. |
| Persistence | Data saved locally, such as drafts in a file or browser database. |
| Integrations | Calls to backend APIs, external services, or device features. |

## Common subsets

- **Calculator:** presentation, state for the inputs, and services.
- **API data viewer:** presentation, an API cache for state, and an integration client.
- **Shopping app:** presentation, services, state, and integrations. Add local persistence if it saves local data.

## Suggested folder structure

```text
src/
  presentation/   # Components, hooks, and view models
  services/       # Checkout, pricing rules, calculations, and other operations
  stores/         # Shared cart state and API caches
  persistence/    # Locally saved drafts or preferences
  integrations/   # Backend and device clients
```

Keep temporary UI state with its component. Use `services/` for operations and business logic, `stores/` for shared state, and `persistence/` for locally saved data. Omit unused folders.

## Example flow

```text
Checkout UI -> checkout hook -> checkout service
                                 -> pricing rules in services/
                                 -> cart store
                                 -> order API client

Cart store / API cache -> hook -> UI
```

The component renders and handles UI events. The hook connects it to state and actions. Services organize checkout and calculate totals; the store owns cart data; the API client handles requests and responses.

Keep simple display logic and temporary UI state with the component. Use a hook or the framework's equivalent when connecting shared data and services. A simple API read can connect the query cache to the API client without a forwarding service.

Reuse the API cache instead of copying its data into another store. The backend remains responsible for server-owned data and decisions. A frontend API call belongs to integrations; the backend's database code belongs to backend persistence.

The code that starts a subscription or request owns its cleanup. Expose loading, errors, and results to the UI, and prevent an old response from replacing newer data when requests overlap.
