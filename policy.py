class PolicyEngine:
    def allow(self, action, risk="unknown"):
        if risk in {"critical", "unknown"}:
            return {
                "allowed": False,
                "reason": "risk requires explicit policy"
            }

        return {
            "allowed": True,
            "action": action,
            "risk": risk
        }
