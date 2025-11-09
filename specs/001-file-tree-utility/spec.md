# Feature Specification: File Tree Utility

**Feature Branch**: `001-file-tree-utility`
**Created**: 2025-11-08
**Status**: Draft
**Input**: User description: "File Tree Utility"

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.

  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - Readable Tree Overview (Priority: P1)

As a developer, I want a fast, readable ASCII tree of a folder so I can quickly understand the structure without opening each directory.

**Why this priority**: Immediate visualization of project layout is the most common need and unlocks rapid navigation and understanding, within the SC-003 performance target (~2 seconds for ≥5,000 entries with `max_lines=200`).

**Independent Test**: Create a synthetic directory structure and call the utility with `mode=string`; verify the exact multi-line ASCII output matches the expected snapshot.

**Acceptance Scenarios**:

1. **Given** a base folder with subfolders and files, **When** I call the utility with default parameters and `mode=string`, **Then** it returns a multi-line ASCII tree with folders suffixed by `/`, and summary comment lines for truncated lists using the format `# N more files|folders`.
2. **Given** an ignore pattern string using `.gitignore` syntax, **When** I call the utility, **Then** ignored entries are excluded while negation patterns re-include matching paths.
3. **Given** nested folders at three or more depth levels, **When** I call the utility with `mode=string`, **Then** every level N renders before any entry from level N+1 (breadth-first ordering).

---

### User Story 2 - Flat Structured Listing (Priority: P2)

As a developer, I want a flat list of items with metadata (name, type, level, created/modified datetimes, text) so I can programmatically filter, analyze, or render custom outputs.

**Why this priority**: Enables downstream automation and analysis beyond visual inspection.

**Independent Test**: Call the utility with `mode=flat` and verify the array of objects contains correct fields and values for a known synthetic structure.

**Acceptance Scenarios**:

1. **Given** a known directory with deterministic file timestamps, **When** I call `mode=flat`, **Then** each item includes `name`, `level`, `type ∈ {file, folder, comment}`, `created` (tz-aware UTC), `modified` (tz-aware UTC), and `text`, and ordering respects sort rules.

---

### User Story 3 - Nested Structured Listing (Priority: P3)

As a developer, I want a nested structure where folder items contain an `items` array of their children so I can traverse the tree in-memory.

**Why this priority**: Supports hierarchical processing and incremental rendering.

**Independent Test**: Call the utility with `mode=nested` and verify parent folders contain `items` arrays while files and comments have `items` as `null` or `[]`.

**Acceptance Scenarios**:

1. **Given** a directory with multiple depths, **When** I call `mode=nested` with `max_depth=2`, **Then** the result contains children up to level 2 and deeper levels are represented by comment lines indicating remaining items.

---

[Add more user stories as needed, each with an assigned priority]

### Edge Cases

- Empty directories should produce only the top-level line and no errors.
- `max_depth=0` means unlimited depth; `max_lines=0` means unlimited lines.
- `folders_first` ordering toggles whether folders are listed before files; sorting still applies within each group.
- Very large directories apply `max_folders`/`max_files` per directory and append comment lines (e.g., `# 23 more files`).
- Ignore patterns must follow `.gitignore` semantics including `!` negation, directory-only patterns (`/`), and `**` recursion.
- Non-existent path results in a clear error surfaced to the caller.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Provide a folder tree utility that outputs one of three modes:
  a) `string`: multi-line ASCII tree;
  b) `flat`: flat array of items with metadata;
  c) `nested`: array at root where folder items include `items` arrays for children.
- **FR-002**: Each listed element must include: `name`, `level` (depth starting at 1 for root entries), `type` (`file` | `folder` | `comment`), `created` (timezone-aware UTC datetime), `modified` (timezone-aware UTC datetime), and `text` (the rendered single-line tree segment such as `├── file.py` or `└── # 6 more folders`).
- **FR-003**: Accept parameters: `relative_path`, `max_depth` (0 = unlimited), `max_lines` (0 = unlimited), `folders_first` (bool), `max_folders`, `max_files`, `sort` (key: name | modified | created; dir: asc | desc), `ignore` (string with `.gitignore` semantics; if starts with `file:`, load patterns from that file), and `output_mode` (`string` | `flat` | `nested`).
  - `ignore` resolution rules when using `file:`:
    - `file:/abs/path/.gitignore` → absolute filesystem path (single slash after colon indicates absolute path)
    - `file:relative/path/.gitignore` → path resolved relative to `relative_path` (scanned root)
    - `file://.gitignore` → path resolved relative to `relative_path` (two slashes indicate URI form; still relative without the third slash)
    - `file:///abs/path/.gitignore` → absolute filesystem path (classic URI absolute form with three slashes)
    - If not prefixed with `file:`, treat `ignore` as inline `.gitignore` content string
