import asyncio
from fastapi import FastAPI
from app.runtime import Runtime

runtime = Runtime()
app = FastAPI(title="TAES Sovereign Agent", version="2.0.0")

@app.on_event("startup")
async def startup():
    asyncio.create_task(runtime.worker.loop())

@app.get("/")
async def root():
    return runtime.identity()

@app.get("/health")
async def health():
    return runtime.health()

@app.get("/capabilities")
async def capabilities():
    return runtime.registry.list()

@app.post("/capabilities/discover")
async def discover(payload: dict):
    return runtime.discover(payload)

@app.post("/agent/run")
async def agent_run(payload: dict):
    return await runtime.agent.run(payload.get("task", ""))

@app.post("/agent/plan")
async def agent_plan(payload: dict):
    return await runtime.agent.plan(payload.get("task", ""))

@app.post("/model/generate")
async def model_generate(payload: dict):
    return await runtime.models.generate(payload.get("prompt", ""))

@app.post("/tools/http")
async def http_tool(payload: dict):
    return await runtime.http.request(
        payload.get("method", "GET"),
        payload.get("url", ""),
        payload.get("headers", {}),
        payload.get("body")
    )

@app.post("/sandbox/run")
async def sandbox_run(payload: dict):
    return await runtime.sandbox.run(
        payload.get("action", ""),
        payload.get("arguments", {})
    )

@app.get("/jobs")
async def jobs():
    return runtime.queue.list()

@app.get("/audit")
async def audit():
    return runtime.audit.list()
