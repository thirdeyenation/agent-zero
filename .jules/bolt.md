## 2024-05-18 - Avoid synchronous time.sleep in async API handlers
**Learning:** `async def process` methods in `helpers.api.ApiHandler` execute on the main asyncio event loop. Calling synchronous functions like `time.sleep` blocks the entire loop, halting other concurrent operations and decreasing throughput.
**Action:** Always use asynchronous alternatives (e.g. `await asyncio.sleep`) inside `async def` API endpoint implementations.
