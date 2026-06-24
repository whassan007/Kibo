import os
from pathlib import Path
from sqlite3 import Connection, connect

DB_PATH = Path(__file__).parent / "calendar_sync.db"

def get_connection() -> Connection:
    conn = connect(str(DB_PATH))
    conn.row_factory = lambda cursor, row: {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()
    # Table to track calendar pushes
    c.execute('''
        CREATE TABLE IF NOT EXISTS calendar_pushes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            task_id TEXT NOT NULL,
            provider TEXT NOT NULL,
            event_id TEXT,
            title TEXT,
            start TEXT,
            end TEXT,
            description TEXT,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Table to store encrypted tokens per user/provider
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            provider TEXT NOT NULL,
            encrypted_token BLOB NOT NULL,
            UNIQUE(user_id, provider)
        )
    ''')
    conn.commit()
    conn.close()

# Initialize on import
if not DB_PATH.exists():
    init_db()
else:
    # Ensure tables exist even if DB file present
    init_db()
