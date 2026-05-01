## 2024-05-14 - Optimize Path Containment Checks
**Learning:** `os.path.commonpath` can be a significant performance bottleneck due to internal list allocations and path splitting.
**Action:** Avoid `os.path.commonpath` for performance-sensitive path containment checks. Instead, use `os.path.abspath` and `str.startswith()`, ensuring that a trailing `os.sep` is conditionally appended to the absolute directory before comparison to prevent path traversal bugs.
