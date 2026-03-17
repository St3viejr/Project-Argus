import sqlite3

DB_NAME = "alerts.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            camera_id TEXT,
            confidence REAL,
            timestamp TEXT
        )
    """)

    conn.commit()
    conn.close()


def insert_event(payload):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO events (camera_id, confidence, timestamp)
        VALUES (?, ?, ?)
    """, (
        payload.camera_ID,
        payload.confidence,
        str(payload.timestamp)
    ))

    conn.commit()
    conn.close()