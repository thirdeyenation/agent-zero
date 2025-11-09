# Tasks: File Tree Utility (`001-file-tree-utility`)

This checklist is organized by phases and user stories. Each task is atomic, ordered, and includes explicit file paths. Tests are included because the feature specification mandates them.

## Phase 1 — Setup

- [X] T001 [P] Verify `pathspec==0.12.1` present in `requirements.txt` (/home/rafael/Workspace/Repos/rafael/a0-local/requirements.txt)
- [X] T002 [P] Create pytest module scaffold for string mode tests (create file) (/home/rafael/Workspace/Repos/rafael/a0-local/tests/test_file_tree_string.py)
- [X] T003 [P] Create pytest module scaffold for structured modes tests (create file) (/home/rafael/Workspace/Repos/rafael/a0-local/tests/test_file_tree_structured.py)
- [X] T004 [P] Create pytest module scaffold for ignore/limits tests (create file) (/home/rafael/Workspace/Repos/rafael/a0-local/tests/test_file_tree_ignore_and_limits.py)

## Phase 2 — Foundational

- [X] T005 Add required imports for file tree utility (datetime, typing, pathspec usage; reuse existing helpers) (/home/rafael/Workspace/Repos/rafael/a0-local/python/helpers/files.py)
- [X] T006 Define constants `SORT_BY_NAME`, `SORT_BY_CREATED`, `SORT_BY_MODIFIED`, `SORT_ASC`, `SORT_DESC`, `OUTPUT_MODE_STRING`, `OUTPUT_MODE_FLAT`, `OUTPUT_MODE_NESTED` directly above `file_tree()` (/home/rafael/Workspace/Repos/rafael/a0-local/python/helpers/files.py)
- [X] T007 Add `file_tree()` signature and comprehensive docstring per contract (parameters, constants, ignore resolution examples, datetime conversion examples, async usage note) (/home/rafael/Workspace/Repos/rafael/a0-local/python/helpers/files.py)
- [X] T008 Stub internal helpers (`_resolve_ignore_patterns`, `_list_directory_children`, `_apply_sorting_and_limits`, `_format_line`, `_build_tree_items_flat`, `_to_nested_structure`) at end of module (/home/rafael/Workspace/Repos/rafael/a0-local/python/helpers/files.py)

## Phase 3 — [US1] Readable Tree Overview (P1)

