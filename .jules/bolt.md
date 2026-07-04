## 2024-07-04 - Native String Operations Are Faster Than Regex For Simple Delimiters
**Learning:** In Python, using `re.split` for simple multi-character delimiter splitting (like whitespace or basic formatting `\s*\+\s*|\s*,\s*`) incurs significant regex compilation and execution overhead compared to native string methods.
**Action:** When delimiter rules are basic, use a combination of `.replace()`, `.split()`, and list comprehensions to tokenize strings instead of `re.split`. This provides a massive performance improvement (e.g. ~5-6x speedup for basic splits).
