## 2024-07-08 - Optimize string splitting for simple delimiters
**Learning:** Native `str.replace().split()` and `str.split()` are vastly faster (~3-6x) than `re.split()` for simple multi-character delimiter tokenization (e.g., replacing '+' with ',' before splitting, or splitting on whitespace).
**Action:** Always prefer native string replacement and splitting combined with list comprehensions over `re.split()` when delimiter rules are basic, to avoid regex compilation and execution overhead in hot paths.
