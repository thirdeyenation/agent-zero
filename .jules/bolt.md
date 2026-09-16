## 2024-05-18 - JSON Parse Performance Optimization
**Learning:** `json_parse_dirty` in `helpers/extract_tools.py` was directly relying on `DirtyJson.parse_string` which is significantly slower than the standard library's `json.loads` for well-formed JSON strings. This was a bottleneck as this method is used frequently to parse extracted JSON strings.
**Action:** When working with custom fallback parsers for data formats like JSON, always attempt parsing with the standard library's fast path first (e.g. `json.loads()`), falling back to the custom parser only upon a `JSONDecodeError`.
## 2024-05-24 - Async API Handler Optimization
**Learning:** `api/mcp_servers_apply.py` uses synchronous `time.sleep(1)` inside an `async def process` method, which blocks the event loop.
**Action:** Replace `time.sleep()` with non-blocking `await asyncio.sleep()` in asynchronous handlers to ensure high concurrency.
## 2023-10-27 - Early returns on template substitution
**Learning:** Found that `replace_placeholders_text` and `replace_placeholders_json` do expensive string manipulations even when no placeholders exist in the text. Checking `if "{{" not in _content:` provides an extremely fast fast-path early return.
**Action:** Always add early-exit checks for common trigger substrings (like `{{` for templates) before iterating over large variable dictionaries to perform string replacement.
