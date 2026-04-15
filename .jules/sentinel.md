## 2025-03-05 - Path Traversal in ApiFilesGet
 **Vulnerability:** The `ApiFilesGet` handler resolved user-provided paths without verifying they were within the base directory (`/app`), allowing arbitrary file read via path traversal.
 **Learning:** When resolving file paths based on user input, simply converting paths to absolute is insufficient. Unchecked `get_abs_path` or using the raw path allows attackers to escape the intended directory tree.
 **Prevention:** Always validate that the fully resolved path is contained within the expected directory using `files.is_in_base_dir(resolved_path)` before attempting to read, write, or serve the file.
