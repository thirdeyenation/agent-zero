## 2025-07-07 - Native String Splitting is Faster Than re.split
 **Learning:** Native string replacements combined with list comprehensions (e.g., `[k.strip() for k in keys.replace('+', ',').split(',')]`) are ~3x faster than `re.split` for simple multi-character delimiter tokenization in hot paths.
 **Action:** Always prefer native string replacement and splitting over `re.split()` when delimiter rules are basic, to avoid regex compilation and execution overhead.
