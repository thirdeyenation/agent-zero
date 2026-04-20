## 2024-05-18 - Optimized is_in_dir path containment check
**Learning:** `os.path.commonpath` can be a significant bottleneck due to internal list allocations and path splitting.
**Action:** Use `os.path.abspath` and `str.startswith()`, ensuring that a trailing `os.sep` is appended to the absolute directory before comparison to prevent path traversal bugs.
