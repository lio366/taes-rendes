import sqlite3
import json
from datetime import datetime, timezone
from app.config import DATABASE_URL

class MemoryStore:
    def __init__(self, path="taes_memory.db"):
        self.mode = "sqlite"
        self.pg = None

        if DATABASE_URL:
            try:
                import psycopg
                self.pg = psycopg.connect(DATABASE_URL)
                self.pg.execute(
                    "CREATE TABLE IF NOT EXISTS taes_memory "
                    "(k TEXT PRIMARY KEY, v JSONB, created_at TIMESTAMPTZ)"
                )
                self.pg.commit()
                self.mode = "postgres"
                return
            except Exception:
                pass

        self.db = sqlite3.connect(path, check_same_thread=False)
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS memory "
            "(k TEXT PRIMARY KEY, v TEXT, created_at TEXT)"
        )
        self.db.commit()

    def remember(self, key, value):
        now = datetime.now(timezone.utc).isoformat()
        if self.mode == "postgres":
            self.pg.execute(
                "INSERT INTO taes_memory(k,v,created_at) VALUES(%s,%s,%s) "
                "ON CONFLICT(k) DO UPDATE SET v=EXCLUDED.v, "
                "created_at=EXCLUDED.created_at",
                (key, json.dumps(value), now)
            )
            self.pg.commit()
        else:
            self.db.execute(
                "INSERT OR REPLACE INTO memory(k,v,created_at) "
                "VALUES(?,?,?)",
                (key, json.dumps(value), now)
            )
            self.db.commit()

    def recent(self, limit=8):
        if self.mode == "postgres":
            rows = self.pg.execute(
                "SELECT k,v,created_at FROM taes_memory "
                "ORDER BY created_at DESC LIMIT %s", (limit,)
            ).fetchall()
            return [{"key": r[0], "value": r[1], "created_at": str(r[2])}
                    for r in rows]

        rows = self.db.execute(
            "SELECT k,v,created_at FROM memory "
            "ORDER BY created_at DESC LIMIT ?",
            (limit,)
        ).fetchall()
        return [
            {"key": r[0], "value": json.loads(r[1]), "created_at": r[2]}
            for r in rows
        ]

    def recall(self, key):
        if self.mode == "postgres":
            row = self.pg.execute(
                "SELECT v FROM taes_memory WHERE k=%s", (key,)
            ).fetchone()
            return row[0] if row else None

        row = self.db.execute(
            "SELECT v FROM memory WHERE k=?", (key,)
        ).fetchone()
        return json.loads(row[0]) if row else None

    def status(self):
        return {
            "backend": self.mode,
            "persistent": True,
            "context_window_items": 8
        }
