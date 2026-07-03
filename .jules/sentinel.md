## 2024-05-24 - [Path Traversal in API Files Get]
 **Vulnerability:** Unrestricted file path loading in `/api/files/get` allowing users to read any file on the machine like `/etc/passwd`.
 **Learning:** Paths weren't validated against the application's base directory before reading them to standard response outputs.
 **Prevention:** Use explicit checks like `files.is_in_base_dir(external_path)` to ensure paths cannot traverse outside intended bounds.
