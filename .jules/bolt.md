## 2024-05-03 - Avoid os.path.commonpath for path containment checks
**Learning:** `os.path.commonpath` can be a significant bottleneck due to internal list allocations and path splitting.
**Action:** Use `os.path.abspath` and `str.startswith()` instead, ensuring that a trailing `os.sep` is conditionally appended to the absolute directory before comparison to prevent path traversal bugs (e.g., `abs_path == abs_dir or abs_path.startswith(abs_dir + ('' if abs_dir.endswith(os.sep) else os.sep))`).
