## 2024-07-03 - Optimize string splitting
**Learning:** Native `str.split()` and `.replace()` are significantly faster (2.5x - 6x) than `re.split()` for simple character delimiter tokenization in Python, avoiding regex compilation and execution overhead in hot paths.
**Action:** Use native string methods combined with list comprehensions instead of `re.split()` when delimiter rules are basic.
