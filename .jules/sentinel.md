## 2024-07-04 - Fix Path Traversal in API Files Get
**Vulnerability:** Path traversal vulnerability in `api_files_get` where users could request paths outside the base directory using `../` sequences or absolute paths.
**Learning:** Incomplete validation when converting internal to external paths left arbitrary file read open.
**Prevention:** Always validate that user-provided file paths are contained within the intended base directory using `files.is_in_base_dir` after absolute resolution.
