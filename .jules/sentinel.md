## 2024-06-25 - Weak random number generation
**Vulnerability:** Weak random number generation using `random.choices` for generating passwords and internal identifiers.
**Learning:** `random.choices` is a pseudo-random number generator that is not cryptographically secure, and should not be used in security-sensitive contexts like generating passwords.
**Prevention:** Use `secrets.choice` or `secrets.token_urlsafe` for generating random strings or passwords.
