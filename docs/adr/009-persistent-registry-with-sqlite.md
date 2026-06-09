# ADR 009 - Persistent Registry with SQLite

## Status
Accepted

## Context
The sandbox registry is currently in-memory. A Petri restart wipes all sandbox
state. This breaks any agent workflow that expects a sandbox to persist across
server restarts.

## Decision
Replace the in-memory dict with a SQLite-backed registry. SQLite is built into
Python, requires no additional services, and handles concurrent writes safely.
It also gives a clean foundation for TTL queries in the next commit.

## Alternatives Considered
- **JSON file** — zero deps and human readable, but no atomic writes and risks
  corruption on crash.
- **Redis** — native TTL support, but requires an extra service, breaking the
  simplicity of `docker compose up` for self-hosters.
- **Abstracted registry interface** — would allow swapping backends cleanly, but
  adds complexity now for a problem only we will solve later.

## Consequences
- Sandbox state survives Petri restarts
- No new dependencies or services required for self-hosters
- TTL cleanup via SQL query (`WHERE expires_at < now()`) in the next commit
- Registry is not abstracted — the SQLite implementation is concrete and intentional

## Future
Redis is a natural upgrade path if horizontal scaling or native TTL becomes a
requirement.
