## 2024-04-26 - [Optimize path containment check]
**Learning:** `os.path.commonpath` can be a significant bottleneck for path containment checks due to internal list allocations and path splitting.
**Action:** For performance-sensitive path containment checks, use `os.path.abspath` and `str.startswith()`. Ensure a trailing `os.sep` is appended to the absolute directory (and path) before comparison to prevent path traversal bugs (e.g., preventing `/app/database` from matching `/app/data`).
