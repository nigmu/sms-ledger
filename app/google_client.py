import json
import requests
import os
from app.token_store import load_refresh_token

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_FILE = os.path.join(BASE_DIR, "google_credentials.json")

TOKEN_URI = "https://oauth2.googleapis.com/token"


def _load_client_credentials():
    data = json.loads(open(CREDENTIALS_FILE).read())
    client = data["web"]
    return client["client_id"], client["client_secret"]


def get_access_token() -> str:
    refresh_token = load_refresh_token()
    if not refresh_token:
        raise RuntimeError("No refresh token stored. Run OAuth first.")

    client_id, client_secret = _load_client_credentials()

    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }

    r = requests.post(TOKEN_URI, data=payload)
    r.raise_for_status()

    return r.json()["access_token"]


def fetch_gmail_profile():
    access_token = get_access_token()

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    r = requests.get(
        "https://gmail.googleapis.com/gmail/v1/users/me/profile",
        headers=headers
    )
    r.raise_for_status()
    return r.json()