- [X] T009 [US1] Implement breadth‑first traversal and directory scanning pipeline honoring `max_depth` (/home/rafael/Workspace/Repos/rafael/a0-local/python/helpers/files.py)
- [X] T010 [US1] Implement `.gitignore` wildmatch filtering via `pathspec`; support `file:` resolution variants (/home/rafael/Workspace/Repos/rafael/a0-local/python/helpers/files.py)
- [X] T011 [US1] Implement grouping/sorting with `folders_first` and `(key, direction)`; default `(modified, desc)` (/home/rafael/Workspace/Repos/rafael/a0-local/python/helpers/files.py)
- [X] T012 [US1] Implement per‑directory `max_folders`/`max_files` summaries (`# N more files|folders`) (/home/rafael/Workspace/Repos/rafael/a0-local/python/helpers/files.py)
- [X] T013 [US1] Implement global `max_lines` with finish‑current‑depth behavior before stopping descent (/home/rafael/Workspace/Repos/rafael/a0-local/python/helpers/files.py)
- [X] T014 [US1] Implement ASCII render (`├──`/`└──`, folder `/`, `#` comment prefix) and return `OUTPUT_MODE_STRING` string (/home/rafael/Workspace/Repos/rafael/a0-local/python/helpers/files.py)
- [X] T015 [P] [US1] Write snapshot tests for string mode output (glyphs, folder suffix, comments) (/home/rafael/Workspace/Repos/rafael/a0-local/tests/test_file_tree_string.py)
- [X] T016 [P] [US1] Write tests for ignore semantics and per‑directory/global limits (may exercise multiple modes) (/home/rafael/Workspace/Repos/rafael/a0-local/tests/test_file_tree_ignore_and_limits.py)
- [X] T024 [US1] Implement invalid-input error handling: raise clear exception for non-existent `relative_path` (/home/rafael/Workspace/Repos/rafael/a0-local/python/helpers/files.py)
- [X] T025 [P] [US1] Add test asserting clear exception/message for non-existent `relative_path` (/home/rafael/Workspace/Repos/rafael/a0-local/tests/test_file_tree_string.py)
- [X] T026 [P] [US1] Write test: empty directory renders top-level only, no errors (/home/rafael/Workspace/Repos/rafael/a0-local/tests/test_file_tree_string.py)
- [X] T027 [P] [US1] Write test: `folders_first=False` ordering in string mode (/home/rafael/Workspace/Repos/rafael/a0-local/tests/test_file_tree_string.py)
- [X] T028 [P] [US1] Write tests: sort variants (name/created/modified × asc/desc) in string mode (/home/rafael/Workspace/Repos/rafael/a0-local/tests/test_file_tree_string.py)
- [X] T029 [P] [US1] Write tests: `max_depth` behaviors (0 unlimited, 1, 2) in string mode (/home/rafael/Workspace/Repos/rafael/a0-local/tests/test_file_tree_string.py)
- [X] T030 [P] [US1] Write test: `max_lines` finishes current depth before stopping (/home/rafael/Workspace/Repos/rafael/a0-local/tests/test_file_tree_ignore_and_limits.py)
- [X] T031 [P] [US1] Write tests: per-directory `max_folders`/`max_files` with correct summary comments (/home/rafael/Workspace/Repos/rafael/a0-local/tests/test_file_tree_ignore_and_limits.py)
- [X] T032 [P] [US1] Write tests: ignore inline semantics including `!` negation, directory-only `/`, `**` recursion (/home/rafael/Workspace/Repos/rafael/a0-local/tests/test_file_tree_ignore_and_limits.py)
- [X] T033 [P] [US1] Write tests: ignore from file using `file:`, `file://`, `file:///` resolution (/home/rafael/Workspace/Repos/rafael/a0-local/tests/test_file_tree_ignore_and_limits.py)
- [X] T048 [P] [US1] Write regression test that fails when traversal output becomes depth-first (assert breadth-first ordering across multiple depths) (/home/rafael/Workspace/Repos/rafael/a0-local/tests/test_file_tree_string.py)
- [X] T034 [P] [US1] Execute US1 tests and record results (pytest selection) (/home/rafael/Workspace/Repos/rafael/a0-local/tests/)
- [X] T035 [P] [US1] Baseline/update snapshots using external fixture files; ensure glyphs and formatting preserved (/home/rafael/Workspace/Repos/rafael/a0-local/tests/fixtures/file_tree/)
- [X] T046 [P] [US1] Create snapshot fixtures directory and baseline files (e.g., `us1_string_default.txt`, permutations) (/home/rafael/Workspace/Repos/rafael/a0-local/tests/fixtures/file_tree/)
- [X] T047 [P] [US1] Update string-mode tests to load expected snapshots from fixture files (/home/rafael/Workspace/Repos/rafael/a0-local/tests/test_file_tree_string.py)

## Phase 4 — [US2] Flat Structured Listing (P2)

- [X] T017 [US2] Implement `OUTPUT_MODE_FLAT` returning list of dicts with fields (`name`, `level`, `type`, `created`, `modified`, `text`) (/home/rafael/Workspace/Repos/rafael/a0-local/python/helpers/files.py)
- [X] T018 [P] [US2] Write tests validating flat items, tz‑aware UTC datetimes, ordering and levels (/home/rafael/Workspace/Repos/rafael/a0-local/tests/test_file_tree_structured.py)
- [X] T036 [P] [US2] Write test: all fields present and `created`/`modified` are tz-aware UTC (/home/rafael/Workspace/Repos/rafael/a0-local/tests/test_file_tree_structured.py)
- [X] T037 [P] [US2] Write test: levels align with hierarchy; files/comments have no `items` (/home/rafael/Workspace/Repos/rafael/a0-local/tests/test_file_tree_structured.py)
- [X] T038 [P] [US2] Write tests: ordering respects `folders_first` and sort variants in flat mode (/home/rafael/Workspace/Repos/rafael/a0-local/tests/test_file_tree_structured.py)
- [X] T039 [P] [US2] Write tests: ignore semantics mirrored in flat mode (inline and file-based) (/home/rafael/Workspace/Repos/rafael/a0-local/tests/test_file_tree_structured.py)
- [X] T040 [P] [US2] Execute US2 tests and record results (pytest selection) (/home/rafael/Workspace/Repos/rafael/a0-local/tests/)

