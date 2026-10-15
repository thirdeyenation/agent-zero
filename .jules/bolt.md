## 2025-02-12 - Replacing synchronous time.sleep with asyncio.sleep
**Learning:** Using `time.sleep` in an async function (`async def`) blocks the main event loop for the duration of the sleep, delaying all other pending async operations.
**Action:** Replace `time.sleep` with `await asyncio.sleep` inside `async def` methods across the backend when a delay is needed.
