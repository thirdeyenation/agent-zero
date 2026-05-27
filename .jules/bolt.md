
## 2024-05-24 - Optimize list comprehensions with walrus operator
 **Learning:** List comprehensions with redundant function calls (like `input_str.find(char)`) cause the function to be evaluated twice, which is an anti-pattern that slows down processing, especially for O(n) string scanning.
 **Action:** Use the Python 3.8+ walrus operator (`:=`) to compute and bind the result once, e.g., `[idx for char in chars if (idx := input_str.find(char)) != -1]`.
