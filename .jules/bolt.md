## 2025-02-18 - Prevent event loop blocking in async API handlers
**Learning:** Using `time.sleep` inside `async def process()` methods of API handlers stalls the entire main event loop, significantly degrading overall application performance.
**Action:** Always use non-blocking `await asyncio.sleep()` equivalents in `async` endpoints inheriting from `ApiHandler`.
