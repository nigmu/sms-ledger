import base64
import requests
from app.google_client import get_access_token


GMAIL_API_BASE = "https://gmail.googleapis.com/gmail/v1"


def _auth_headers():
    token = get_access_token()
    return {"Authorization": f"Bearer {token}"}


def list_messages(max_results: int = 10):
    url = f"{GMAIL_API_BASE}/users/me/messages"
    params = {"maxResults": max_results}

    r = requests.get(url, headers=_auth_headers(), params=params)
    r.raise_for_status()

    return r.json().get("messages", [])


def get_message(message_id: str):
    url = f"{GMAIL_API_BASE}/users/me/messages/{message_id}"
    params = {"format": "full"}

    r = requests.get(url, headers=_auth_headers(), params=params)
    r.raise_for_status()

    return r.json()


def _decode_base64(data: str) -> str:
    missing_padding = len(data) % 4
    if missing_padding:
        data += "=" * (4 - missing_padding)
    return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")


def extract_headers(payload: dict):
    headers = {}
    for h in payload.get("headers", []):
        headers[h["name"]] = h["value"]
    return headers


def extract_body(payload: dict) -> str:
    if "body" in payload and payload["body"].get("data"):
        return _decode_base64(payload["body"]["data"])

    for part in payload.get("parts", []):
        if part.get("mimeType") == "text/plain":
            return _decode_base64(part["body"].get("data", ""))

    return ""


def parse_message(message: dict):
    payload = message.get("payload", {})
    headers = extract_headers(payload)
    body = extract_body(payload)

    return {
        "id": message.get("id"),
        "threadId": message.get("threadId"),
        "from": headers.get("From"),
        "to": headers.get("To"),
        "subject": headers.get("Subject"),
        "date": headers.get("Date"),
        "body": body,
    }