## Phase 5 — [US3] Nested Structured Listing (P3)

- [X] T019 [US3] Implement `OUTPUT_MODE_NESTED` building hierarchical `items` arrays; honor `max_depth` (/home/rafael/Workspace/Repos/rafael/a0-local/python/helpers/files.py)
- [X] T020 [P] [US3] Write tests validating nested structure, children arrays, and depth limiting (/home/rafael/Workspace/Repos/rafael/a0-local/tests/test_file_tree_structured.py)
- [X] T041 [P] [US3] Write test: nested items arrays for folders; files/comments have `None`/empty (/home/rafael/Workspace/Repos/rafael/a0-local/tests/test_file_tree_structured.py)
- [X] T042 [P] [US3] Write test: `max_depth` truncation represented appropriately (e.g., comment items) (/home/rafael/Workspace/Repos/rafael/a0-local/tests/test_file_tree_structured.py)
- [X] T043 [P] [US3] Write test: deterministic ordering within each level in nested mode (/home/rafael/Workspace/Repos/rafael/a0-local/tests/test_file_tree_structured.py)
- [X] T044 [P] [US3] Execute US3 tests and record results (pytest selection) (/home/rafael/Workspace/Repos/rafael/a0-local/tests/)
- [X] T049 [P] [US3] Write tests: ignore semantics (including `!`, `/`, `**`, file-based patterns) reflected in `OUTPUT_MODE_NESTED` results (/home/rafael/Workspace/Repos/rafael/a0-local/tests/test_file_tree_structured.py)

## Final Phase — Polish & Cross‑Cutting

- [X] T022 [P] Add automated performance guard test using `time.perf_counter()` to assert a ≥5k entry synthetic tree with `max_lines=200` completes within 2.0 seconds while verifying deterministic ordering and summary comments (/home/rafael/Workspace/Repos/rafael/a0-local/tests/test_file_tree_ignore_and_limits.py)
- [X] T023 [P] Align contract doc with final signature/details if needed (/home/rafael/Workspace/Repos/rafael/a0-local/specs/001-file-tree-utility/contracts/file_tree.md)
- [X] T045 [P] Run full test suite and collect coverage report (target 100% for new code) (/home/rafael/Workspace/Repos/rafael/a0-local/tests/)

## Phase 6 — Extended Validation

- [X] T050 [P] Expand string-mode coverage to validate all sorting key/direction combinations and deep `max_lines` truncation (/home/rafael/Workspace/Repos/rafael/a0-local/tests/test_file_tree_string.py)
- [X] T051 [P] Add negative/invalid parameter tests (unsupported sort tuples, invalid output modes, negative limits, missing ignore file) (/home/rafael/Workspace/Repos/rafael/a0-local/tests/test_file_tree_invalid.py)
- [X] T052 [P] Validate nested summary comment generation when per-directory limits truncate children (/home/rafael/Workspace/Repos/rafael/a0-local/tests/test_file_tree_structured.py)

---

## Dependencies (Story Order)
- US1 → US2 → US3 (string mode first, then flat, then nested). Foundational Phase 2 must precede all stories.

## Parallel Execution Examples
- US1: Implement `_resolve_ignore_patterns` [P] in parallel with writing initial snapshot tests file.
- US2: Add flat‑mode fields and write field assertions [P] concurrently.
- US3: Build `_to_nested_structure` [P] while extending structured tests for nested validation.

## Implementation Strategy
- MVP scope: Complete US1 (string mode) with ignore/limits and snapshot tests.
- Incrementally add US2 (flat) and US3 (nested), keeping tests green after each phase.

## Validation
- All tasks follow required checklist format with IDs, optional [P], optional [US?], and explicit file paths.
