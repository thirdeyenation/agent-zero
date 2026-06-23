## 2024-06-23 - Predictable Randomness

**Vulnerability:** Weak random number generation using the `random` module for security-sensitive contexts (tokens, identifiers, passwords).
**Learning:** The `random` module uses a pseudo-random number generator, making it predictable. Security contexts require cryptographically secure generation.
**Prevention:** Always use the `secrets` module for generating tokens, passwords, or cryptographic identifiers. Specifically, use `secrets.randbelow()` instead of `random.randint()`, and `"".join(secrets.choice(chars) for _ in range(n))` instead of `"".join(random.choices(chars, k=n))`.
