# Research: File Tree Utility

## Decisions

- Ignore semantics implementation: Use `pathspec` with Git wildmatch patterns to evaluate `.gitignore`-style rules, including `!` negation, directory-only patterns (trailing `/`), and `**` recursion. Paths must be evaluated relative to the scanned root.
- `ignore` input resolution:
  - Inline patterns: treat the string as `.gitignore` content
  - `file:/abs/path/.gitignore` and `file:///abs/path/.gitignore`: absolute file path
  - `file:relative/path/.gitignore` and `file://.gitignore`: resolve relative to `relative_path` (the scan root)
- Traversal strategy: Breadth-first by depth. For each directory, collect children (folders/files), apply limits (`max_folders`, `max_files`) and sorting, render lines and comments, then move to next directory at the same depth before descending.
- Sorting: Group by folder/file depending on `folders_first` (default True). Within each group, sort by `modified` (default key) descending (default direction). Support keys: name, created, modified; directions: asc, desc.
- Performance: Cap items per directory, cap total lines (`max_lines`), and short-circuit deeper traversal once `max_lines` is met after finishing the current depth pass. Ensure deterministic ordering with stable sorts.
- Datetime fields: Use timezone-aware UTC `datetime` for `created` and `modified`. Consumers can convert with `.isoformat()` or `.timestamp()` as needed.
- Output forms:
  - `string`: join rendered `text` lines with newlines (no metadata returned)
  - `flat`: return flat list of TreeItem dicts
  - `nested`: return top-level list where folder TreeItems contain `items` arrays of children; files/comments have `items` as `null` or `[]`
- Helper placement: Implement helpers at end of `python/helpers/files.py` with single leading underscore names (module-internal convention).

## Rationale

- `pathspec` is de facto for Git wildmatch semantics; it correctly handles edge cases and negations.
- Breadth-first traversal matches spec requirements (FR‑006) and yields predictable depth-wise rendering.
- Using existing helpers in `python/helpers/files.py` adheres to architecture and centralizes filesystem logic.
- UTC-aware datetimes avoid ambiguity and make conversions straightforward.

## Alternatives Considered

- `gitignore_parser`: Simpler API but less explicit control vs `pathspec` and not the preferred dependency in spec.
- Depth-first traversal: Simpler implementation, but violates FR‑006 breadth-first requirement and produces different visual grouping.
- Returning only strings: Loses metadata needed by downstream automation; rejected in favor of multiple modes.

## Clarifications Resolved

- Python version: Target Python 3.11+ (tested under 3.12 on Linux). No features require newer than 3.11.
- Default `folders_first`: True by default (per Clarifications), with parameter to toggle.
- Large directory behavior: Per-directory `max_folders`/`max_files` with summary comment lines; stop descending when `max_lines` reached, but finish current depth scan.
