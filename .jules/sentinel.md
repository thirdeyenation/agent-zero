## 2025-02-12 - Path Traversal in Skill Importer Zip Extraction
**Vulnerability:** Found a Zip Slip vulnerability in `helpers/skills_import.py` where `zipfile.ZipFile.extractall()` was called on untrusted zip paths without checking if the embedded file members traversed outside the target directory (e.g. `../` paths).
**Learning:** Python's built-in `zipfile` module does not protect against path traversal automatically when using `extractall()`.
**Prevention:** Instead of directly calling `extractall()`, iterate through `z.namelist()`, construct absolute destination paths using `.resolve()`, and verify they are safe using `Path.is_relative_to(target.resolve())` before extracting.
