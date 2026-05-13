## 2024-05-18 - [Optimize path containment checks]
**Learning:** Using `os.path.commonpath` for path containment checks is a significant bottleneck due to internal list allocations and path splitting.
**Action:** Use `os.path.abspath` combined with `str.startswith()` and a conditionally appended `os.sep` to prevent path traversal bugs while being significantly faster.
