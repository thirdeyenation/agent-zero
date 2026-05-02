## 2025-01-20 - Optimize path containment check
**Learning:** `os.path.commonpath` is a significant bottleneck for performance-sensitive path containment checks due to internal list allocations and path splitting.
**Action:** Use `os.path.abspath` and `str.startswith()` instead, ensuring that a trailing `os.sep` is conditionally appended to the absolute directory before comparison to prevent path traversal bugs.
