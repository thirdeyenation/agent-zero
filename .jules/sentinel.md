## 2025-05-23 - Prevent Zip Slip Vulnerability in Skills Import
**Vulnerability:** Path traversal (Zip Slip) vulnerability found in `helpers/skills_import.py` when using `z.extractall()` without validating archive members.
**Learning:** `zipfile.ZipFile.extractall()` does not inherently prevent path traversal using relative paths (`../`), allowing maliciously crafted ZIP files to overwrite files outside the intended extraction directory.
**Prevention:** Always validate every member of `z.namelist()` to ensure its resolved absolute path falls within the intended target directory before extracting.
