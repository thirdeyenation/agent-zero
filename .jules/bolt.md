
## 2024-04-13 - Regex Optimization in strings.py
**Learning:** `str.isalnum()` checks in Python character-by-character loops are slower compared to using compiled regex substitutions (`re.compile(r'[^\w]|_')`). Also `isalnum()` is Unicode-aware so matching non-alphanumeric via ASCII regex `[^a-zA-Z0-9]` leads to regression with international characters.
**Action:** When refactoring string builders, compile regular expressions and use `[^\w]|_` to maintain Unicode awareness while improving performance significantly.
