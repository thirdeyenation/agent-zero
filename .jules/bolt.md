## 2024-10-19 - Do not block async APIs with synchronous sleeps
**Learning:** Using synchronous `time.sleep` in async API handlers (`helpers.api.ApiHandler.process`) blocks the entire asyncio event loop because the process runs directly on the loop.
**Action:** Replace `time.sleep()` with `await asyncio.sleep()` in async endpoints to allow concurrent operations.
