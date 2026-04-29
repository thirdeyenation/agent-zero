## 2024-04-29 - Prevent Timing Attacks in Token Validation
**Vulnerability:** Timing attack vulnerabilities found during token, API key, and password hash validations where standard string equality operators (`==`, `!=`) were used instead of constant-time comparison functions.
**Learning:** Attackers can potentially use timing differences to guess valid authentication tokens or API keys character by character when standard equality is used.
**Prevention:** Always use `secrets.compare_digest` (or `hmac.compare_digest`) for validating API keys, webhook secrets, CSRF tokens, and authentication hashes to prevent timing attacks. Additionally, ensure both arguments are strings using `isinstance(val, str)` to prevent `TypeError` exceptions.
