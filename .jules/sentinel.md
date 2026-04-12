
## $(date +%Y-%m-%d) - Prevent Timing Attacks in Authentication
**Vulnerability:** String comparisons for credentials (`login_handler` in `helpers/ui_server.py`) and hashes (`verify_data` in `helpers/crypto.py`) used the `==` operator. This exposes the application to timing attacks, where an attacker can deduce correct characters based on response times.
**Learning:** Python's `==` operator for strings short-circuits upon the first mismatch. For security-sensitive data like passwords, API keys, and hashes, this leakage of timing information is a known vulnerability.
**Prevention:** Always use `secrets.compare_digest` or `hmac.compare_digest` for validating secrets. Ensure both arguments are strictly strings or bytes (e.g., check `isinstance(val, str)` and handle missing data) before comparison to prevent `TypeError` or logical bypasses.
