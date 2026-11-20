# Apply SOLID


Use the *real* definitions, not the folklore. SOLID is a diagnostic, **not** permission to add abstraction. If a principle makes the code larger without clarifying ownership or protecting behavior, choose the smaller design.


| Principle | How to apply it |
|---|---|
| **S — Single Responsibility** | Give a module one coherent job and reason to change. File size or method count alone does not decide this. "One reason to change" = **one actor/stakeholder** drives its changes, not "it does one thing." *Test:* would a request from a different role (DB admin vs. UI designer vs. domain expert) force edits to the same unit? *Fix:* split along those change-axes; separate policy, state, rendering, persistence, and I/O. |
| **O — Open/Closed** | Add extension points for real, supported variations. Avoid designing for hypothetical future needs. *Test:* does adding a variant require editing an existing `if/else`/`switch`? *Fix:* a registry/strategy map or polymorphic contract — when it reduces the total diff, not preemptively. |
| **L — Liskov Substitution** | A replacement must accept the promised inputs and preserve the contract's results, errors, and effects. Callers should not need special cases for it. |
| **I — Interface Segregation** | Give callers only the operations they need. Avoid interfaces that force unrelated methods on implementations. *Test:* do implementers stub methods, or callers use a slice of a fat interface? *Fix:* split into role-specific interfaces (reader vs. writer); split option bags carrying unrelated concepts.
 |
| **D — Dependency Inversion** | Services depend on small contracts for storage and external operations. Setup code supplies the concrete implementations. High-level policy depends on abstractions; details do too. *Test:* does a service `new` a concrete class or reach for a global singleton? *Fix:* depend on an interface, inject the concrete, wire concretes at one composition root.|

Use the language's natural tools: functions, modules, interfaces, protocols, or classes. Add an abstraction for a real boundary or supported variation. Avoid empty layers and wrappers that only forward calls.

**Guardrail:** an interface earns its place only with a real second implementation, a genuine test seam, or a true policy/detail boundary. Don't invert dependencies that will never vary. Prefer the smallest seam that removes the coupling.
