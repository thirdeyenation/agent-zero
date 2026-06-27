## 2026-03-25 - Optimize tokenization with native string methods
**Learning:** Native `str.split()` and combined `.replace().split()` are significantly faster (~3-6x) than `re.split()` for simple whitespace or multi-character delimiter tokenization, avoiding regex compilation overhead in hot paths. `str.split()` is heavily optimized in C and naturally drops empty strings, eliminating the need for subsequent list comprehension filtering.
**Action:** Always prefer native string replacement and splitting for basic delimiter rules over regex for measurable performance gains in tokenization tasks.
