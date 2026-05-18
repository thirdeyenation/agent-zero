## 2024-05-24 - [Insecure Random Number Generation]
**Vulnerability:** Weak random number generation using `random.choices` for passwords and unique identifiers (e.g. root SSH password, user IDs, session IDs).
**Learning:** `random.choices` is not cryptographically secure and predictable. It should never be used for security-sensitive operations.
**Prevention:** Always use the `secrets` module (e.g. `secrets.choice`) for generating cryptographic or security-sensitive identifiers.
