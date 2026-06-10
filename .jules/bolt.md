## 2025-03-08 - Fast String Tokenization
**Learning:** Python's built-in `str.split()` method (without arguments) is significantly faster (~10x) for tokenizing consecutive whitespace compared to `re.split(r"\s+", value)`. `str.split()` bypasses regex compilation and execution overhead and naturally handles discarding empty strings.
**Action:** Always prefer `str.split()` over `re.split` for simple whitespace tokenization in Python scripts.
