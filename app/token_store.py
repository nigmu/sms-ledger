import json
from pathlib import Path

TOKEN_FILE = Path("tokens.json")


def save_refresh_token(refresh_token: str):
    data = {
        "refresh_token": refresh_token
    }
    TOKEN_FILE.write_text(json.dumps(data))


def load_refresh_token() -> str | None:
    if not TOKEN_FILE.exists():
        return None
    data = json.loads(TOKEN_FILE.read_text())
    return data.get("refresh_token")
