## 2024-05-18 - JSON Parse Performance Optimization
**Learning:** `json_parse_dirty` in `helpers/extract_tools.py` was directly relying on `DirtyJson.parse_string` which is significantly slower than the standard library's `json.loads` for well-formed JSON strings. This was a bottleneck as this method is used frequently to parse extracted JSON strings.
**Action:** When working with custom fallback parsers for data formats like JSON, always attempt parsing with the standard library's fast path first (e.g. `json.loads()`), falling back to the custom parser only upon a `JSONDecodeError`.
## 2024-05-18 - Asyncio Event Loop Blocking
**Learning:** `time.sleep` inside `async def` methods blocks the entire `asyncio` event loop. This prevents the server from processing other concurrent requests or tasks.
**Action:** When working inside an `async def` function, always use `await asyncio.sleep(...)` instead of `time.sleep(...)` to allow other tasks to run.
