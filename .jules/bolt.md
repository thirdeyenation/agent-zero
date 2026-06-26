## 2024-06-26 - Native String Operations Over Regex for Tokenization
**Learning:** For basic whitespace or simple delimiter tokenization (e.g. `\s+` or `\s*\+\s*|\s*,\s*`), using native string methods like `.split()` and `.replace()` is vastly faster (~3-8x) than `re.split()`. Native `str.split()` avoids regex compilation overhead and handles consecutive whitespace out-of-the-box.
**Action:** Always prefer native string replacement and splitting combined with list comprehensions over `re.split()` when delimiter rules are basic, avoiding regex overhead in hot paths.
