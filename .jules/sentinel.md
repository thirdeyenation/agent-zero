## 2025-02-14 - Fix Weak Random Number Generation for Security Context
**Vulnerability:** The cryptographically weak `random.choices` function was being used to generate security-sensitive data, specifically a 32-character root password and several 8-character agent/context IDs.
**Learning:** This likely existed because `random` is the default go-to module for random data generation in Python, but it's not suitable for secrets or predictable identifiers where security is a concern.
**Prevention:** Always use the `secrets` module (e.g., `secrets.choice()`, `secrets.token_hex()`) instead of `random` when generating passwords, security tokens, session keys, or any data intended to be unpredictable and secure against cryptographic attacks.
