## 2024-05-24 - Async API Handler Optimization
**Learning:** `api/mcp_servers_apply.py` uses synchronous `time.sleep(1)` inside an `async def process` method, which blocks the event loop.
**Action:** Replace `time.sleep()` with non-blocking `await asyncio.sleep()` in asynchronous handlers to ensure high concurrency.
