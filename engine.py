from urllib.parse import urlparse

SAFE_LICENSES = {
    "mit", "apache-2.0", "bsd-2-clause",
    "bsd-3-clause", "mpl-2.0", "isc", "unlicense", "cc0"
}

class CapabilityDiscoveryEngine:
    def __init__(self, registry):
        self.registry = registry

    def evaluate(self, candidate):
        if not candidate.get("name") or not candidate.get("kind"):
            return {"approved": False, "reason": "name and kind required"}

        license_name = (candidate.get("license") or "").lower()
        if license_name not in SAFE_LICENSES:
            return {"approved": False, "reason": "license requires review"}

        endpoint = candidate.get("endpoint")
        if endpoint and urlparse(endpoint).scheme != "https":
            return {"approved": False, "reason": "HTTPS required"}

        return {
            "approved": True,
            "checks": ["identity", "license", "transport"]
        }

    def register_if_approved(self, candidate):
        result = self.evaluate(candidate)
        if not result["approved"]:
            return result

        self.registry.register({
            **candidate,
            "enabled": True,
            "verified": False
        })

        return {
            "approved": True,
            "registered": candidate["name"]
        }
