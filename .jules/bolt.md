## 2024-05-18 - JSON Parse Performance Optimization
**Learning:** `json_parse_dirty` in `helpers/extract_tools.py` was directly relying on `DirtyJson.parse_string` which is significantly slower than the standard library's `json.loads` for well-formed JSON strings. This was a bottleneck as this method is used frequently to parse extracted JSON strings.
**Action:** When working with custom fallback parsers for data formats like JSON, always attempt parsing with the standard library's fast path first (e.g. `json.loads()`), falling back to the custom parser only upon a `JSONDecodeError`.
## 2024-05-20 - O(N) linear search bottleneck in provider caching
**Learning:** `ProviderManager.get_provider_config` iterated over all loaded providers via list search resulting in an O(N) penalty for every provider config lookup. This is a common pitfall where configuration objects are cached in a list format suited for UI options, but not optimized for frequent ID-based lookups.
**Action:** When caching collections meant to be queried frequently by a unique identifier, always construct and store an auxiliary hash map (`dict`) keyed by that identifier to enable O(1) lookups.
