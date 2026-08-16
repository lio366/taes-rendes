# TAES 10/10 — Sovereign Agent v2.0

This is the consolidated architecture package.

## Core

TAES is one agent with many capabilities. It is not a swarm of
independent agents.

Cognitive loop:
PLAN -> SELECT -> ACT -> OBSERVE -> VERIFY -> REPLAN

## Included

- Single-agent orchestration
- Model Router
- Persistent memory
- PostgreSQL adapter
- Redis adapter
- Execution queue
- Worker controller
- Restricted sandbox
- HTTPS-only HTTP tool
- Capability discovery
- License policy gate
- Capability health checks
- Verification
- Audit trail
- Docker
- Docker Compose
- Render deployment

## Capability acquisition

TAES can register external capabilities only after policy checks.
"Public" does not mean "free to use"; licensing, authentication,
rate limits and commercial-use conditions must be verified.

## Model independence

TAES does not require a specific commercial AI provider.
MODEL_BASE_URL can point to an OpenAI-compatible model runtime.

## Security

The model cannot directly execute arbitrary shell commands.
Tool execution passes through policy and allowlists.
The included sandbox is a restricted bootstrap, not a hostile-code
containment boundary.

For truly untrusted code, deploy the sandbox as a separate container or
microVM with network isolation, read-only filesystem, seccomp/AppArmor,
dropped capabilities, resource quotas and an external kill switch.

## Production topology

Internet
  v
API Gateway / Auth
  v
TAES Control Plane
  |-- Agent Core
  |-- Model Router
  |-- Capability Registry
  |-- Policy
  |-- Verification
  `-- Audit
       v
  Redis Queue
       v
  Worker
       v
  Isolated Sandbox
       v
  PostgreSQL / Vector Memory

## Reality check

This package is a strong autonomous-agent foundation. It is not an
honest claim of full parity with frontier products such as Copilot,
Claude or Kimi. Frontier parity depends primarily on the model, context
window, tool ecosystem, inference infrastructure, evaluation suite and
product integration-not only on Python architecture.

## First production hardening tasks

1. Put API authentication/rate limiting in front of the service.
2. Use managed PostgreSQL and Redis.
3. Run the sandbox as a separate isolated service.
4. Add secret management.
5. Add structured telemetry and distributed tracing.
6. Add automated evaluation datasets.
7. Add model fallback providers if desired.
8. Add signed capability manifests and dependency scanning.
