## 2025-07-05 - Optimize whitespace tokenization
**Learning:** Native `str.split()` (with no arguments) is vastly faster (~9x) than `re.split(r'\s+', value)` for simple whitespace tokenization in Python. It automatically handles consecutive whitespace, inherently drops empty strings, and avoids regex compilation overhead.
**Action:** Always prefer native `str.split()` over `re.split()` when delimiter rules are basic whitespace, to avoid unnecessary regex compilation and execution overhead in hot paths.
