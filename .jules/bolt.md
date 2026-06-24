## 2025-06-24 - Basic string splitting optimizations
**Learning:** Native `str.split()` or `replace().split()` is vastly faster (~3-6x) than `re.split()` for simple delimiter tokenization (whitespace, basic punctuation) in Python. `re.split()` carries compilation and execution overhead not suitable for frequent hot paths like data normalizers or parsers.
**Action:** Always prefer `str.split()` combined with list comprehensions or `replace()` over `re.split()` when the delimiter rules are basic, especially in hot paths like query parsing, data normalizers, or input formatters.
