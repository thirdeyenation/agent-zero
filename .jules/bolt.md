## 2024-04-11 - DirtyJson Fast Path
**Learning:** `DirtyJson` parser operates character-by-character and is very slow compared to the standard library `json.loads` (roughly 10x slower on typical JSON strings).
**Action:** When creating custom fault-tolerant parsers or wrappers like `DirtyJson`, always include a fast path that attempts to use the highly optimized native `json` module first. Fall back to the slower custom parsing only on failure.
