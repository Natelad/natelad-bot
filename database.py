import sqlite3

def init_db():
    with sqlite3.connect("chatlogs.db") as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_number TEXT NOT NULL,
                sender TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)

def log_message(user_number, sender, message):
    with sqlite3.connect("chatlogs.db") as conn:
        conn.execute(
            "INSERT INTO messages (user_number, sender, message) VALUES (?, ?, ?)",
            (user_number, sender, message)
        )

def get_all_conversations():
    with sqlite3.connect("chatlogs.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_number, sender, message, timestamp FROM messages ORDER BY timestamp ASC")
        return cursor.fetchall()
