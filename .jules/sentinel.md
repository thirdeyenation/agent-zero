## 2024-05-24 - Zip Slip in skills import
**Vulnerability:** Found `z.extractall(target)` without sanitizing path traversal members in `helpers/skills_import.py`.
**Learning:** Python's `zipfile` module does not prevent path traversal if members contain absolute paths or relative paths (`../`) that escape the target extraction directory.
**Prevention:** Always verify members before extracting using `is_relative_to` for paths, e.g., `if not (target / member).resolve().is_relative_to(target.resolve()): raise ValueError("Path traversal detected")`. Alternatively, safely extract files individually ensuring safe paths, or iterate and ensure `extractall` uses safe member lists.
