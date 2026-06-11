## 2024-06-11 - Optimize string splitting and list comprehensions
**Learning:** For basic whitespace tokenization in Python, native `str.split()` is significantly faster (~7x) than `re.split(r"\s+", value)` and avoids regex compilation overhead. Additionally, using the walrus operator `:=` in list comprehensions avoids redundant function calls (like `.strip()`).
**Action:** Strictly prefer native `str.split()` over `re.split` for simple whitespace separation, and use the walrus operator in Python 3.8+ to bind and reuse computed values in comprehensions.
