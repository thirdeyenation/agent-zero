## 2025-02-27 - Path Traversal via string startswith
**Vulnerability:** Path Traversal vulnerability where `str(target_file).startswith(str(base_dir))` was used to check if a resolved file path is within a base directory. This allowed accessing paths like `/app/workspace-malicious` if the base directory was `/app/workspace` because they share the same string prefix.
**Learning:** Checking path containment using string prefixes is inherently flawed and can be bypassed by sibling directories that share the same prefix name.
**Prevention:** Always use `is_relative_to()` on Pathlib objects or `os.path.commonpath()` to verify directory containment instead of string-based prefix checks.
