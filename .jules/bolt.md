## 2024-06-09 - Prefer native string methods over regex for simple tokenization
**Learning:** Python's native `str.split()` without arguments is heavily optimized in C and automatically handles consecutive whitespace sequences while discarding empties. Replacing `re.split(r'\s+', value)` with `str.split()` avoids regular expression compilation overhead and yields a ~6x performance improvement for basic tokenization.
**Action:** Always use `str.split()` instead of `re.split` when breaking strings by arbitrary whitespace.

## 2024-06-09 - Utilize walrus operator to prevent redundant operations in list comprehensions
**Learning:** In list comprehensions, computing an intermediate value for conditional checks (like `.strip()`) often leads to redundant function calls (e.g., `[x.strip() for x in items if x.strip()]`).
**Action:** Use the walrus operator (`:=`) introduced in Python 3.8 to compute and bind the result once: `[stripped for x in items if (stripped := x.strip())]`.
