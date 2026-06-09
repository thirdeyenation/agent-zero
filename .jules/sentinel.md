## 2024-06-09 - Insecure Random Number Generation
**Vulnerability:** The standard `random` module was used to generate security-sensitive tokens, passwords, and IDs (e.g. `root_pass`, authentication tokens).
**Learning:** `random` is predictable and not cryptographically secure, which allows attackers to potentially guess generated sensitive values.
**Prevention:** Use the `secrets` module (`secrets.choice`, `secrets.randbelow`) for all security-sensitive random value generation instead of `random`.
