## 2024-06-25 - Path Containment Check Bottleneck
**Learning:** `os.path.commonpath` is slow for frequent path containment checks due to internal list allocations and path splitting.
**Action:** Use `os.path.abspath` combined with `str.startswith()` for a ~3x performance gain. Always ensure a trailing `os.sep` is appended to the absolute directory (and path) before the `startswith` comparison to prevent path traversal bugs (e.g., preventing `/app/database` from matching `/app/data`).
