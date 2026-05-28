## 2025-03-01 - Path Traversal in API Files Get Endpoint
**Vulnerability:** Found a critical path traversal vulnerability in `api/api_files_get.py` where user-provided paths (like `../../../etc/passwd`) were directly used to read and return file contents without verifying if they were within the application's base directory.
**Learning:** `files.get_abs_path()` uses `os.path.join` which resolves `..` paths naturally. But `os.path.join` on its own doesn't restrict paths to a specific root directory. Thus, absolute path resolution does not inherently prevent path traversal.
**Prevention:** Always validate resolved paths using `helpers.files.is_in_base_dir()` before performing file reading or writing operations based on user input.
