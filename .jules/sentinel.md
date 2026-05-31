## 2025-05-23 - Prevent Zip Slip Vulnerability
**Vulnerability:** `zipfile.ZipFile.extractall()` is vulnerable to path traversal if the archive contains malicious paths with `../`.
**Learning:** Never blindly extract archives using `extractall()`.
**Prevention:** Iterate over `z.namelist()`, resolve the extraction path, and explicitly verify it falls inside the intended destination using `Path.is_relative_to()` before extracting.
