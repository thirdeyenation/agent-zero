## 2023-10-27 - Path traversal in skill zip extraction
**Vulnerability:** Path traversal vulnerability due to unchecked zip file extraction.
**Learning:** `zipfile.ZipFile.extractall()` is vulnerable to directory traversal attacks if the zip file contains relative paths like `../`.
**Prevention:** Always validate every path in the archive using `os.path.abspath` and `str.startswith` instead of `.resolve()` or `.is_relative_to()` before extracting to prevent path traversal while maintaining performance.
