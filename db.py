import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path("natelad.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        phone TEXT PRIMARY KEY,
        username TEXT,
        assigned_agent TEXT,
        is_human_takeover INTEGER DEFAULT 0,
        created_at TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phone TEXT NOT NULL,
        sender TEXT NOT NULL,          -- 'user' | 'bot' | 'human'
        msg_type TEXT NOT NULL,        -- text|image|video|document|interactive|unknown
        text TEXT,
        media_path TEXT,
        mime_type TEXT,
        wa_message_id TEXT,
        ts TEXT
    )
    """)

    conn.commit()
    conn.close()


def upsert_user(phone: str, username: str | None = None):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT phone FROM users WHERE phone=?", (phone,))
    exists = cur.fetchone()

    if exists:
        if username:
            cur.execute("UPDATE users SET username=? WHERE phone=?", (username, phone))
    else:
        cur.execute(
            "INSERT INTO users(phone, username, created_at) VALUES (?,?,?)",
            (phone, username, datetime.utcnow().isoformat())
        )

    conn.commit()
    conn.close()


def get_user(phone: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE phone=?", (phone,))
    row = cur.fetchone()
    conn.close()
    return row


def set_username(phone: str, username: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE users SET username=? WHERE phone=?", (username, phone))
    conn.commit()
    conn.close()


def set_takeover(phone: str, takeover: bool):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE users SET is_human_takeover=? WHERE phone=?", (1 if takeover else 0, phone))
    conn.commit()
    conn.close()


def is_takeover(phone: str) -> bool:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT is_human_takeover FROM users WHERE phone=?", (phone,))
    row = cur.fetchone()
    conn.close()
    return bool(row and row["is_human_takeover"] == 1)


def save_message(phone, sender, msg_type, text=None, media_path=None, mime_type=None, wa_message_id=None):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO messages(phone, sender, msg_type, text, media_path, mime_type, wa_message_id, ts)
    VALUES(?,?,?,?,?,?,?,?)
    """, (phone, sender, msg_type, text, media_path, mime_type, wa_message_id, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()


def list_conversations(limit=100):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    SELECT u.phone, u.username, u.is_human_takeover,
           (SELECT COALESCE(text,'') FROM messages m WHERE m.phone=u.phone ORDER BY m.id DESC LIMIT 1) AS last_text,
           (SELECT ts FROM messages m WHERE m.phone=u.phone ORDER BY m.id DESC LIMIT 1) AS last_ts
    FROM users u
    ORDER BY COALESCE(last_ts, u.created_at) DESC
    LIMIT ?
    """, (limit,))
    rows = cur.fetchall()
    conn.close()
    return rows


def get_messages(phone, limit=300):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    SELECT * FROM messages
    WHERE phone=?
    ORDER BY id DESC
    LIMIT ?
    """, (phone, limit))
    rows = cur.fetchall()
    conn.close()
    return list(reversed(rows))


def get_recent_history_for_ai(phone: str, limit=20):
    """
    Returns a compact history list (oldest->newest) of dicts:
    [{"role":"user"|"model", "parts":[text]}]
    """
    msgs = get_messages(phone, limit=limit)
    history = []

    for m in msgs:
        sender = m["sender"]
        text = (m["text"] or "").strip()

        # Only feed text content to the model (skip raw media bytes)
        if not text:
            continue

        if sender == "user":
            history.append({"role": "user", "parts": [text]})
        else:
            # bot + human = assistant side
            history.append({"role": "model", "parts": [text]})

    return history[-limit:]
