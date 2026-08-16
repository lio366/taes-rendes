from app.agent.core import SovereignAgent
from app.discovery.registry import CapabilityRegistry
from app.discovery.engine import CapabilityDiscoveryEngine
from app.memory.store import MemoryStore
from app.execution.queue import ExecutionQueue
from app.execution.worker import WorkerController
from app.execution.sandbox import Sandbox
from app.tools.http_tool import HTTPTool
from app.verification.engine import VerificationEngine
from app.security.policy import PolicyEngine
from app.audit.logger import AuditLogger
from app.models.router import ModelRouter
from app.health.checker import CapabilityHealthChecker

class Runtime:
    def __init__(self):
        self.registry = CapabilityRegistry()
        self.discovery = CapabilityDiscoveryEngine(self.registry)
        self.memory = MemoryStore()
        self.queue = ExecutionQueue()
        self.sandbox = Sandbox()
        self.worker = WorkerController(self.queue, self.sandbox)
        self.http = HTTPTool()
        self.verifier = VerificationEngine()
        self.policy = PolicyEngine()
        self.audit = AuditLogger()
        self.models = ModelRouter()
        self.health_checker = CapabilityHealthChecker(self.registry)
        self.agent = SovereignAgent(
            self.registry, self.discovery, self.memory, self.queue,
            self.http, self.verifier, self.policy, self.audit, self.models
        )

    def identity(self):
        return {
            "system": "TAES",
            "version": "2.0.0",
            "name": "Sovereign Agent",
            "mode": "autonomous-control-plane",
            "execution": "policy-gated"
        }

    def health(self):
        return {
            "status": "healthy",
            "worker": self.worker.status(),
            "memory": self.memory.status(),
            "queue": self.queue.status(),
            "sandbox": self.sandbox.status(),
            "model_router": self.models.status(),
            "capabilities": self.registry.count()
        }

    def discover(self, payload):
        result = self.discovery.register_if_approved(payload)
        self.audit.record("capability_discovery", result)
        return result
