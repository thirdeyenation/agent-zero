## 2025-02-18 - Native String Methods vs Regex
**Learning:** Native string methods like `.split()` and `.replace().split()` are vastly faster (3-5x) than `re.split()` for simple tokenization tasks in Python due to the overhead of regular expression compilation and execution.
**Action:** Always prefer native string operations over regex when splitting on arbitrary whitespace or simple multi-character delimiters. Use `.split()` with no arguments to aggressively strip whitespace, and use list comprehensions with `.strip()` for multiple delimiters.