- **FR-004**: Apply ignore patterns using Git wildmatch semantics (comments, blanks ignored; support `!` negation, directory-only patterns, `**` recursion) against paths relative to the scanned root.
- **FR-005**: Sorting: group by folder/file based on `folders_first`, then sort by the requested key and direction within each group. Default is sort by modification time descending; default `folders_first=True` (folders before files).
- **FR-006**: Traversal order is breadth-first by depth: scan and render all directories at level N before descending to N+1, honoring `max_depth`, `max_files`, and `max_folders`.
- **FR-007**: When limits are reached within a directory, render summary comment lines indicating the number of omitted files and/or folders (e.g., `# 12 more files`, `# 6 more folders`).
- **FR-008**: The ASCII `text` format uses `├──`/`└──` with indentation guides, appends `/` to folders, and prefixes comments with `# `.
- **FR-009**: Errors for invalid inputs (e.g., non-existent path) must be clear and actionable.
- **FR-010**: Implementation MUST satisfy the detailed interface contract documented in `specs/001-file-tree-utility/contracts/file_tree.md`, including developer-facing ergonomics, helper structure, and docstring guidance.

## Clarifications

### Session 2025-11-08

- Q: What should be the default for `folders_first` ordering? → A: `True` (folders before files) by default.
- Q: Which filesystem access conventions should be followed? → A: Use Agent Zero wrappers in `python/helpers/files.py` (e.g., `get_abs_path`, `exists`, `list_files`) whenever possible; fallback to the same Python modules used in `files.py` only when no wrapper exists.
- Q: How to resolve `ignore` when prefixed with `file:`? → A: Resolve relative to `relative_path` when the path after `file:` or `file://` is relative; treat as absolute when starting with `/` (support both `file:/abs/...` and `file:///abs/...`). Document with examples in the function docstring.

### Key Entities *(include if feature involves data)*

- **TreeItem**:
  - `name: str` — filename or folder name (or comment label)
  - `level: int` — depth level starting from 1 at root entries
  - `type: "file" | "folder" | "comment"`
  - `created: datetime` — timezone-aware UTC
  - `modified: datetime` — timezone-aware UTC
  - `text: str` — one-line rendered tree segment
  - `items: list[TreeItem] | null` — present for folders in nested mode; empty or null for files and comments

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For a known synthetic structure (≤ 50 nodes), `mode=string` output matches the stored snapshot exactly (whitespace and glyphs).
- **SC-002**: Given ignore patterns with negations, excluded entries never appear and negated entries always appear in all modes.
- **SC-003**: For a directory containing ≥ 5,000 entries, an automated test using a monotonic timer (`time.perf_counter()`) asserts that a call with `max_lines=200` completes within 2.0 seconds while rendering deterministic ordering and correct summary comment lines.
- **SC-004**: `created`/`modified` fields are timezone-aware UTC datetimes and can be converted to ISO 8601 strings and Unix timestamps without loss of timezone information in all modes that include metadata.
- **SC-005**: Automated tests create temporary top-level directories using the mktemp family (cross‑platform), generate synthetic structures, and validate:
  - String snapshot equality for `mode=string`
  - Structural and field correctness for `mode=flat` and `mode=nested`
  - Ignore semantics including negation and directory-only patterns in all modes (string, flat, nested)
  - Breadth-first ordering across multiple depth levels (fails if depth-first traversal occurs)
  - Sorting and summary comment behaviors under limits
  - Sorting for `name`, `created`, and `modified` keys in both ascending and descending directions across flat and nested outputs
  - `created`/`modified` metadata returned by flat and nested modes matches the filesystem stats for the represented entries
  - Invalid parameter paths (unsupported sort tuples, unknown output modes, negative limits, missing referenced ignore file) raise the documented exceptions
  Tests reside under `tests/` and use the utility from `python/helpers/files.py`.

## Testing

- Tests MUST construct synthetic folder/file structures in temporary directories using mktemp family functions to ensure cross‑platform behavior.
- Tests MUST import and exercise `file_tree()` from `python/helpers/files.py` (no duplicated logic).
- Recommended organization:
  - `tests/test_file_tree_string.py` — end‑to‑end snapshot tests for `mode=string`
  - `tests/test_file_tree_structured.py` — validations for `mode=flat` and `mode=nested` (fields, levels, types, ordering)
  - `tests/test_file_tree_ignore_and_limits.py` — `.gitignore` semantics, `max_files`/`max_folders`, `max_depth`, `max_lines`
- For snapshots, store expected multi‑line strings as literals within tests or fixture files adjacent to tests; ensure glyphs (`├──`, `└──`) and folder suffix `/` and comment prefix `# ` are preserved.

## Dependencies

- `.gitignore` evaluation MUST use `pathspec` (Git wildmatch semantics). Target version: `pathspec==0.12.1` (or newer compatible) for implementation; exact pin may be set during dependency management.
