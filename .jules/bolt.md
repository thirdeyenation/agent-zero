## 2024-05-01 - Blocking the event loop in async API handlers
**Learning:** API endpoints inheriting from `helpers.api.ApiHandler` implement an `async def process` method that executes directly on the main asyncio event loop.
**Action:** Use asynchronous equivalents like `await asyncio.sleep()` instead of synchronous blocking operations like `time.sleep()` to prevent stalling the entire server.
