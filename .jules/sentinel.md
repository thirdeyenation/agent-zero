## 2024-10-24 - Fix Path Traversal in ApiFilesGet
 **Vulnerability:** Path traversal in `api/api_files_get.py` allowed arbitrary file reading outside of the base directory via manipulated input paths (e.g. starting with `/a0/../../`).
 **Learning:** When converting internal virtual paths to physical paths on the file system, standard normalization handles `..` but can resolve to directories completely outside the expected application root.
 **Prevention:** Always use a base directory check function (like `files.is_in_base_dir()`) immediately before acting on any user-provided or user-manipulated file path to restrict access boundaries.
