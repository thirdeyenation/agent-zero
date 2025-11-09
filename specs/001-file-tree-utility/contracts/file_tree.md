# Contract: file_tree() Utility

## Location
- Module: `python/helpers/files.py`
- Exported function: `file_tree()`
- Predefined constants (declared directly before function definition):
  - Sort keys: `SORT_BY_NAME`, `SORT_BY_CREATED`, `SORT_BY_MODIFIED`
  - Sort directions: `SORT_ASC`, `SORT_DESC`
  - Output modes: `OUTPUT_MODE_STRING`, `OUTPUT_MODE_FLAT`, `OUTPUT_MODE_NESTED`

## Signature (proposed)
```python
def file_tree(
    relative_path: str,
    *,
    max_depth: int = 0,
    max_lines: int = 0,
    folders_first: bool = True,
    max_folders: int | None = None,
    max_files: int | None = None,
    sort: tuple[str, str] = (SORT_BY_MODIFIED, SORT_DESC),
    ignore: str | None = None,
    output_mode: str = OUTPUT_MODE_STRING,
) -> str | list[dict]:
    ...
```

## Parameters
- `relative_path`: Base folder to scan. The implementation MUST resolve with `get_abs_path(relative_path)` from helpers.
- `max_depth`: Maximum depth to scan; `0` means unlimited.
- `max_lines`: Maximum total output lines across the whole render; `0` means unlimited.
- `folders_first`: If `True`, group folders before files when rendering/sorting (default per Clarifications).
- `max_folders`: Per-directory maximum number of folder entries to render before emitting a summary comment (e.g., `# 6 more folders`).
- `max_files`: Per-directory maximum number of file entries to render before emitting a summary comment (e.g., `# 23 more files`).
- `sort`: Tuple `(key, direction)`:
  - `key ∈ {SORT_BY_NAME, SORT_BY_CREATED, SORT_BY_MODIFIED}`
  - `direction ∈ {SORT_ASC, SORT_DESC}`
  - Default: `(SORT_BY_MODIFIED, SORT_DESC)`
- `ignore`: `.gitignore`-style patterns as inline string, or `file:` reference:
  - `file:/abs/path/.gitignore` or `file:///abs/path/.gitignore` → absolute path
  - `file:relative/path/.gitignore` or `file://.gitignore` → resolved relative to `relative_path`
  - Comments and blanks ignored; support `!` negation, trailing `/` (directory-only), and `**` recursion
- `output_mode`: One of:
  - `OUTPUT_MODE_STRING`: Return a single multi-line string
  - `OUTPUT_MODE_FLAT`: Return a flat list of TreeItem dicts
  - `OUTPUT_MODE_NESTED`: Return a top-level list where folder TreeItems include `items` arrays

## Return Types
- `OUTPUT_MODE_STRING` → `str` (multi-line ASCII)
- `OUTPUT_MODE_FLAT` → `list[TreeItem]`
- `OUTPUT_MODE_NESTED` → `list[TreeItem]`

Where `TreeItem` has:
- `name: str`
- `level: int` (root entries start at 1)
- `type: "file" | "folder" | "comment"`
- `created: datetime` (timezone-aware UTC)
- `modified: datetime` (timezone-aware UTC)
- `text: str` (rendered single-line tree segment, e.g., `├── main.py`, `└── helpers/`, `# 6 more folders`)
- `items: list[TreeItem] | None` (folders in nested mode contain children; files/comments are `None` or empty)

## Behavior
- Traversal order: Breadth-first by depth (FR‑006) for discovery and limit enforcement; string rendering walks the established tree depth-first so connector glyphs reflect parent/child structure.
- Sorting/grouping: Respect `folders_first`; within each group, sort by requested key/direction (FR‑005).
- Limits:
  - Per-directory `max_folders` / `max_files` summarize omitted items with comment lines (FR‑007). When only a single entry exceeds the limit and the limit is greater than zero, that entry is rendered instead of emitting a summary comment. A value of `0` is treated as unlimited for each per-directory constraint.
  - Global `max_lines` caps the total rendered lines; finish current depth level before stopping further descent.
- ASCII format (FR‑008):
  - Use `├──` / `└──` connectors, indentation guides, append `/` to folder names.
  - Prefix comment lines with `# ` (e.g., `# 12 more files`).
- Ignore semantics (FR‑004): Use Git wildmatch via `pathspec`, evaluate paths relative to the scanned root; honor negation `!` patterns and directory-only patterns.

## Error Handling
- Non-existent `relative_path` or inaccessible directories: Raise a clear, actionable error (FR‑009).

## Datetime Conversions (docstring examples required)
```python
# item['created'] and item['modified'] are timezone-aware UTC datetime objects.
iso = item['created'].isoformat()     # e.g., '2025-11-09T00:21:00.123456+00:00'
epoch = item['created'].timestamp()   # e.g., 1762647660.123456
```

## Docstring Requirements
- Document every parameter, including the predefined constants (`SORT_BY_*`, `SORT_*`, `OUTPUT_MODE_*`) so callers understand valid values.
- Include code snippets demonstrating conversion of `created`/`modified` datetimes to ISO 8601 strings and Unix timestamps (see Datetime Conversions section).
- Explain `ignore` resolution for inline patterns and `file:`/`file://`/`file:///` references with examples that match FR‑003 semantics.
- Note that the utility is synchronous and should not be invoked on hot async event-loop paths.

## Helper Functions (module-internal)
- Implement helpers at end of module with single leading underscore:
  - `_resolve_ignore_patterns(...)`
  - `_list_directory_children(...)`
  - `_apply_sorting_and_limits(...)`
  - `_format_line(...)`
  - `_build_tree_items_flat(...)`
  - `_to_nested_structure(...)`

## Implementation Notes
- Perform filesystem operations via existing Agent Zero helpers in `python/helpers/files.py` (`get_abs_path`, `exists`, `list_files`, timestamp helpers, etc.); fall back to standard library only when no wrapper exists.
- Keep helper definitions module-internal (single leading underscore) to preserve the public API surface.

## Dependencies
- `pathspec==0.12.1` for Git wildmatch semantics (FR‑004/Dependencies).
