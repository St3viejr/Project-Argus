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
# Database handler class to manage SQLite interactions (OOP style for better organization)


class DatabaseHandler:
    def __init__(self, db_name="alerts.db"):
        self.db_name = db_name

    def init_db(self):
        """Creates the events table if it doesn't already exist."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                camera_id TEXT,
                confidence REAL,
                timestamp TEXT,
                image_data TEXT,
                description TEXT 
            )
        """)
        conn.commit()
        conn.close()
        return True

    def insert_event(self, camera_id, confidence, timestamp, image_data, description):
        """Inserts a new threat event into the database."""
        conn = sqlite3.connect(self.db_name) 
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO events (camera_id, confidence, timestamp, image_data, description) 
            VALUES (?, ?, ?, ?, ?)""",
            (camera_id, confidence, timestamp, image_data, description))
        conn.commit()
        row_id = cursor.lastrowid
        conn.close()
        return row_id
        
    def get_event_count(self):
        """Returns the total number of alerts in the database."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM events")
        count = cursor.fetchone()[0]
        conn.close()
        return count