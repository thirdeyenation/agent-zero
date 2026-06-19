## 2024-06-19 - Path Traversal Vulnerability in File Retrieval API
**Vulnerability:** The `ApiFilesGet` endpoint accepted unvalidated file paths and read file contents, allowing path traversal attacks (e.g., `../../../../etc/passwd`).
**Learning:** Any endpoint that accepts a file path from a request and reads its contents must rigorously validate that the fully resolved path remains within the intended base directory to prevent arbitrary file reading on the host.
**Prevention:** Always validate resolved absolute paths using `files.is_in_base_dir(external_path)` or `Path.resolve().is_relative_to(base_dir)` before performing file operations.
