import sqlite3
from datetime import datetime
from pathlib import Path
from .config import DATABASE_MODE, SQLITE_PATH, MONGO_URI, MONGO_DB

class EventStore:
    def __init__(self):
        self.mode = DATABASE_MODE
        self.mongo = None
        self.collection = None

        if self.mode == "mongodb":
            try:
                from pymongo import MongoClient
                self.mongo = MongoClient(MONGO_URI, serverSelectionTimeoutMS=1500)
                self.mongo.admin.command("ping")
                self.collection = self.mongo[MONGO_DB]["events"]
            except Exception:
                self.mode = "sqlite"

        if self.mode == "sqlite":
            Path(SQLITE_PATH).parent.mkdir(parents=True, exist_ok=True)
            with sqlite3.connect(SQLITE_PATH) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        event_type TEXT NOT NULL,
                        object_type TEXT,
                        confidence REAL,
                        message TEXT,
                        timestamp TEXT NOT NULL
                    )
                """)
                conn.commit()

    def add(self, event_type, object_type, confidence, message):
        timestamp = datetime.utcnow().isoformat(timespec="seconds") + "Z"
        if self.mode == "mongodb":
            result = self.collection.insert_one({
                "event_type": event_type,
                "object_type": object_type,
                "confidence": confidence,
                "message": message,
                "timestamp": timestamp
            })
            return str(result.inserted_id)

        with sqlite3.connect(SQLITE_PATH) as conn:
            cur = conn.execute(
                "INSERT INTO events(event_type, object_type, confidence, message, timestamp) VALUES(?,?,?,?,?)",
                (event_type, object_type, confidence, message, timestamp)
            )
            conn.commit()
            return str(cur.lastrowid)

    def list(self, limit=50):
        limit = max(1, min(int(limit), 500))
        if self.mode == "mongodb":
            docs = list(self.collection.find().sort("timestamp", -1).limit(limit))
            for d in docs:
                d["_id"] = str(d["_id"])
            return docs

        with sqlite3.connect(SQLITE_PATH) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT id,event_type,object_type,confidence,message,timestamp FROM events ORDER BY id DESC LIMIT ?",
                (limit,)
            ).fetchall()
            return [dict(r) for r in rows]

    def clear(self):
        if self.mode == "mongodb":
            self.collection.delete_many({})
            return
        with sqlite3.connect(SQLITE_PATH) as conn:
            conn.execute("DELETE FROM events")
            conn.commit()
