## 2024-06-25 - Prevent Path Traversal in API Files Get
**Vulnerability:** Arbitrary file read in api/api_files_get.py due to lack of base directory boundaries checking on resolved file paths.
**Learning:** An endpoint returning file contents based on paths provided in the API request must strictly validate those paths to ensure they don't escape the application's root directory via relative traversal or absolute paths.
**Prevention:** Always validate that user-provided file paths are contained within the intended base directory after absolute resolution using files.is_in_base_dir(external_path) before attempting to read or process them.
