class SovereignAgent:
    """
    Single-agent cognitive loop:
    PLAN -> SELECT -> ACT -> OBSERVE -> VERIFY -> REPLAN.

    The model proposes; policy decides; tools execute; verification
    determines whether the loop may continue.
    """
    def __init__(self, registry, discovery, memory, queue, http,
                 verifier, policy, audit, models):
        self.registry = registry
        self.discovery = discovery
        self.memory = memory
        self.queue = queue
        self.http = http
        self.verifier = verifier
        self.policy = policy
        self.audit = audit
        self.models = models
        self.max_steps = 5

    async def plan(self, task):
        if not task.strip():
            return {"status": "rejected", "reason": "empty task"}

        context = self.memory.recent(limit=8)
        prompt = (
            "You are the planning component of TAES. "
            "Return a compact JSON object with keys: objective, "
            "steps, required_capabilities, risk. "
            "Do not execute anything. Task: " + task +
            "\nContext:\n" + str(context)
        )

        model = await self.models.generate(prompt)

        return {
            "status": "planned",
            "objective": task,
            "model_plan": model,
            "available_capabilities": self.registry.list()
        }

    async def run(self, task):
        if not task.strip():
            return {"status": "rejected", "reason": "empty task"}

        trace = []
        plan = await self.plan(task)
        trace.append({"phase": "plan", "data": plan})

        for step in range(self.max_steps):
            decision = self.policy.allow("agent_step", risk="low")
            trace.append({"phase": "policy", "data": decision})

            if not decision["allowed"]:
                return {"status": "blocked", "trace": trace}

            # v2.0 uses a safe queue boundary. Automatic external actions
            # are not inferred from arbitrary model text.
            job = self.queue.enqueue(
                f"TAES_STEP {step + 1}: {task}"
            )
            trace.append({"phase": "queue", "data": job})

            observation = {
                "status": "awaiting_worker",
                "step": step + 1,
                "job_id": job.get("job_id")
            }
            trace.append({"phase": "observe", "data": observation})

            verified = self.verifier.verify(observation)
            trace.append({"phase": "verify", "data": verified})

            if verified.get("verified"):
                self.memory.remember(
                    f"trace:{job.get('job_id')}",
                    {"task": task, "trace": trace}
                )

                self.audit.record(
                    "agent_run",
                    {"task": task, "steps": step + 1}
                )

                return {
                    "status": "accepted",
                    "task": task,
                    "steps": step + 1,
                    "trace": trace
                }

        return {
            "status": "max_steps_reached",
            "trace": trace
        }
