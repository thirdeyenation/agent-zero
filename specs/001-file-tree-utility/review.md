# File Tree Utility – Formal Review & Remediation Plan

## 1. Scope & Context
- **Feature**: `file_tree()` helper and supporting internals in `python/helpers/files.py`
- **Artifacts Reviewed**:
  - Implementation source (`python/helpers/files.py`)
  - Test modules (`tests/test_file_tree_string.py`, `tests/test_file_tree_structured.py`, `tests/test_file_tree_ignore_and_limits.py`, `tests/test_file_tree_invalid.py`)
  - String fixtures under `tests/fixtures/file_tree/`
  - Specification bundle in `specs/001-file-tree-utility/` (spec, plan, data-model, contracts, research, tasks)
  - Constitution (`.specify/memory/constitution.md`)
- **Environment**: Python 3.12.11 inside project `.venv`, pytest 8.4.2
  `PYTHONPATH=. pytest tests/test_file_tree_string.py tests/test_file_tree_structured.py tests/test_file_tree_ignore_and_limits.py tests/test_file_tree_invalid.py`

## 2. Specification References
- **FR‑006** / **FR‑007** / **FR‑008** – `specs/001-file-tree-utility/spec.md`
- `contracts/file_tree.md` – finish-current-depth requirement, summary semantics
- Tasks `T013`, `T030`, `T031` – enforcement of depth-finish, limit summaries
- Constitution Principles I & VII – verification of contractual behaviour

## 3. Verified Behaviour & Reproduction
```
python - <<'PY'
from python.helpers.files import file_tree, create_dir, delete_dir, write_file, get_abs_path
import os

def materialize(base, tree):
    for name, value in tree.items():
        rel = os.path.join(base, name)
        if isinstance(value, dict):
            create_dir(rel)
            materialize(rel, value)
        else:
            write_file(rel, value or "")

base = "tmp/tests/file_tree/string_breadth_first_check"
delete_dir(base); create_dir(base)
materialize(base, {
    "alpha": {"alpha_file.txt": "alpha", "nested": {"inner.txt": "inner"}},
    "beta": {"beta_file.txt": "beta"},
    "zeta": {},
    "a.txt": "A",
    "b.txt": "B",
})
print(file_tree(base, folders_first=True, sort=("name","asc"), output_mode="string"))
delete_dir(base)
PY
```
Output shows stray leading `│` ahead of deeper nodes (`nested/`, `alpha_file.txt`, etc.), despite all level-one siblings already rendered.

```
python - <<'PY'
from python.helpers.files import file_tree, create_dir, delete_dir, write_file
import os

def materialize(base, tree):
    for name, value in tree.items():
        rel = os.path.join(base, name)
        if isinstance(value, dict):
            create_dir(rel)
            materialize(rel, value)
        else:
            write_file(rel, value or "")

base = "tmp/tests/file_tree/string_ignore_limits_check"
delete_dir(base); create_dir(base)
materialize(base, {
    "src": {
        "main.py": "print('hello')",
        "utils.py": "pass",
        "tmp.tmp": "",
        "cache": {"cached.txt": "", "keep.txt": ""},
        "modules": {"a.py": "", "b.py": "", "c.py": ""},
    },
    "logs": {"2024.log": "", "2025.log": ""},
    "notes.md": "",
    "build.tmp": "",
})
write_file(os.path.join(base, ".treeignore"), "\n".join(
    ["*.tmp", "cache/", "!src/cache/keep.txt", "logs/", "!logs/2025.log"]
))
print(file_tree(
    base,
    folders_first=False,
    sort=("name","asc"),
    ignore="file:.treeignore",
    max_folders=1,
    max_files=2,
    max_lines=12,
    output_mode="string",
))
delete_dir(base)
PY
```
Produces:
```
tmp/tests/file_tree/string_ignore_limits_check/
├── .treeignore
├── notes.md
├── logs/
└── # 1 more folders
│   └── 2025.log
```
- Comment precedes folder child (`2025.log`), implying a “comment node” with children.
- Grammar shows “# 1 more folders” (singular noun mismatch).

```
python - <<'PY'
from python.helpers.files import file_tree, create_dir, delete_dir, write_file
import os

def materialize(base, tree):
    for name, value in tree.items():
        rel = os.path.join(base, name)
        if isinstance(value, dict):
            create_dir(rel)
            materialize(rel, value)
        else:
            write_file(rel, value or "")

base = "tmp/tests/file_tree/string_max_lines_check"
delete_dir(base); create_dir(base)
materialize(base, {
    "dirA": {f"a{i}.txt": "" for i in range(3)},
    "dirB": {f"b{i}.txt": "" for i in range(3)},
    "root.txt": "",
})
print(file_tree(base, max_lines=2, output_mode="string"))
print(file_tree(base, max_lines=2, output_mode="flat"))
delete_dir(base)
PY
```
Only two top-level entries appear, violating the “finish current depth before stopping” contract.

