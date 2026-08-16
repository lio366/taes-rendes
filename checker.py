import httpx
from urllib.parse import urlparse

class CapabilityHealthChecker:
    def __init__(self, registry):
        self.registry = registry

    async def check_all(self):
        results = []

        for item in self.registry.list():
            endpoint = item.get("endpoint")
            status = "unknown"

            if endpoint:
                try:
                    if urlparse(endpoint).scheme != "https":
                        status = "blocked"
                    else:
                        async with httpx.AsyncClient(
                            timeout=8,
                            follow_redirects=False
                        ) as client:
                            response = await client.head(endpoint)
                            status = (
                                "healthy"
                                if response.status_code < 500
                                else "unhealthy"
                            )
                except Exception:
                    status = "unreachable"

            results.append({
                "name": item.get("name"),
                "status": status
            })

        return {"capabilities": results}
