import asyncio
import io
import json
import secrets
import subprocess
import zipfile
from collections.abc import AsyncGenerator, Generator
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel

from petri.config import LOG_MAX_MB, TTL_SECONDS, WORKSPACE_ROOT
from petri.dashboard import DASHBOARD_HTML
from petri.executor import run_stream
from petri.log_retention import evict_logs_if_needed
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


class SandboxListItem(BaseModel):
    id: str
    language: str
    status: SandboxStatus
    agent: str | None
    created_by: str
    created_at: datetime
    expires_at: datetime


class ExecRequest(BaseModel):
    command: str
    test: bool = False


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/v1/metrics")
def get_metrics(
    registry: Registry = Depends(get_registry),
) -> dict:  # type: ignore[type-arg]
    return registry.get_metrics()


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


def _stream_and_record(
    sandbox_id: str,
    registry: Registry,
    generator: Generator[str, None, None],
    log_path: Path,
) -> Generator[str, None, None]:
    for event in generator:
        yield event
        if event.startswith("event: done"):
            data_line = event.split("data: ", 1)[1].strip()
            payload = json.loads(data_line)
            run_id = f"run_{secrets.token_hex(8)}"
            now = datetime.now(timezone.utc)
            started_at = now - timedelta(milliseconds=payload["duration_ms"])
            log_path.parent.mkdir(parents=True, exist_ok=True)
            log_path.write_text(payload["output"] or "")
            evict_logs_if_needed(WORKSPACE_ROOT, LOG_MAX_MB)
            registry.add_run(
                run_id=run_id,
                sandbox_id=sandbox_id,
                started_at=started_at,
                completed_at=now,
                duration_ms=payload["duration_ms"],
                exit_code=payload["exit_code"],
                error=payload["error"],
                output=None,
            )


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
    log_path = (
        WORKSPACE_ROOT
        / sandbox_id
        / "runs"
        / f"{sandbox_id}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}.log"
    )
    return StreamingResponse(
        _stream_and_record(
            sandbox_id=sandbox_id,
            registry=registry,
            generator=run_stream(sandbox, request.command, request.test),
            log_path=log_path,
        ),
        media_type="text/event-stream",
    )


@app.get("/v1/sandboxes/active")
def list_active_sandboxes(
    registry: Registry = Depends(get_registry),
) -> list[SandboxListItem]:
    return [
        SandboxListItem(
            id=s.id,
            language=s.language,
            status=s.status,
            agent=s.agent,
            created_by=s.created_by,
            created_at=s.created_at,
            expires_at=s.expires_at,
        )
        for s in registry.list_active()
    ]


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


@app.get("/v1/sandboxes")
def list_sandboxes(
    limit: int = 50,
    offset: int = 0,
    registry: Registry = Depends(get_registry),
) -> list[SandboxListItem]:
    return [
        SandboxListItem(
            id=s.id,
            language=s.language,
            status=s.status,
            agent=s.agent,
            created_by=s.created_by,
            created_at=s.created_at,
            expires_at=s.expires_at,
        )
        for s in registry.list_all(limit=limit, offset=offset)
    ]


@app.get("/v1/sandboxes/{sandbox_id}/runs")
def list_sandbox_runs(
    sandbox_id: str,
    registry: Registry = Depends(get_registry),
) -> list[dict]:  # type: ignore[type-arg]
    return registry.list_runs(sandbox_id)


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard() -> str:
    return DASHBOARD_HTML
