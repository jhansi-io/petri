# Changelog

## [0.9.0] - 2026-06-11

### Added
- Typed SSE events — `event: output` for stream lines, `event: done` for structured result
- `done` payload includes `exit_code`, `duration_ms`, `output`, and `error` (last error line on failure)
- Run model — every execution stored in SQLite with metadata: `exit_code`, `duration_ms`, `error`, `started_at`, `completed_at`
- Full execution output written to flat log file at `PETRI_WORKSPACE_ROOT/{sandbox_id}/runs/{run_id}.log`
- Rolling log retention — `PETRI_LOG_MAX_MB` env var (default `500`) caps total log storage, oldest files evicted first
- Soft delete — sandboxes marked `deleted` with `deleted_at` timestamp, rows retained in SQLite
- `agent` and `created_by` optional fields on `POST /v1/sandboxes` — tracks calling agent and creator
- `GET /v1/metrics` — live counts: active sandboxes, total sandboxes, total runs, failed runs, success rate, avg duration, breakdown by agent
- ADR-014: observability and execution history

### Changed
- `DELETE /v1/sandboxes/{id}` — soft delete, row retained for history
- `GET /v1/sandboxes/{id}` — returns 404 for deleted sandboxes

## [0.7.0] - 2026-06-10

### Changed
- `POST /v1/sandboxes/{id}/exec` now streams output via SSE — breaking change
- Replaced `subprocess.run` with `subprocess.Popen` for exec — output streamed line by line
- Dep install remains silent and blocking; only exec output is streamed
- Test mode streams pytest output line by line

### Added
- `run_stream()` generator in `executor.py`
- ADR-011: streaming execution via SSE

## [0.6.0] - 2026-06-10

### Added
- SQLite-backed registry — sandbox state survives Petri restarts
- `expires_at` field on `Sandbox` — default TTL of 1 hour
- `PETRI_SANDBOX_TTL_SECONDS` env var to configure TTL
- Background cleanup task — expired sandboxes removed every 60 seconds
- `update_expires_at()` and `list_expired()` methods on `Registry`

### Changed
- Exec resets `expires_at` on every call — only idle sandboxes are cleaned up
- Dep install and exec split into separate Docker runs — clean output separation
- Removed `pipreqs` fallback — no more noise in exec output

## [0.5.0] - 2026-06-08

### Added
- Dockerfile for containerised deployment
- docker-compose.yml for self-hosting — mounts Docker socket and workspace volume
- `PETRI_WORKSPACE_ROOT` set to `/tmp/petri-workspaces` in Docker Compose

## [0.4.0] - 2026-06-07
### Added
- `POST /v1/sandboxes/{id}/upload` — project upload via zip, preserves folder structure
- `POST /v1/sandboxes/{id}/exec` now accepts `command` and optional `test` flag
- Test mode — starts the command, waits 2 seconds, runs language-appropriate test suite, returns results
- Test runners: pytest (Python), jest (Node), go test (Go), mvn test (Java)
- ADR-007: test mode
- ADR-008: project upload via zip

### Changed
- `exec` request body: `filename` replaced by `command` — breaking change
- Java image updated to `maven:3.9-amazoncorretto-21` to support `mvn test`
- Dependency installation separated from execution for test mode

## [0.3.0] - 2026-06-06

### Added
- Auto dependency detection at exec time for Python, Node, Go, and Java
- Python: supports pyproject.toml, requirements.txt, and pipreqs fallback
- Node: supports package.json + npm install
- Go: supports go.mod + go mod download, falls back to go mod init + tidy
- Java: supports pom.xml (Maven), build.gradle (Gradle), falls back to javac
- Dependencies installed into sandbox workspace — persists across runs
- ADR-006: auto dependency detection and installation

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
