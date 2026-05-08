
## 2024-05-24 - Optimize path containment checks
**Learning:** `os.path.commonpath` is slow because it allocates lists and splits paths internally.
**Action:** Replace it with a string-based containment check using `os.path.abspath` and `str.startswith()` while ensuring a trailing `os.sep` is conditionally appended to the absolute directory to prevent path traversal bugs.
