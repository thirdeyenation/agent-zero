## $(date +%Y-%m-%d) - Optimize character search in dirty_json parser
**Learning:** List comprehensions that execute O(N) operations like `str.find()` multiple times per element (e.g., both in the condition and the value assignment) create significant hidden performance bottlenecks, doubling the execution time for large strings.
**Action:** Always use the walrus operator (`:=`) in Python 3.8+ list comprehensions when filtering and mapping based on the same function call to halve redundant execution time.
