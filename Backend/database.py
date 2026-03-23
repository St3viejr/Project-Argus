import sqlite3

'''This module handles all interactions with the SQLite database for storing event data.

Functionality:
    -Provides functions to initialize the database and insert new events.

    -database schema includes fields for camera ID, confidence level, 
    timestamp, and image data (stored as a base64 string).

    -The init_db function creates the events table if it doesn't already exist, 
    while the insert_event function takes an event payload and inserts it into the database. 
    Make sure to adjust the database path as needed for your environment(but should be fine as is).
'''


DB_NAME = "alerts.db"


def init_db():
    conn = sqlite3.connect("alerts.db")
    cursor = conn.cursor()
    # Added image_data TEXT to the table definition
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            camera_id TEXT,
            confidence REAL,
            timestamp TEXT,
            image_data TEXT  
        )
    """)
    conn.commit()
    conn.close()

def insert_event(payload):
    conn = sqlite3.connect("alerts.db") 
    cursor = conn.cursor()
    
    # pull the data directly from the payload object
    cursor.execute(
        """INSERT INTO events (camera_id, confidence, timestamp, image_data) 
        VALUES (?, ?, ?, ?)""",
        (payload.camera_ID, payload.confidence, str(payload.timestamp), payload.image_data)
    )
    
    conn.commit()
    conn.close()