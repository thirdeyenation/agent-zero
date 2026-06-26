## 2026-06-26 - Prevent Path Traversal via string prefixes
**Vulnerability:** The FileBrowser component was using `str(path).startswith(str(base_dir))` to validate if user-provided paths were contained within the base directory. This allowed path traversal to sister directories that share the same prefix (e.g., `/workspace_backup` via base `/workspace`).
**Learning:** Checking for valid directory containment by doing string prefix comparisons is insecure as it matches unintended sibling paths.
**Prevention:** Always use the built-in `Path.is_relative_to(base_dir)` method to perform structural path validation rather than simple string prefix checking.
