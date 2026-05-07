## 2024-05-07 - Avoid os.path.commonpath for path containment checks
**Learning:** `os.path.commonpath` is a significant bottleneck for frequent path validation because it internally allocates lists and splits strings.
**Action:** For simple directory containment checks, use `abs_path == abs_dir or abs_path.startswith(abs_dir + ('' if abs_dir.endswith(os.sep) else os.sep))` instead, which is ~5x faster.
