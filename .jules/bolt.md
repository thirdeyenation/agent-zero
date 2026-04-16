## 2024-05-24 - Avoid os.path.commonpath for path containment checks
**Learning:** `os.path.commonpath` can be a significant bottleneck in performance-sensitive path containment checks due to internal list allocations and path splitting overhead.
**Action:** Use `os.path.abspath` and `str.startswith()` instead, ensuring that a trailing `os.sep` is appended to the absolute directory (and checked) before comparison to prevent path traversal bugs (e.g., preventing `/app/database` from matching `/app/data`).
