## YYYY-MM-DD - [Title]
**Learning:** [Insight]
**Action:** [How to apply next time]
## 2026-04-29 - Optimize path containment checks in `is_in_dir`
**Learning:** `os.path.commonpath` can be a significant bottleneck due to internal list allocations and path splitting.
**Action:** For path containment checks, use `os.path.abspath` and `str.startswith()`. Ensure a trailing `os.sep` is appended to the absolute directory before comparison to prevent path traversal bugs (e.g., preventing `/app/database` from matching `/app/data`).
