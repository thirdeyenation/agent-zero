## 2025-05-14 - os.path.commonpath Performance Bottleneck
**Learning:** `os.path.commonpath` creates a significant bottleneck during frequent path containment checks due to internal list allocations and path splitting overhead.
**Action:** Use `abs_path == abs_dir or abs_path.startswith(abs_dir + ('' if abs_dir.endswith(os.sep) else os.sep))` instead of `os.path.commonpath` for measurable performance gains without sacrificing correctness.
