## 2025-05-29 - Zip Slip in Skills Import
**Vulnerability:** Unsafe extraction of ZIP archives allowing path traversal via z.extractall(target) without checking member paths.
**Learning:** Archives can contain relative paths like ../ to write files outside the intended extraction directory.
**Prevention:** Always iterate through z.namelist(), resolve absolute paths, and use Path.is_relative_to() to ensure containment within the target directory before extracting.
