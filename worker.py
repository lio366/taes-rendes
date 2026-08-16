import asyncio
from datetime import datetime, timezone

class WorkerController:
    def __init__(self, queue, sandbox):
        self.queue = queue
        self.sandbox = sandbox
        self.running = False
        self.processed = 0
        self.last_job = None

    async def loop(self):
        if self.running:
            return
        self.running = True

        while True:
            job = self.queue.claim()
            if not job:
                await asyncio.sleep(2)
                continue

            result = await self._dispatch(job["task"])
            status = (
                "completed"
                if result.get("status") == "completed"
                else "blocked"
                if result.get("status") == "blocked"
                else "failed"
            )

            self.queue.complete(job["id"], status)
            self.processed += 1
            self.last_job = {
                "job_id": job["id"],
                "task": job["task"],
                "result": result,
                "finished_at": datetime.now(timezone.utc).isoformat()
            }

    async def _dispatch(self, task):
        if task.strip().lower() == "sandbox_test":
            return await self.sandbox.run("sandbox_test")
        return {
            "status": "blocked",
            "reason": "no allowlisted execution mapping"
        }

    def status(self):
        return {
            "running": self.running,
            "processed": self.processed,
            "last_job": self.last_job
        }
