from fastapi import FastAPI, Request
from datetime import datetime
import json

app = FastAPI()

@app.post("/webhook/sms")
async def sms_webhook(request: Request):
    body = await request.json()

    # raw payload
    event = body.get("event")
    payload = body.get("payload", {})

    record = {
        "event": event,
        "message_id": payload.get("messageId"),
        "message": payload.get("message"),
        "phone": payload.get("phoneNumber"),
        "sim": payload.get("simNumber"),
        "received_at": payload.get("receivedAt"),
        "ingested_at": datetime.utcnow().isoformat()
    }

    # Example: append to file (replace with DB later)
    with open("sms_log.jsonl", "a") as f:
        f.write(json.dumps(record) + "\n")

    return {"status": "ok"}
