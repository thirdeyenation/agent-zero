## 2024-05-24 - Path Traversal in API Files Get
**Vulnerability:** The API Files Get endpoint accessed user-supplied paths without validating if they belonged to the base directory.
**Learning:** Absolute paths provided by external inputs can bypass basic filtering.
**Prevention:** Always validate external paths using `files.is_in_base_dir()` before accessing them.
