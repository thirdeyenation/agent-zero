## 2024-05-01 - Fix Timing Attacks in Authentication
**Vulnerability:** Timing attacks on token, hash, and API key comparisons via standard string equality checks (`==` / `!=`).
**Learning:** Always use `secrets.compare_digest` for security-sensitive comparisons to prevent timing attacks.
**Prevention:** Use `secrets.compare_digest` with explicit `isinstance(val, str)` type checks to safely handle `None` and non-string inputs.
