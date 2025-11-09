# Data Model: File Tree Utility

## Entity: TreeItem

- `name: str` — filename or folder name (or comment label)
- `level: int` — depth level starting from 1 at root entries
- `type: \"file\" | \"folder\" | \"comment\"`
- `created: datetime` — timezone-aware UTC
- `modified: datetime` — timezone-aware UTC
- `text: str` — one-line rendered tree segment (e.g., `├── main.py`, `└── helpers/`, `# 6 more folders`)
- `items: list[TreeItem] | null` — present for folders in nested mode; empty or null for files and comments

### Example (flat item)
```json
{
  "name": "context_data.py",
  "level": 1,
  "type": "file",
  "created": "datetime (UTC-aware)",
  "modified": "datetime (UTC-aware)",
  "text": "├── context_data.py",
  "items": null
}
```

### Example (nested folder)
```json
{
  "name": "helpers",
  "level": 1,
  "type": "folder",
  "created": "datetime (UTC-aware)",
  "modified": "datetime (UTC-aware)",
  "text": "└── helpers/",
  "items": [
    {
      "name": "api.py",
      "level": 2,
      "type": "file",
      "created": "datetime (UTC-aware)",
      "modified": "datetime (UTC-aware)",
      "text": "    ├── api.py",
      "items": null
    }
  ]
}
```


