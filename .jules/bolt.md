## 2024-04-18 - Optimize Path Containment Checks
**Learning:** `os.path.commonpath` is a significant bottleneck for performance-sensitive path containment checks due to internal list allocations and path splitting.
**Action:** Use `os.path.abspath` and `str.startswith()`, ensuring that a trailing `os.sep` is appended to the absolute directory (and path, if needed) before comparison to prevent path traversal bugs (e.g., preventing `/app/database` from matching `/app/database-backup`).
