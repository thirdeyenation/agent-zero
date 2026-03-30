### text_editor
read write or patch text files; binary files are not supported
always use the method form in `tool_name`; never send bare `text_editor`
- `text_editor:read`: `path`, optional `line_from`, `line_to`
- `text_editor:write`: `path`, `content`
- `text_editor:patch`: `path`, `edits[]`
example:
~~~json
{
  "thoughts": ["Need to inspect the file before patching it."],
  "headline": "Reading file with text editor",
  "tool_name": "text_editor:read",
  "tool_args": {
    "path": "/path/file.py",
    "line_from": 1,
    "line_to": 50
  }
}
~~~
patch edit format: `{from,to?,content?}`
- omit `to` to insert before `from`
- omit `content` to delete
- line numbers come from the last read
- avoid overlapping edits; re-read after insert delete or other line shifts
