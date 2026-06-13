## 2024-05-24 - Optimize whitespace tokenization
**Learning:** `re.split(r'\s+', value)` is unoptimized for basic whitespace splitting. Using `str.split()` (without arguments) is much faster since it's highly optimized in C and naturally discards empty string elements, making subsequent filters redundant.
**Action:** Always prefer native `str.split()` for whitespace tokenization over regex, especially in parsing loops.
