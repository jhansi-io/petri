# ADR 015: Read-only dashboard (v0.11)

**Status:** Proposed
**Date:** 2026-06-18

## Context

Petri tracks sandboxes and runs in SQLite and exposes `GET /v1/metrics`, but there's no way to *see* what's alive or what has run without hitting the DB directly. v0.11 adds a developer-facing dashboard: a single HTML page served by Petri showing live sandboxes, full history, and a runs drill-down.

## Decision

- **Two views, one page.** "Active" (what's alive now) and "History" (everything, paginated), plus a runs drill-down per sandbox. Plain HTML + `fetch`, no templating engine.
- **Active predicate is `deleted_at IS NULL AND expires_at > now`.** A sandbox is "current" only if not soft-deleted and still within TTL.
- **Two list endpoints, not one filtered endpoint.** `GET /v1/sandboxes/active` (no pagination — live set is small) and `GET /v1/sandboxes` (paginated via `limit`/`offset`, newest first).
- **Register `/active` before `/{sandbox_id}`.** FastAPI matches routes in order; otherwise `"active"` is captured as a sandbox_id.
- **Runs endpoint returns metadata only.** `GET /v1/sandboxes/{id}/runs` returns `id, started_at, completed_at, duration_ms, exit_code, error`. No log contents — the flat `.log` files stay out of scope.
- **Richer list row.** List endpoints return `id, language, status, agent, created_by, created_at, expires_at` — `SandboxResponse` (id/language/status) is too thin for the table. New `SandboxListItem` model.
- **Three new registry methods.** `list_active()`, `list_all(limit, offset)`, `list_runs(sandbox_id)`.
- **Dashboard served at `GET /dashboard`.** Returns a single static HTML string from the FastAPI app. No `static/` dir needed for one file.

## Out of scope (deferred)

- **Log contents drill-down.** Blocked anyway: runs have no link to their flat log file (backlog #28). Revisit when that link exists.
- **`command` in runs drill-down.** No `command` column on runs yet (backlog #29).
- **Mutating actions** (delete sandbox from the browser). Read-only for v0.11.

## Consequences

- Dashboard is honest but minimal — it reflects exactly what the DB knows, nothing inferred.
- The two deferred drill-down gaps are now visible in the UI as "what's missing," which naturally pulls the backlog items forward.
