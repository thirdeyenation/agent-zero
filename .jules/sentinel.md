## 2024-05-18 - Weak Random Generation in IDs
**Vulnerability:** The codebase was using the standard `random` module for generating session tokens and identifiers (`helpers/guids.py`).
**Learning:** The `random` module is not cryptographically secure and predictable, which could compromise generated IDs.
**Prevention:** Always use the `secrets` module (e.g., `secrets.choice`) for generating random strings where security or unpredictability is needed.
