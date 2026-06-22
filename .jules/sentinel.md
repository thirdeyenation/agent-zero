## 2025-06-22 - Path Traversal in File Downloads
**Vulnerability:** The `api_files_get.py` file retrieval endpoint allowed fetching arbitrary files from the system by accepting absolute paths, as it did not validate if the resolved paths fell within the intended base directory.
**Learning:** Using `os.path.basename` combined with strings is not sufficient for secure file retrieval if earlier code can interpret user inputs as complete absolute file paths bypassing directory construction.
**Prevention:** Always strictly enforce boundaries for user-supplied paths by validating that the resolved absolute path starts with or resides within the expected sandbox directory tree, using methods like `files.is_in_base_dir()`.
