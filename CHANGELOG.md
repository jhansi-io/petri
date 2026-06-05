# Changelog

## [v0.2.0] - 2026-06-05

### Added
- Persistent workspace per sandbox — dedicated folder on disk at creation time
- `POST /v1/sandboxes/{id}/files` — file upload endpoint
- `petri/config.py` — workspace root configuration via `PETRI_WORKSPACE_ROOT`
- Defaults to `~/.petri/workspaces` if env var not set

### Changed
- `POST /v1/sandboxes/{id}/exec` — now accepts `filename` instead of `code`
- Executor mounts workspace folder instead of temp file
- `Sandbox` dataclass now includes `workspace_path`

### Removed
- Code as string in exec request body

## [0.1.0] — 2026-06-04

Initial release.

### API
- `POST /v1/sandboxes` — create isolated sandbox, returns `sb_` prefixed ID
- `POST /v1/sandboxes/{id}/exec` — execute code, return stdout/stderr
- `GET /v1/sandboxes/{id}` — inspect sandbox status
- `DELETE /v1/sandboxes/{id}` — tear down sandbox, returns 204

### Execution
- Docker-based isolation per execution
- Multi-language support — python, go, node
- Stderr captured via `2>&1` inside container
- Temp file mount strategy — code written to disk, mounted into container

### Internals
- In-memory `Registry` with `SandboxNotFound` domain exception
- `Sandbox` dataclass with status enum and `sb_` ID prefix
- `Registry` injected as FastAPI dependency — no global singletons
- Mypy strict, Ruff, Pytest — full quality gate via Makefile

### Decisions recorded
- ADR-001 — execution strategy (temp file + mount)
- ADR-002 — sandbox ID generation (`secrets.token_hex` over `uuid4`)
- ADR-003 — sandbox model structure
- ADR-004 — stderr handling

---

> Foundation release. Execution is ephemeral — container spins up, runs, dies.
> Workspace model, file upload, and dependency handling are planned for v0.2.
