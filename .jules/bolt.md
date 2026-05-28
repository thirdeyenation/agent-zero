## 2024-05-18 - Replacing `re.split` with native `str.split()`
**Learning:** Native `str.split()` with no arguments automatically splits on arbitrary whitespace and is heavily optimized in C, performing ~6x faster than `re.split(r"\s+", value)` and inherently stripping empty tokens.
**Action:** Always prefer `str.split()` over `re.split` for basic whitespace tokenization unless complex regex matching is strictly required.
