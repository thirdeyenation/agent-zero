## 2024-10-25 - Prevent Insecure Randomness for Tokens and Passwords
**Vulnerability:** The application used `random.choices` and `random.randint` from the standard `random` module to generate sensitive IDs, root passwords, and security tokens. The `random` module is predictable and not cryptographically secure, which could allow an attacker to predict generated secrets.
**Learning:** Found multiple instances where random number generators were used where cryptographically secure generators were required, highlighting a gap in secure randomness practices in the codebase.
**Prevention:** Always use the `secrets` module (`secrets.choice` or `secrets.randbelow`) for generating any value used in a security-sensitive context like identifiers, passwords, or authentication tokens.
