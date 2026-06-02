## 2025-02-28 - Avoid regex for simple whitespace splitting
**Learning:** Using `re.split(r"\s+", value)` for simple whitespace tokenization is significantly slower (approx 6x slower compilation/execution overhead in tight loops) than using Python's heavily optimized native `str.split()`.
**Action:** Strictly prefer native `str.split()` over `re.split` for tokenizing whitespace strings.
