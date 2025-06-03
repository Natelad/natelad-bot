import sqlite3
from datetime import datetime
import json

DB = "chats.db"

def init_db():
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            role TEXT,
            message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')
        conn.commit()

def save_message(user_id, message, role):
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO messages (user_id, role, message) VALUES (?, ?, ?)",
                  (user_id, role, message))
        conn.commit()

def get_conversations(user_id=None):
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        if user_id:
            c.execute("SELECT id, user_id, role, message, timestamp FROM messages WHERE user_id = ? ORDER BY timestamp", (user_id,))
        else:
            c.execute("SELECT DISTINCT user_id FROM messages ORDER BY timestamp DESC")
        rows = c.fetchall()
    return rows

def get_messages(user_id):
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("SELECT role, message, timestamp FROM messages WHERE user_id = ? ORDER BY timestamp", (user_id,))
        rows = c.fetchall()
    messages = [{"role": role, "message": message, "timestamp": timestamp} for role, message, timestamp in rows]
    return json.dumps(messages)
