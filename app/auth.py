import os
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from app.token_store import save_refresh_token

router = APIRouter()

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly"
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_SECRET_FILE = os.path.join(BASE_DIR, "google_credentials.json")

REDIRECT_URI = "http://localhost:8000/auth/google/callback"


def build_flow(state: str | None = None):
    return Flow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
        state=state
    )


@router.get("/auth/google/login")
def google_login():
    flow = build_flow()
    auth_url, state = flow.authorization_url(
        access_type="offline",
        prompt="consent",
        include_granted_scopes="true"
    )
    return RedirectResponse(auth_url)


@router.get("/auth/google/callback")
def google_callback(request: Request):
    code = request.query_params.get("code")
    state = request.query_params.get("state")

    if not code:
        return {"error": "Missing authorization code"}

    flow = build_flow(state=state)
    flow.fetch_token(code=code)

    credentials = flow.credentials

    if credentials.refresh_token:
        save_refresh_token(credentials.refresh_token)

    return {
        "message": "OAuth successful. Refresh token stored."
    }
