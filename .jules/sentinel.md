## 2024-04-03 - [Path Traversal in `get_file_info`]
 **Vulnerability:** Unauthenticated/arbitrary file reads via path traversal in endpoints relying on `helpers.files.get_abs_path`.
 **Learning:** The `get_abs_path` function returns the absolute path untouched if the input is already absolute, meaning inputs like `/etc/passwd` successfully bypass validation if not explicitly checked against a base directory.
 **Prevention:** Always enforce path bounds checking using `helpers.files.is_in_base_dir()` after resolving absolute paths from user input.
