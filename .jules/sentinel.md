## 2025-02-14 - Fix Zip Slip in skills_import.py
**Vulnerability:** Zip Slip (path traversal during ZIP extraction using `z.extractall(target)`)
**Learning:** `zipfile.ZipFile.extractall()` is inherently vulnerable to path traversal.
**Prevention:** Explicitly verify that every extracted member's resolved path falls within the intended target directory using `Path.is_relative_to()`.
