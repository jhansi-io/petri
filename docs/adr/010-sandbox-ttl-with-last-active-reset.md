# ADR 010 - Sandbox TTL with Last-Active Reset

## Status
Accepted

## Context

Sandboxes are persistent (since ADR 009) but nothing cleans them up.
Abandoned sandboxes leak disk and memory over time.

## Decision

Add an `expires_at` field to every sandbox. Default TTL is 1 hour. Every `exec` call resets `expires_at` to `now + 1 hour`. A background task runs periodically, finds sandboxes where `expires_at < now`, stops their containers and removes them from the registry.

## Consequences

- Abandoned sandboxes are automatically cleaned up after 1 hour of inactivity.
- Active sandboxes (receiving exec calls) are never killed
- TTL is configurable via `PETRI_SANDBOX_TTL_SECONDS` environment variable
- Default TTL is 3600 seconds (1 hour)
