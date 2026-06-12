## 2023-10-25 - Python String Split over regex split
**Learning:** Python's native `str.split()` automatically splits by consecutive whitespace and inherently drops empty strings. It bypasses regular expression compilation overhead and is heavily optimized in C, performing approximately 6x faster than `re.split(r'\s+', value)`.
**Action:** Always strictly prefer `value.split()` (with no arguments) for general whitespace tokenization instead of `re.split(r'\s+', value)` to maximize parsing speed and avoid redundant filtering operations.

## 2023-10-25 - Using walrus operator for redundant transforms
**Learning:** Redundant list comprehension filters and transforms (e.g., `[str(x).strip() for x in items if str(x).strip()]`) incur double function execution per valid item, wasting cycles on string allocation and stripping logic.
**Action:** Use Python 3.8+ walrus operator (`:=`) to capture the transformed output once: `[stripped for x in items if (stripped := str(x).strip())]`. This halves the method invocations and garbage allocations for validated elements.
