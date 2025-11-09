# Quickstart: File Tree Utility

## Overview
`file_tree()` in `python/helpers/files.py` renders a directory tree as:
- Multi-line ASCII string (`OUTPUT_MODE_STRING`)
- Flat list of items with metadata (`OUTPUT_MODE_FLAT`)
- Nested list where folders contain `items` arrays (`OUTPUT_MODE_NESTED`)

## Import
```python
from python.helpers.files import (
    file_tree,
    SORT_BY_NAME, SORT_BY_CREATED, SORT_BY_MODIFIED,
    SORT_ASC, SORT_DESC,
    OUTPUT_MODE_STRING, OUTPUT_MODE_FLAT, OUTPUT_MODE_NESTED,
)
```

## Examples

### 1) String mode (ASCII)
```python
tree_str = file_tree(
    relative_path="my_project",
    output_mode=OUTPUT_MODE_STRING,
    max_depth=0,
    max_lines=0,
    folders_first=True,
    sort=(SORT_BY_MODIFIED, SORT_DESC),
)
print(tree_str)
```
Sample output:
```text
my_project/
├── context_data.py
├── main.py
└── helpers/
    ├── api.py
    └── utils/
        ├── files.py
        └── strings.py
```

### 2) Flat mode (structured list)
```python
items = file_tree(
    relative_path="my_project",
    output_mode=OUTPUT_MODE_FLAT,
    max_depth=2,
    max_lines=200,
    folders_first=True,
    sort=(SORT_BY_NAME, SORT_ASC),
)

# Convert datetimes:
first = items[0]
iso_created = first["created"].isoformat()
ts_created = first["created"].timestamp()
```

### 3) Nested mode (hierarchical)
```python
nested = file_tree(
    relative_path="my_project",
    output_mode=OUTPUT_MODE_NESTED,
    max_depth=2,
    folders_first=True,
)
```

## Ignore Patterns
Inline patterns:
```python
ignore = \"\"\"\n*.pyc\n__pycache__/\n!important_file.py\n\"\"\"\n
items = file_tree(\"my_project\", output_mode=OUTPUT_MODE_FLAT, ignore=ignore)
```

From file (resolved as specified):
```python
# Absolute path
items = file_tree(\"my_project\", output_mode=OUTPUT_MODE_FLAT, ignore=\"file:/abs/path/.gitignore\")
# Absolute (URI form)
items = file_tree(\"my_project\", output_mode=OUTPUT_MODE_FLAT, ignore=\"file:///abs/path/.gitignore\")
# Relative to scan root
items = file_tree(\"my_project\", output_mode=OUTPUT_MODE_FLAT, ignore=\"file:.gitignore\")
items = file_tree(\"my_project\", output_mode=OUTPUT_MODE_FLAT, ignore=\"file://.gitignore\")
```

## Limits and Summaries
```python
tree_str = file_tree(
    relative_path=\"large_dir\",
    output_mode=OUTPUT_MODE_STRING,
    max_lines=200,
    max_folders=10,
    max_files=20,
)
```
When limits are hit within a directory, summary comment lines are emitted, e.g.:
```\n# 12 more files\n# 6 more folders\n```
