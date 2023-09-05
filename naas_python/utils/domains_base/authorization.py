import os
from dataclasses import dataclass


@dataclass
class NAASCredentials:
    token: str


def write_token_to_file(token: str):
    credentials_dir = os.path.expanduser("~/.naas")
    os.makedirs(credentials_dir, exist_ok=True)

    with open(os.path.join(credentials_dir, "credentials"), "w") as f:
        f.write(f"NAAS_TOKEN={token}")


def load_token_from_file() -> str:
    with open("~/.naas/credentials", "r") as f:
        for line in f:
            if line.startswith("NAAS_TOKEN="):
                return line.strip().split("=")[1]

    return ""  # File exists but does not contain a valid token
