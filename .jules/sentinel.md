## 2024-05-24 - simpleeval Sandbox Escape (CVE-2026-32640)
**Vulnerability:** The `simpleeval` package used in the project allowed arbitrary function execution resulting in potential sandbox escapes or remote code injection during the evaluation of user inputs and template conditions.
**Learning:** Using `simple_eval()` without explicitly disabling `functions` allowed unintended function executions.
**Prevention:** Update `simpleeval` dependency to version >=1.0.5 and always use `SimpleEval(names=..., functions={}).eval(...)` to prevent code execution when only evaluating variables.
## 2024-05-24 - Path Traversal in API Files Get
**Vulnerability:** The `ApiFilesGet` endpoint allowed arbitrary reading of files by not verifying if the dynamically generated `external_path` was inside the application base directory or other allowed directories. Attackers could supply paths like `/a0/../../../../etc/passwd` to exfiltrate system data since they were simply translated to absolute paths and opened directly.
**Learning:** `helpers.files.get_abs_path` resolves paths but does not inherently enforce boundary checks or prevent directory traversal `../` beyond simply normalizing the string. If `get_abs_path` is passed a path like `../../`, it will happily resolve it outside of `_base_dir`.
**Prevention:** Always follow calls to `get_abs_path` on user-provided path inputs with a definitive security boundary check using `helpers.files.is_in_base_dir(path)` before accessing the filesystem for reading or writing.
## 2024-05-25 - Path Traversal in File Download API
**Vulnerability:** The `DownloadFile` endpoint in `api/download_work_dir_file.py` allowed arbitrary file downloads. The API used `helpers.files.get_abs_path` through `file_info.get_file_info(path)` without performing a boundary check on the supplied `path` parameter. An attacker could retrieve files outside of the workspace directory.
**Learning:** Even when delegating to another function like `get_file_info`, the top-level endpoint receiving user input must still enforce boundaries if the underlying function doesn't. A raw path must be validated before it is used to retrieve file information or content.
**Prevention:** Always follow calls to `get_abs_path(path)` with `helpers.files.is_in_base_dir(abs_path)` in API handlers dealing with user-provided file paths.
