## 2024-05-24 - API Files Path Traversal Vulnerability
**Vulnerability:** The API endpoint `api/api_files_get.py` allowed path traversal attacks, returning files arbitrarily on the filesystem if absolute paths or paths with `../` were provided.
**Learning:** By directly taking paths from user input and opening them without checking if they reside within an allowed directory structure, arbitrary files could be read and returned via the API in Base64 encoding. Even when paths start with expected prefixes like `/a0/`, combining them with `../` bypassing the intent.
**Prevention:** Always validate that resolved file paths are contained within the intended base directory using safe path containment methods like `files.is_in_base_dir()` before reading or processing them.
