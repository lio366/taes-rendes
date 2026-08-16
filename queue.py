import sqlite3
import uuid
from datetime import datetime, timezone
from app.config import REDIS_URL

class ExecutionQueue:
    def __init__(self, path="taes_queue.db"):
        self.mode = "sqlite"
        self.redis = None

        if REDIS_URL:
            try:
                import redis
                self.redis = redis.from_url(
                    REDIS_URL, decode_responses=True
                )
                self.redis.ping()
                self.mode = "redis"
            except Exception:
                pass

        if self.mode == "sqlite":
            self.db = sqlite3.connect(
                path, check_same_thread=False
            )
            self.db.execute(
                "CREATE TABLE IF NOT EXISTS jobs "
                "(id TEXT PRIMARY KEY, task TEXT, status TEXT, "
                "created_at TEXT)"
            )
            self.db.commit()

    def enqueue(self, task):
        if not task.strip():
            return {"status": "rejected", "reason": "empty task"}

        job_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        if self.mode == "redis":
            self.redis.hset(
                f"taes:job:{job_id}",
                mapping={
                    "id": job_id,
                    "task": task,
                    "status": "queued",
                    "created_at": now
                }
            )
            self.redis.rpush("taes:queue", job_id)
        else:
            self.db.execute(
                "INSERT INTO jobs VALUES(?,?,?,?)",
                (job_id, task, "queued", now)
            )
            self.db.commit()

        return {"status": "queued", "job_id": job_id}

    def claim(self):
        if self.mode == "redis":
            job_id = self.redis.lpop("taes:queue")
            if not job_id:
                return None
            job = self.redis.hgetall(f"taes:job:{job_id}")
            if job:
                self.redis.hset(
                    f"taes:job:{job_id}", "status", "running"
                )
            return job or None

        row = self.db.execute(
            "SELECT id,task,status,created_at FROM jobs "
            "WHERE status='queued' ORDER BY created_at LIMIT 1"
        ).fetchone()

        if not row:
            return None

        self.db.execute(
            "UPDATE jobs SET status='running' WHERE id=?", (row[0],)
        )
        self.db.commit()

        return {
            "id": row[0], "task": row[1],
            "status": "running", "created_at": row[3]
        }

    def complete(self, job_id, status):
        if self.mode == "redis":
            self.redis.hset(f"taes:job:{job_id}", "status", status)
        else:
            self.db.execute(
                "UPDATE jobs SET status=? WHERE id=?",
                (status, job_id)
            )
            self.db.commit()

    def list(self):
        if self.mode == "redis":
            keys = self.redis.keys("taes:job:*")
            return [self.redis.hgetall(k) for k in keys[:100]]

        rows = self.db.execute(
            "SELECT id,task,status,created_at FROM jobs "
            "ORDER BY created_at DESC LIMIT 100"
        ).fetchall()

        return [
            {"id": r[0], "task": r[1], "status": r[2],
             "created_at": r[3]}
            for r in rows
        ]

    def status(self):
        if self.mode == "redis":
            return {
                "backend": "redis",
                "queued": self.redis.llen("taes:queue")
            }

        count = self.db.execute(
            "SELECT COUNT(*) FROM jobs WHERE status='queued'"
        ).fetchone()[0]
        return {"backend": "sqlite", "queued": count}
