## YYYY-MM-DD - [Title]
**Vulnerability:** [What you found]
**Learning:** [Why it existed]
**Prevention:** [How to avoid next time]
## 2024-05-24 - Path Traversal in Skill Imports
**Vulnerability:** Zip Slip / Path Traversal in `helpers/skills_import.py` due to unsafe `zipfile.ZipFile.extractall()` without path containment checks.
**Learning:** `extractall()` blindly follows paths in zip files, which can include `../` to escape the extraction directory.
**Prevention:** Always iterate through `z.namelist()`, construct absolute paths, and explicitly verify they are within the target directory using `Path.is_relative_to()` before extraction.
