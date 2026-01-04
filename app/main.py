from fastapi import FastAPI, Request, HTTPException
from datetime import datetime
import json

app = FastAPI()

@app.post("/webhook/sms")
async def sms_webhook(request: Request):
    raw = await request.body()

    if not raw:
        # harmless empty POST (health checks, probes, noise)
        return {"status": "ignored", "reason": "empty body"}

    try:
        body = json.loads(raw)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

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

    with open("sms_log.jsonl", "a") as f:
        f.write(json.dumps(record) + "\n")

    return {"status": "ok"}
