## 2024-05-18 - Insecure Random Number Generation for Security Contexts
**Vulnerability:** The codebase was using the non-cryptographic `random.choices()` to generate root passwords and internal identifiers.
**Learning:** Python's built-in `random` module produces predictable sequences which can be guessed or reverse-engineered by an attacker, leading to unauthorized access.
**Prevention:** Always use the `secrets` module (e.g., `secrets.choice()`) when generating random data for security-sensitive contexts like passwords, tokens, or session IDs.
