## 2025-01-31 - [Async Event Loop Blocking]
**Learning:** Using synchronous `time.sleep()` inside `async` Python functions blocks the event loop, degrading concurrency and performance for all other asynchronous operations.
**Action:** Always replace `time.sleep()` with non-blocking `await asyncio.sleep()` in any `async def` functions.