Pytest run (with corrected `PYTHONPATH`) currently passes, proving tests fail to cover these cases:
```
PYTHONPATH=. pytest tests/test_file_tree_string.py tests/test_file_tree_structured.py \
           tests/test_file_tree_ignore_and_limits.py tests/test_file_tree_invalid.py
```

## 4. Findings (F1–F5)

| ID | Description | Root Cause | Impacted Spec Items |
|----|-------------|------------|---------------------|
| **F1** | ASCII tree shows stray leading `│` for deeper nodes; visual connectors imply depth-first emission though actual order is breadth-first. | String renderer consumes breadth-first list (`nodes_in_order`) directly; `_format_line()` computes connector state from ancestors whose `is_last` flags were never recalculated for depth-first rendering. | FR‑006, FR‑008, Contract §Behavior (connector expectations) |
| **F2** | Summary comments appear before descendants, giving “comment with children.” | `_apply_sorting_and_limits()` appends `_create_summary_comment()` to children list feeding BFS queue. Comments emitted before queue dequeues the folder they summarize. | FR‑007, Contract §Behavior |
| **F3** | Singular omission reported as `# 1 more folders`; UX expects either singular noun or direct rendering of the lone item. | `name=f"{count} more {noun}"` uses plural noun regardless of count; limit logic never promotes single remaining entries. | FR‑007 (per-directory summaries) |
| **F4** | `max_lines` stops mid-level, omitting siblings at same depth. | String/flat outputs slice `nodes_in_order[:limit]`; `limit_level` is ignored when rendering string/flat outputs. | FR‑007, Contract §Behavior (“finish current depth before stopping”) |
| **F5** | Existing tests/fixtures miss defects above. | Test suite lacks low `max_lines`, connector validation, summary ordering, and singular cases. | Tasks T030, T031; SC-criteria in spec |

## 5. Remediation Plan

### 5.1 Renderer & Traversal
1. Retain breadth-first traversal for limit computation but render ASCII via a depth-first serializer that walks the established `_TreeEntry` hierarchy recursively, calculating connectors in-context.
2. Recompute/propagate `is_last` flags inside the depth-first renderer (children sorted by final render order).

### 5.2 Summary Comment Semantics
1. Store summary counts as metadata rather than queue entries, or render them after child subtrees (e.g., track pending comments and emit once child recursion finishes).
2. Handle singular counts explicitly:
   - If only one entry exceeds the per-directory limit, render the entry (preferred) or output `# 1 more folder`.
   - Ensure comments never accumulate children; `items` stays `None`.

### 5.3 `max_lines` Compliance
1. Use `limit_level` to cap traversal depth instead of slicing output arrays:
   - Build nodes breadth-first as today.
   - Before rendering, prune the tree using `limit_level` so entire depths remain intact.
   - For flat outputs, filter nodes by `level <= limit_level` (plus any summaries if retained).

### 5.4 Documentation Updates
1. Update `file_tree()` docstring with corrected examples (showing depth-first ASCII and revised summary semantics).
2. If singular behaviour shifts to “render entry” rather than comment, reflect in `contracts/file_tree.md`.

### 5.5 Testing Enhancements
Add targeted cases:
1. `test_file_tree_string_depth_render()` – verifies ASCII connectors with multi-level tree (no stray leading `│`).
2. `test_file_tree_summary_comment_order()` – ensures comments render after child listings and never own children.
3. `test_file_tree_summary_comment_singular()` – confirms either singular grammar or rendering of the lone item.
4. `test_file_tree_max_lines_depth_finish()` – asserts string/flat/nested modes honour level completion when `max_lines` < number of level-one entries.

## 6. Post-Fix Verification Checklist
- Run enhanced pytest suite (`PYTHONPATH=. pytest ...`) ensuring new tests cover regressions.
- Manual spot-check using reproduction scripts above.
- Validate docstring/contract snippets compile and align with outputs.
- Confirm summary comments contain zero children and appear only after their folder’s listings.
- Verify singular grammar or item rendering meets UX decision.

## 7. Handoff Notes
- No schema changes required; `_TreeEntry` can remain dataclass.
- Refactor should avoid altering traversal ordering semantics beyond rendering & limit handling.
- Communicate final summary-comment decisions back into spec to keep documentation authoritative.

---

Prepared for follow-up implementation; provides reproduction commands, root causes, and actionable remediation to eliminate current defects without further clarification.
