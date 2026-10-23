## 2024-05-18 - Replacing synchronous time.sleep in Async Handlers
**Learning:** API endpoints inheriting from `helpers.api.ApiHandler` implement an `async def process(...)` method that executes directly on the main asyncio event loop. Using synchronous `time.sleep()` within these blocks stalls the entire server.
**Action:** Always avoid using synchronous blocking operations (such as `time.sleep()`) within `async def process(...)` and replace them with asynchronous equivalents (e.g., `await asyncio.sleep()`) to prevent stalling the entire server.
