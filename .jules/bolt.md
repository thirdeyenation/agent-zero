## 2024-05-24 - Async API Handler Optimization
**Learning:** `api/mcp_servers_apply.py` uses synchronous `time.sleep(1)` inside an `async def process` method, which blocks the event loop.
**Action:** Replace `time.sleep()` with non-blocking `await asyncio.sleep()` in asynchronous handlers to ensure high concurrency.
## 2023-10-27 - Early returns on template substitution
**Learning:** Found that `replace_placeholders_text` and `replace_placeholders_json` do expensive string manipulations even when no placeholders exist in the text. Checking `if "{{" not in _content:` provides an extremely fast fast-path early return.
**Action:** Always add early-exit checks for common trigger substrings (like `{{` for templates) before iterating over large variable dictionaries to perform string replacement.
