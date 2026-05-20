## 2025-02-28 - Path Traversal Vulnerability in file path validation
**Vulnerability:** Path traversal logic bypass when using string `startswith` on absolute paths without checking for `os.sep` or correctly checking path containment.
**Learning:** `str(full_path).startswith(str(base_dir))` can be bypassed if `full_path` is a sibling directory sharing the same prefix (e.g., `/tmp/app_log` shares the prefix `/tmp/app`). `os.path.commonpath` or appending `os.sep` to `base_dir` must be used to ensure correct path containment checks.
**Prevention:** Always use secure path containment checks. In Python, either check `os.path.abspath(path) == os.path.abspath(base_dir)` or ensure the absolute path starts with `os.path.abspath(base_dir) + os.sep`.
