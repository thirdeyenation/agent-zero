## 2024-05-24 - simpleeval Sandbox Escape (CVE-2026-32640)
**Vulnerability:** The `simpleeval` package used in the project allowed arbitrary function execution resulting in potential sandbox escapes or remote code injection during the evaluation of user inputs and template conditions.
**Learning:** Using `simple_eval()` without explicitly disabling `functions` allowed unintended function executions.
**Prevention:** Update `simpleeval` dependency to version >=1.0.5 and always use `SimpleEval(names=..., functions={}).eval(...)` to prevent code execution when only evaluating variables.
## 2024-05-24 - Path Traversal Vulnerability in API File Retrieval
**Vulnerability:** In `api/api_files_get.py`, user-provided file paths were resolved using `files.get_abs_path` and read directly from the filesystem without verification, allowing directory traversal sequences (like `../`) to escape the application's base directory and access sensitive files on the host (e.g. `/etc/passwd`).
**Learning:** Functions designed to convert relative paths to absolute paths (`get_abs_path`) do not inherently enforce directory restrictions, and trusting external user input blindly for file operations leaves the system vulnerable to traversal attacks.
**Prevention:** Always perform a definitive security check (e.g., `files.is_in_base_dir()`) on resolved absolute paths against an allowed base directory before interacting with the file system.
