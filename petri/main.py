from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel

from petri.executor import run
from petri.registry import Registry, SandboxNotFound
from petri.sandbox import Sandbox, SandboxStatus

app = FastAPI(title="Petri", version="0.1.0")

_registry = Registry()


def get_registry() -> Registry:
    return _registry


class CreateSandboxRequest(BaseModel):
    language: str = "python"


class SandboxResponse(BaseModel):
    id: str
    language: str
    status: SandboxStatus


class ExecRequest(BaseModel):
    code: str


class ExecResponse(BaseModel):
    output: str


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/sandboxes", status_code=201)
def create_sandbox(
    request: CreateSandboxRequest,
    registry: Registry = Depends(get_registry),
) -> SandboxResponse:
    sandbox = Sandbox(language=request.language)
    registry.add(sandbox)

    return SandboxResponse(
        id=sandbox.id, language=sandbox.language, status=sandbox.status
    )


@app.post("/v1/sandboxes/{sandbox_id}/exec")
def exec_sandbox(
    sandbox_id: str,
    request: ExecRequest,
    registry: Registry = Depends(get_registry),
) -> ExecResponse:
    try:
        sandbox = registry.get(sandbox_id)
    except SandboxNotFound:
        raise HTTPException(status_code=404, detail="Sandbox not found")
    output = run(sandbox, request.code)
    return ExecResponse(output=output)


@app.get("/v1/sandboxes/{sandbox_id}")
def get_sandbox(
    sandbox_id: str,
    registry: Registry = Depends(get_registry),
) -> SandboxResponse:

    try:
        sandbox = registry.get(sandbox_id)
    except SandboxNotFound:
        raise HTTPException(status_code=404, detail="Sandbox not found")
    return SandboxResponse(
        id=sandbox.id, language=sandbox.language, status=sandbox.status
    )


@app.delete("/v1/sandboxes/{sandbox_id}", status_code=204)
def delete_sandbox(
    sandbox_id: str,
    registry: Registry = Depends(get_registry),
) -> None:
    try:
        registry.remove(sandbox_id)
    except SandboxNotFound:
        raise HTTPException(status_code=204, detail="Sandbox not found")
