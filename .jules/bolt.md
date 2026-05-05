## 2024-05-05 - Optimize path containment checks
**Learning:** `os.path.commonpath` is a significant bottleneck for performance-sensitive path containment checks due to internal list allocations and path splitting.
**Action:** Use `os.path.abspath` and `str.startswith()` instead, ensuring a trailing `os.sep` is conditionally appended to prevent path traversal bugs.
