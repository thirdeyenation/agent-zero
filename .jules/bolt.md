## 2024-07-01 - Native String Splitting vs Regex
**Learning:** Native `str.replace().split()` is ~3-6x faster than `re.split()` for simple multi-character delimiter tokenization, and `str.split()` is ~10x faster than `re.split(r"\s+", ...)` because they avoid regex compilation and execution overhead in hot paths.
**Action:** Always prefer native string replacement and splitting (sometimes combined with list comprehensions) over `re.split()` when delimiter rules are basic.
