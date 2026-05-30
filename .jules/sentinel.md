## 2024-05-24 - Insecure Random String Generation

**Vulnerability:** Found the use of Python's built-in `random` module (`random.choices`) being used to generate sensitive data, specifically the root SSH password in `prepare.py` and internal system identifiers in `agent.py` and `helpers/guids.py`.

**Learning:** Developers frequently use `random` because it's familiar and convenient (e.g., `random.choices` accepts a `k` argument for length). However, the standard `random` module uses the Mersenne Twister, a deterministic PRNG designed for simulations, not security. Its outputs are entirely predictable if a small sample of prior outputs is known, making generated passwords or session tokens vulnerable to brute-force or prediction attacks.

**Prevention:** For any security-sensitive context (passwords, tokens, system IDs, session keys), always use the `secrets` module, which relies on the operating system's cryptographically secure pseudo-random number generator (CSPRNG, like `/dev/urandom`). Note that `secrets.choice()` does not have a `k` argument, so it must be implemented via a generator expression: `"".join(secrets.choice(chars) for _ in range(length))`.
