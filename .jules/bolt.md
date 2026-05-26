## 2024-05-26 - Optimize List Comprehensions with Walrus Operator
**Learning:** List comprehensions with redundant function calls (e.g., `[x.strip() for x in items if x.strip()]`) are a common anti-pattern that can be optimized using the walrus operator (`:=`) in Python 3.8+ to compute and bind the result once (e.g., `[stripped for x in items if (stripped := x.strip())]`).
**Action:** Always use the walrus operator when filtering and mapping list elements simultaneously to avoid redundant calculations.
