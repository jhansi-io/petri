import asyncio
import io
import subprocess
import zipfile
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from petri.config import TTL_SECONDS, WORKSPACE_ROOT
from petri.executor import run_stream
from petri.registry import Registry, SandboxNotFound
from petri.sandbox import Sandbox, SandboxStatus


async def cleanup_loop() -> None:
    while True:
        await asyncio.sleep(60)
        expired = _registry.list_expired()
        for sandbox in expired:
            if sandbox.container_id:
                subprocess.run(
                    ["docker", "stop", sandbox.container_id],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            _registry.remove(sandbox.id)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    asyncio.create_task(cleanup_loop())
    yield


app = FastAPI(title="Petri", version="0.1.0", lifespan=lifespan)

_registry = Registry()


def get_registry() -> Registry:
    return _registry


class CreateSandboxRequest(BaseModel):
    language: str = "python"
    agent: str | None = None
    created_by: str = "unknown"


class SandboxResponse(BaseModel):
    id: str
    language: str
    status: SandboxStatus


class ExecRequest(BaseModel):
    command: str
    test: bool = False


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/sandboxes", status_code=201)
def create_sandbox(
    request: CreateSandboxRequest,
    registry: Registry = Depends(get_registry),
) -> SandboxResponse:
    sandbox = Sandbox(
        language=request.language,
        agent=request.agent,
        created_by=request.created_by,
    )
    sandbox.workspace_path = WORKSPACE_ROOT / sandbox.id
    sandbox.workspace_path.mkdir(parents=True, exist_ok=True)
    registry.add(sandbox)

    return SandboxResponse(
        id=sandbox.id, language=sandbox.language, status=sandbox.status
    )


@app.post("/v1/sandboxes/{sandbox_id}/files", status_code=201)
async def upload_file(
    sandbox_id: str,
    file: UploadFile = File(...),
    registry: Registry = Depends(get_registry),
) -> dict[str, str]:
    try:
        sandbox = registry.get(sandbox_id)
    except SandboxNotFound:
        raise HTTPException(status_code=404, detail="Sandbox not found")

    if sandbox.workspace_path is None:
        raise HTTPException(status_code=500, detail="Workspace not initialised")

    if file.filename is None:
        raise HTTPException(status_code=400, detail="Filename is missing")
    destination = sandbox.workspace_path / file.filename
    destination.write_bytes(await file.read())

    return {"filename": file.filename}


@app.post("/v1/sandboxes/{sandbox_id}/upload", status_code=201)
async def upload_project(
    sandbox_id: str,
    file: UploadFile = File(...),
    registry: Registry = Depends(get_registry),
) -> dict[str, str]:
    try:
        sandbox = registry.get(sandbox_id)
    except SandboxNotFound:
        raise HTTPException(status_code=404, detail="Sandbox not found")

    contents = await file.read()
    with zipfile.ZipFile(io.BytesIO(contents)) as zf:
        for member in zf.namelist():
            if member.startswith("..") or member.startswith("/"):
                raise HTTPException(status_code=400, detail="Invalid zip path")
            if sandbox.workspace_path is None:
                raise HTTPException(status_code=500, detail="Workspace not initialised")
            target = sandbox.workspace_path / member
            if member.endswith("/"):
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(zf.read(member))
    return {"status": "uploaded"}


@app.post("/v1/sandboxes/{sandbox_id}/exec")
def exec_sandbox(
    sandbox_id: str,
    request: ExecRequest,
    registry: Registry = Depends(get_registry),
) -> StreamingResponse:
    try:
        sandbox = registry.get(sandbox_id)
    except SandboxNotFound:
        raise HTTPException(status_code=404, detail="Sandbox not found")
    new_expires = datetime.now(timezone.utc) + timedelta(seconds=TTL_SECONDS)
    registry.update_expires_at(sandbox_id, new_expires)
    return StreamingResponse(
        (
            f"data: {line}"
            for line in run_stream(sandbox, request.command, request.test)
        ),
        media_type="text/event-stream",
    )


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
        raise HTTPException(status_code=404, detail="Sandbox not found")
