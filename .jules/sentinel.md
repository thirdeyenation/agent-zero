## 2024-05-01 - Prevent Timing Attacks in Security Validations
**Vulnerability:** String comparison operators (`==` or `!=`) are used for validating authentication tokens, CSRF tokens, and API keys. This makes the application vulnerable to timing attacks.
**Learning:** Python's standard `==` operator fails fast on the first mismatched character. An attacker can use the difference in response time to guess tokens byte by byte.
**Prevention:** Always use `secrets.compare_digest` when comparing security-sensitive strings (like API keys, CSRF tokens, hashes) to ensure constant-time comparison, and check that both are strings before comparing.
