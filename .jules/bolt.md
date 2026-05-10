## 2024-05-10 - Fast path containment checks
**Learning:** `os.path.commonpath` can be a significant bottleneck due to internal list allocations and path splitting. Using string matching with `os.path.abspath` and `str.startswith()` is about 4x faster.
**Action:** Use `abs_path == abs_dir or abs_path.startswith(abs_dir + ('' if abs_dir.endswith(os.sep) else os.sep))` for path containment checks instead of `os.path.commonpath` to handle root directory edge cases quickly and safely.
