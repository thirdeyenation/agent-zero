## 2024-05-06 - Optimize path containment check
**Learning:** `os.path.commonpath` is a significant bottleneck for path containment checks due to internal list allocations and path splitting.
**Action:** For performance-sensitive checks, use `os.path.abspath` and `str.startswith()`, ensuring that a trailing `os.sep` is conditionally appended to the absolute directory before comparison to prevent path traversal bugs.
