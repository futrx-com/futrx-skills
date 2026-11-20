# Concurrency and transactions

Read when moving or restructuring asynchronous or concurrent code, locks, transactions, cancellation, or timeouts.

- Preserve ordering. Reordering awaited calls, running sequential work concurrently, or serializing concurrent work changes timing, failures, and load.
- Preserve when work starts. Creating a task, future, promise, or goroutine earlier or later changes which side effects happen before a failure or cancellation.
- Keep shared mutable state with the owner that synchronizes it. Move a lock with the state it guards and keep the critical section's scope unchanged.
- The service decides which changes succeed together; persistence implements the transaction. Do not widen, narrow, split, or merge transactions, and keep each external call on the same side of the transaction boundary.
- Pass the existing cancellation signal, timeout, or deadline to moved code instead of creating a new one.
- Preserve concurrency limits, backpressure, and how overlapping requests resolve, including which result wins.
- Do not move blocking work onto a thread, event loop, or async runtime that previously avoided it.
- Report races, deadlocks, and missing cancellation separately instead of fixing them during the refactor.

| | Go | Java | Rust | TypeScript | C# |
|---|---|---|---|---|---|
| Work starts | at `go` | when submitted to an executor | when polled or spawned | when the promise is created | when the async method is called |
| Run concurrently | goroutines, `errgroup` | executors, `CompletableFuture`, virtual threads | `tokio::spawn`, `join!`, threads | `Promise.all` | `Task.WhenAll` |
| Cancellation | `context.Context` | interrupts, `Future.cancel` | dropping the future, `CancellationToken` | `AbortSignal` | `CancellationToken` |
| Mutual exclusion | `sync.Mutex`, channels | `synchronized`, `Lock` | `Mutex`, `RwLock` | single thread, but state can change across `await` | `lock`, `SemaphoreSlim` |
