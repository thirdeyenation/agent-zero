## 2024-06-08 - String Parsing Performance

**Learning:** When splitting strings by whitespace in Python, `str.split()` (without arguments) is significantly faster (~6x) than using `re.split(r'\s+', string)`. This is because `str.split()` automatically handles consecutive whitespace and avoids regular expression compilation and matching overhead. Also, list comprehensions with redundant function calls (like `.strip()`) can be optimized using the walrus operator `:=`.
**Action:** Replace `re.split(r'\s+', ...)` with `.split()` whenever basic whitespace tokenization is needed. Use the walrus operator to prevent repeated string operations inside comprehensions.
