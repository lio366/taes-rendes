import httpx
from app.config import MODEL_BASE_URL, MODEL_NAME, MODEL_API_KEY

class ModelRouter:
    def __init__(self):
        self.providers = []
        if MODEL_BASE_URL and MODEL_NAME:
            self.providers.append({
                "name": "primary",
                "base_url": MODEL_BASE_URL,
                "model": MODEL_NAME,
                "api_key": MODEL_API_KEY
            })

    def status(self):
        return {
            "providers": len(self.providers),
            "configured": bool(self.providers),
            "routing": "priority-fallback"
        }

    async def generate(self, prompt):
        if not prompt.strip():
            return {"status": "rejected", "reason": "empty prompt"}

        if not self.providers:
            return {
                "status": "not_configured",
                "mode": "control_plane_only"
            }

        last_error = None

        for provider in self.providers:
            try:
                headers = {}
                if provider["api_key"]:
                    headers["Authorization"] = (
                        f"Bearer {provider['api_key']}"
                    )

                payload = {
                    "model": provider["model"],
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1
                }

                async with httpx.AsyncClient(timeout=60) as client:
                    response = await client.post(
                        f"{provider['base_url']}/v1/chat/completions",
                        json=payload,
                        headers=headers
                    )
                    response.raise_for_status()
                    data = response.json()

                return {
                    "status": "ok",
                    "provider": provider["name"],
                    "model": provider["model"],
                    "text": data["choices"][0]["message"]["content"]
                }
            except Exception as exc:
                last_error = type(exc).__name__

        return {"status": "provider_error", "error": last_error}
