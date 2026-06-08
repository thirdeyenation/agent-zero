## 2024-06-08 - Fixed weak random number generation
**Vulnerability:** Weak random number generators `random.choices` and `random.randint` were being used to generate security-critical identifiers such as `root_pass`, agent IDs, and scheduler tokens.
**Learning:** `random` module uses the Mersenne Twister PRNG, which is deterministic and predictable. Predictable IDs or tokens could allow attackers to bypass security layers.
**Prevention:** Always use the `secrets` module (`secrets.choice`, `secrets.randbelow`, `secrets.token_hex`) for generating secure random strings or numbers in security-sensitive contexts.
