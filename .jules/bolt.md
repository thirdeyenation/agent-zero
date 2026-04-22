## 2024-06-13 - Path Containment Optimization
**Learning:** `os.path.commonpath` can be a significant bottleneck for path containment checks due to internal list allocations and path splitting.
**Action:** Use `os.path.abspath` and `str.startswith()` instead, ensuring that a trailing `os.sep` is appended to the absolute directory before comparison to prevent path traversal bugs (e.g., preventing `/app/database` from matching `/app/data`).
