from fastapi import FastAPI
from app.auth import router as auth_router
from app.gmail_service import list_messages, get_message, parse_message

app = FastAPI()
app.include_router(auth_router)


@app.get("/")
def root():
    return {"status": "running"}


@app.get("/gmail/messages")
def gmail_messages():
    return list_messages(max_results=5)


@app.get("/gmail/messages/{message_id}")
def gmail_message(message_id: str):
    raw = get_message(message_id)
    return parse_message(raw)
