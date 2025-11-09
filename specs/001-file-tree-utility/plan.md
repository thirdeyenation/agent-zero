# Implementation Plan: File Tree Utility

**Branch**: `001-file-tree-utility` | **Date**: 2025-11-08 | **Spec**: `specs/001-file-tree-utility/spec.md`
**Input**: Feature specification from `/specs/001-file-tree-utility/spec.md`

**Note**: This plan is produced by the `/speckit.plan` workflow.

## Summary

Implement a `file_tree()` utility in `python/helpers/files.py` that generates a readable ASCII tree along with structured metadata. The function supports three output modes (`string`, `flat`, `nested`), breadth‑first traversal, `.gitignore`-style filtering via `pathspec`, sorting and grouping (folders vs files), depth and line limits, and summary comment lines when limits are reached. All filesystem access must use existing helpers in `python/helpers/files.py`. Convenience constants are defined adjacent to the function, and helper routines are implemented as module-internal functions with a single leading underscore.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: `pathspec==0.12.1`, standard library `datetime`, existing helpers in `python/helpers/files.py`
**Storage**: N/A (read-only filesystem traversal)
**Testing**: `pytest` with temporary directories (mktemp family) and snapshot/assertion tests under `tests/`
**Target Platform**: Linux (development + container), cross-platform filesystem semantics respected
**Project Type**: Single-user backend helper within existing codebase
**Performance Goals**: For ≥5,000 entries and `max_lines=200`, return within ~2 seconds with deterministic ordering (per SC-003)
**Constraints**:
- Use Agent Zero filesystem helpers (FR‑013) for path ops and listing
- Honor `.gitignore` Git wildmatch semantics including negation and `**` (FR‑004)
- Breadth‑first traversal order; folders grouped per `folders_first` (FR‑005/006)
- Non-blocking async discipline: function is synchronous; avoid calling on event loop hot paths
**Scale/Scope**: Should handle large directories (5k+ entries) with limits applied per directory and overall lines

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Exploration-First Development: Using existing helpers in `python/helpers/files.py` and reading spec; PASS
- Security-First: Read-only traversal, no secrets to UI, no new endpoints; PASS
- Non-Blocking Async: Utility is synchronous; caller must not invoke on event loop hot paths; PASS
- Architectural Boundaries: No new systems; extends helpers only; PASS
- Environment Separation: Reuses helpers that abstract environment; PASS
- PrintStyle Logging Only: No logging added; N/A
- Project Scope & Simplicity: Single-user helper, no enterprise features; PASS

## Project Structure

### Documentation (this feature)
```text
specs/001-file-tree-utility/
├── plan.md              # This file (/speckit.plan output)
├── research.md          # Phase 0 output (/speckit.plan)
├── data-model.md        # Phase 1 output (/speckit.plan)
├── quickstart.md        # Phase 1 output (/speckit.plan)
└── contracts/           # Phase 1 output (/speckit.plan)
```

### Source Code (repository root)
```text
python/
└── helpers/
    └── files.py         # Add file_tree(), constants, and helper functions

tests/
├── test_file_tree_string.py
├── test_file_tree_structured.py
└── test_file_tree_ignore_and_limits.py
```

**Structure Decision**: Extend `python/helpers/files.py` with the new utility and add three pytest modules in `tests/` to validate string snapshot, structured outputs, ignore/limits, and sorting behaviors.

- `tests/test_file_tree_string.py` also owns the breadth-first traversal regression test to ensure level N entries render before level N+1 across modes.
- `tests/test_file_tree_structured.py` covers metadata assertions for flat/nested outputs, including ignore semantics for nested structures.
- `tests/test_file_tree_ignore_and_limits.py` includes the performance guard using `time.perf_counter()` to assert the ≤2.0 s budget on ≥5k synthetic entries while exercising limit summaries.

## Complexity Tracking

No constitutional violations identified; section not applicable.

## Constitution Check (Post-Design)

Re-evaluated after drafting research, data model, contracts, and quickstart:
- Exploration-First Development: PASS
- Security-First Design: PASS
- Non-Blocking Async: PASS (utility remains synchronous; callers should avoid hot event-loop contexts)
- Architectural Boundaries: PASS
- Environment Separation: PASS
- PrintStyle Logging Only: PASS (no logging added)
- Project Scope & Simplicity: PASS
