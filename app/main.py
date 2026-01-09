from fastapi import FastAPI, Request
from datetime import datetime
import json

app = FastAPI()
SEEN = set()

@app.post("/webhook/sms")
async def sms_webhook(request: Request):
    raw = await request.body()
    if not raw:
        return {"status": "ignored"}

    body = json.loads(raw)
    payload = body.get("payload", {})
    msg_id = payload.get("messageId")

    if msg_id in SEEN:
        return {"status": "duplicate"}

    SEEN.add(msg_id)

    record = {
        "event": body.get("event"),
        "message_id": msg_id,
        "message": payload.get("message"),
        "phone": payload.get("phoneNumber"),
        "sim": payload.get("simNumber"),
        "received_at": payload.get("receivedAt"),
        "ingested_at": datetime.utcnow().isoformat()
    }

    with open("sms_log.jsonl", "a") as f:
        f.write(json.dumps(record) + "\n")

    return {"status": "ok"}

