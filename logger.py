from datetime import datetime, timezone

class AuditLogger:
    def __init__(self):
        self.events = []

    def record(self, event, data):
        self.events.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event,
            "data": data
        })
        if len(self.events) > 5000:
            self.events = self.events[-5000:]

    def list(self):
        return self.events
