## 2025-06-13 - Path Traversal (Zip Slip) in Skill Import
**Vulnerability:** Found a Zip Slip vulnerability in `helpers/skills_import.py` where uploaded zip files were extracted without checking if their member paths fell within the intended destination directory.
**Learning:** `zipfile.ZipFile.extractall()` inherently does not resolve paths against the intended extraction root unless manually implemented, leaving an opening for `../` style path traversals.
**Prevention:** Always validate every member in `z.namelist()` using `pathlib.Path.is_relative_to()` against the resolved destination path before extracting.
