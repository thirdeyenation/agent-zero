
## 2024-05-24 - Optimize path containment checks
**Learning:** `os.path.commonpath` is a significant bottleneck for frequent path containment checks due to internal list allocations and path splitting overhead.
**Action:** Use `os.path.abspath` and `str.startswith()` instead, conditionally appending a trailing `os.sep` to the absolute directory before comparison to prevent path traversal bugs (e.g., `abs_path == abs_dir or abs_path.startswith(abs_dir + ('' if abs_dir.endswith(os.sep) else os.sep))`).
