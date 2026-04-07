## 2024-05-24 - simpleeval Sandbox Escape (CVE-2026-32640)
**Vulnerability:** The `simpleeval` package used in the project allowed arbitrary function execution resulting in potential sandbox escapes or remote code injection during the evaluation of user inputs and template conditions.
**Learning:** Using `simple_eval()` without explicitly disabling `functions` allowed unintended function executions.
**Prevention:** Update `simpleeval` dependency to version >=1.0.5 and always use `SimpleEval(names=..., functions={}).eval(...)` to prevent code execution when only evaluating variables.
## 2024-05-24 - Path Traversal in API Files Get
**Vulnerability:** The `ApiFilesGet` endpoint allowed arbitrary reading of files by not verifying if the dynamically generated `external_path` was inside the application base directory or other allowed directories. Attackers could supply paths like `/a0/../../../../etc/passwd` to exfiltrate system data since they were simply translated to absolute paths and opened directly.
**Learning:** `helpers.files.get_abs_path` resolves paths but does not inherently enforce boundary checks or prevent directory traversal `../` beyond simply normalizing the string. If `get_abs_path` is passed a path like `../../`, it will happily resolve it outside of `_base_dir`.
**Prevention:** Always follow calls to `get_abs_path` on user-provided path inputs with a definitive security boundary check using `helpers.files.is_in_base_dir(path)` before accessing the filesystem for reading or writing.

## 2025-02-24 - Fix Timing Attack Vulnerabilities in Authentication Checks

**Vulnerability:** The functions `requires_api_key`, `requires_auth`, and `csrf_protect` in `helpers/api.py` used simple string comparison (`!=`) to validate API keys, authentication hashes, and CSRF tokens. This exposed the application to timing attacks, where an attacker could deduce valid tokens by observing the time it took for the server to reject incorrect tokens (since `!=` short-circuits upon encountering the first differing character).

**Learning:** Authentication tokens and cryptographic hashes must always be compared in constant time. The standard `==` or `!=` operators in Python are not safe for these operations because their execution time depends on the length of the matching prefix.

**Prevention:** Use `secrets.compare_digest(a, b)` or `hmac.compare_digest(a, b)` for all comparisons involving sensitive secrets, API keys, session hashes, or CSRF tokens to ensure constant-time comparison and prevent timing attacks.
