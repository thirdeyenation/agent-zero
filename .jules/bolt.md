## 2024-05-15 - Fast Whitespace Tokenization
**Learning:** `re.split(r"\s+", value)` is significantly slower (~6x) than the heavily-optimized native `str.split()` method in Python. `str.split()` handles multiple spaces seamlessly and automatically drops empty strings.
**Action:** Always prefer `str.split()` over regex splitting for basic whitespace tokenization.

## 2024-05-15 - List Comprehension Walrus Optimization
**Learning:** Doing `[str(v).strip() for v in value if str(v).strip()]` recalculates `str(v).strip()` twice per element.
**Action:** Use Python 3.8+ walrus operator `[stripped for v in value if (stripped := str(v).strip())]` to calculate the condition once and use the result, drastically reducing redundant function calls and yielding roughly a 2x speedup on iterations.
