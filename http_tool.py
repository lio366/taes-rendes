from urllib.parse import urlparse
import httpx

class HTTPTool:
    async def request(self, method, url, headers=None, body=None):
        parsed = urlparse(url)

        if parsed.scheme != "https":
            return {"status": "blocked", "reason": "HTTPS required"}

        try:
            async with httpx.AsyncClient(
                timeout=15,
                follow_redirects=False
            ) as client:
                response = await client.request(
                    method.upper(),
                    url,
                    headers=headers or {},
                    json=body
                )

            return {
                "status": "ok",
                "http_status": response.status_code,
                "content_type": response.headers.get("content-type"),
                "text": response.text[:20000]
            }
        except Exception as exc:
            return {"status": "error", "error": type(exc).__name__}
