## 2025-06-28 - [Path Traversal in API Files Get Endpoint]
**Vulnerability:** Path traversal vulnerability in API endpoint `api/api_files_get.py`. The `paths` array allowed retrieving files outside of the intended directories when path traversal elements (e.g. `../../../`) are provided in the path or filename.
**Learning:** `files.get_abs_path()` and `os.path.basename()` alone do not resolve paths safely against path traversal if malicious components bypass `basename()` or traverse out after `get_abs_path` resolves. A strict boundary check must be explicitly made.
**Prevention:** Always validate that the final resolved absolute path is within the intended base directory using `files.is_in_base_dir(external_path)`.
