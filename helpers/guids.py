import random, string, secrets

def generate_id(length: int = 8) -> str:
    return "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))
