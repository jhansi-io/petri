# ADR 003 - Sandbox Model Structure

## Status
Accepted

## Context
We needed to define the core Sandbox dataclass - what state a sandbox
carries, what we defer, and how it is stored.

## Decision
The Sandbox model contains five fields only:

- `id` - cryptographically random identifier (see ADR 002)
- `language` - target runtime (python, node, go)
- `container_id` - Docker container reference, None until started
- `status` - enum: created, running, stopped, error
- `created_at` - UTC timestamp for audit and cleanup

Status is a `str` enum (not plain string) so invalid states are
impossible at the type level.

Sandboxes are stored in an in-memory Registry - a plain dict
keyed by sandbox id.

## Alternatives Considered
- **Add timeout and memory_limit** - deferred to Phase 2.
  No real usage data yet to choose sensible defaults.
- **Persist to a database** - deferred to Phase 2.
  In-memory is sufficient for MVP and keeps the stack simple.
- **Status as plain string** - rejected. Enum catches invalid
  states at type-check time, not at runtime.


## Consequences
- Registry is lost on restart - acceptable for MVP
- Adding timeout/limits later is a non-breaking field addition
- Mypy enforces valid state transitions at compile time

## Future
- Add `timeout` and `memory_limit` when real usage informs defaults
- Replace in-memory Registry with Postgres or Redis for persistence
