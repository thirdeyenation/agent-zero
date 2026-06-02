## 2024-05-30 - Path Traversal via str.startswith

**Vulnerability:** Path traversal in `helpers.file_browser` where paths were validated using `str(full_path).startswith(str(self.base_dir))`.
**Learning:** Checking path containment with string operations is insecure because `/app-secrets/secret.txt` starts with `/app`, but `/app-secrets` is not inside `/app`.
**Prevention:** Always validate path containment using `is_relative_to()` on `pathlib.Path` objects, or rely on `helpers.files.is_in_base_dir()`.
