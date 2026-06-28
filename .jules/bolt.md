## 2025-02-27 - Native String Split Performance
**Learning:** For basic whitespace tokenization, native `str.split()` is vastly faster (~4-6x) than `re.split(r'\s+', value)`. The native method automatically handles consecutive whitespace and drops empty tokens, avoiding regex compilation overhead and the need for redundant `if item` filtering.
**Action:** Always prefer native `str.split()` over regex splitting when delimiter rules are just basic whitespace, especially in hot paths.
