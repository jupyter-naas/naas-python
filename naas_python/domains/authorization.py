import os
from pathlib import Path


def write_token_to_file(token: str):
    credentials_dir = Path.home() / ".naas"
    credentials_dir.mkdir(parents=True, exist_ok=True)

    credentials_file = credentials_dir / "credentials"
    with open(credentials_file, "w") as f:
        f.write(f"NAAS_TOKEN={token}")


def load_token_from_file() -> str:
    credentials_file = Path.home() / ".naas" / "credentials"
    if not credentials_file.exists():
        raise FileNotFoundError("Missing NAAS credentials file")

    with open(credentials_file, "r") as f:
        for line in f:
            if line.startswith("NAAS_TOKEN="):
                token = line.strip().split("=")[1]

    if not token:
        raise ValueError("File exists but does not contain a valid NAAS token")

    return token
