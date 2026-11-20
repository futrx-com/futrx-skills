# Errors and failures

Read when moving, wrapping, translating, or handling errors, or changing retries, fallbacks, or failure logging.

- Treat failure behavior as output. Preserve error kinds, codes, messages, status codes, logged events, and which operations fail versus return partial results.
- Moving code into or out of a catch block, error check, or transaction changes which failures it handles. Re-check that boundary after each move.
- Translate each error once, in the adapter that sees its raw form: persistence maps storage errors, integrations map provider errors, presentation maps results to responses. Business code never handles SQL, HTTP, or SDK errors.
- Keep the original cause when wrapping. Do not make a specific error generic or a generic error specific.
- Do not add, remove, or broaden handlers, fallbacks, default values, or retries. Report swallowed errors and missing handling separately.
- The owner that knows whether an operation is safe to repeat decides retry policy; transport may implement the mechanics. Preserve retry count, backoff, and timeouts.
- Keep the language's error model and the split between recoverable errors and crashes. Converting between thrown errors, returned errors, and panics changes the contract.

| | Go | Java | Rust | TypeScript | C# |
|---|---|---|---|---|---|
| Recoverable errors | returned `error` | exceptions | `Result<T, E>` | thrown errors, rejected promises | exceptions |
| Wrap with cause | `fmt.Errorf("...: %w", err)` | `new X(msg, cause)` | `map_err`, `Error::source` | `new Error(msg, { cause })` | `new X(msg, inner)` |
| Match a kind | `errors.Is`, `errors.As` | `catch (X e)` | `match` on the error | `instanceof` or a tag field | `catch (X e) when (...)` |
| Crash | `panic` | `Error` subclasses | `panic!` | uncaught error | unhandled exception, `Environment.FailFast` |
