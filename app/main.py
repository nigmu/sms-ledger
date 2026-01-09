from fastapi import FastAPI, Request
from datetime import datetime
import sqlite3
from pathlib import Path

app = FastAPI(title="SMS Ledger")

DB_PATH = Path("sms.db")

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS sms (
            message_id TEXT PRIMARY KEY,
            phone TEXT,
            message TEXT,
            sim INTEGER,
            received_at TEXT,
            ingested_at TEXT
        )
        """)

@app.on_event("startup")
def startup():
    init_db()

@app.post("/webhook/sms")
async def sms_webhook(request: Request):
    body = await request.json()
    payload = body.get("payload", {})

    record = (
        payload.get("messageId"),
        payload.get("phoneNumber"),
        payload.get("message"),
        payload.get("simNumber"),
        payload.get("receivedAt"),
        datetime.utcnow().isoformat(),
    )

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT OR IGNORE INTO sms
            (message_id, phone, message, sim, received_at, ingested_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, record)

    return {"status": "ok"}

@app.get("/stats")
def stats():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM sms")
        total = cur.fetchone()[0]
    return {"total_messages": total}

@app.get("/")
def health():
    return {"status": "ok"}
