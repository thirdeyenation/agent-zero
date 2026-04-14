## 2024-05-18 - Prevent timing attacks with constant-time comparison
**Vulnerability:** API keys, CSRF tokens, and authentication hashes were compared using standard equality operators (`==`, `!=`), which are susceptible to timing attacks. This could allow attackers to guess secrets by observing comparison times.
**Learning:** Python string comparison operators (`==`, `!=`) short-circuit, causing the comparison time to vary based on the number of matching characters from the start.
**Prevention:** Always use `secrets.compare_digest` or `hmac.compare_digest` for validating security tokens, ensuring both arguments are strictly instances of strings or bytes to prevent TypeErrors when `None` is provided.
