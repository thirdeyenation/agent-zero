## 2024-10-25 - API Handlers blocking the event loop
**Learning:** API endpoint methods in `helpers.api.ApiHandler` subclasses (like `process()`) run directly on the main asyncio event loop. Using synchronous operations like `time.sleep()` within them blocks the loop and stalls all concurrent processing.
**Action:** Always verify if an API handler is `async def`. If so, strictly use non-blocking equivalents (e.g., `await asyncio.sleep()`) instead of synchronous delays.
