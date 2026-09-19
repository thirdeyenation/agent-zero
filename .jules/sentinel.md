## 2024-05-24 - simpleeval Sandbox Escape (CVE-2026-32640)
**Vulnerability:** The `simpleeval` package used in the project allowed arbitrary function execution resulting in potential sandbox escapes or remote code injection during the evaluation of user inputs and template conditions.
**Learning:** Using `simple_eval()` without explicitly disabling `functions` allowed unintended function executions.
**Prevention:** Update `simpleeval` dependency to version >=1.0.5 and always use `SimpleEval(names=..., functions={}).eval(...)` to prevent code execution when only evaluating variables.
## 2024-05-24 - Path Traversal in API Files Get
**Vulnerability:** The `ApiFilesGet` endpoint allowed arbitrary reading of files by not verifying if the dynamically generated `external_path` was inside the application base directory or other allowed directories. Attackers could supply paths like `/a0/../../../../etc/passwd` to exfiltrate system data since they were simply translated to absolute paths and opened directly.
**Learning:** `helpers.files.get_abs_path` resolves paths but does not inherently enforce boundary checks or prevent directory traversal `../` beyond simply normalizing the string. If `get_abs_path` is passed a path like `../../`, it will happily resolve it outside of `_base_dir`.
**Prevention:** Always follow calls to `get_abs_path` on user-provided path inputs with a definitive security boundary check using `helpers.files.is_in_base_dir(path)` before accessing the filesystem for reading or writing.
## 2026-04-17 - Timing Attack in Authentication\n**Vulnerability:** The login handler used a direct string comparison (`==`) to verify the provided username and password against the environment variables. This allowed timing attacks which could potentially leak the credentials byte by byte.\n**Learning:** In authentication or token verification routines, always compare sensitive strings securely using constant-time comparison methods, checking that arguments are the right types to prevent TypeErrors.\n**Prevention:** Use `secrets.compare_digest()` instead of `==` for sensitive string comparisons, and ensure inputs are validated (e.g., using `isinstance`) before comparison.
## 2025-02-28 - Timing Attack Vulnerability in Authentication
 **Vulnerability:** Standard equality operators (`==` and `!=`) were used for sensitive string comparisons (passwords, API keys, CSRF tokens, webhook secrets), exposing the system to timing attacks.
 **Learning:** Standard string comparisons terminate early upon encountering the first mismatched character. This allows attackers to theoretically infer valid tokens character by character by measuring the exact time taken by the server to reject incorrect tokens.
 **Prevention:** Always use `secrets.compare_digest` for validating authentication tokens, hashes, and secrets. When replacing `==` or `!=`, explicitly cast operands to strings handling `None` values (e.g., `secrets.compare_digest(str(a or ""), str(b or ""))`) to prevent `TypeError`s, and ensure necessary modules (like `secrets`) are imported globally.
## 2026-05-17 - Prevent XSS in generic UI components
**Vulnerability:** XSS vulnerability in `showConfirmDialog` via unsafe `innerHTML` interpolation of `title` and `message`.
**Learning:** Generic UI components that accept parameters often construct DOM elements using template literals and `innerHTML`, making them vulnerable if untrusted input is passed.
**Prevention:** Always use `textContent` for text-only inputs, or sanitize HTML inputs using `DOMPurify` (e.g., `sanitizeHtml`) before injecting them into the DOM.
## 2025-06-22 - Path Traversal in File Downloads
**Vulnerability:** The `api_files_get.py` file retrieval endpoint allowed fetching arbitrary files from the system by accepting absolute paths, as it did not validate if the resolved paths fell within the intended base directory.
**Learning:** Using `os.path.basename` combined with strings is not sufficient for secure file retrieval if earlier code can interpret user inputs as complete absolute file paths bypassing directory construction.
**Prevention:** Always strictly enforce boundaries for user-supplied paths by validating that the resolved absolute path starts with or resides within the expected sandbox directory tree, using methods like `files.is_in_base_dir()`.
## 2024-07-04 - Fix Path Traversal in API Files Get
**Vulnerability:** Path traversal vulnerability in `api_files_get` where users could request paths outside the base directory using `../` sequences or absolute paths.
**Learning:** Incomplete validation when converting internal to external paths left arbitrary file read open.
**Prevention:** Always validate that user-provided file paths are contained within the intended base directory using `files.is_in_base_dir` after absolute resolution.
## 2024-05-15 - Path Traversal in File Info API
**Vulnerability:** The `/api/file_info` endpoint allowed path traversal (`../../`) because it used `files.get_abs_path(path)` but did not explicitly check if the resulting absolute path resided within the intended base directory.
**Learning:** Just resolving to an absolute path does not prevent escaping the sandbox if the input contains `../`. The filesystem functions like `os.path.exists()` and `os.stat()` will still succeed for paths outside the base directory.
**Prevention:** Always validate that user-provided file paths are contained within the intended base directory using `files.is_in_base_dir(abs_path)` after absolute resolution.
