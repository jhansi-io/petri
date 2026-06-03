# ADR 002 - Sandbox ID Generation

## Status
Accepted

## Context
Sandbox IDs are exposed in URLs. We needed a way to generate them
that is unique and safe.

## Decision
Use `secrets.token_hex(16)` prefixed with `sb_` - e.g. `sb_3f9a...`

## Alternatives Considered
- **uuid4()** - random and unique but signals "identifier" not "secret".
  Fine for internal IDs, wrong intent for exposed URLs

## Consequences
- IDs are cryptographically random - safe to expose in URLs
 - `secrets` module signals security intent clearly to future developers
 - 128 bits of entropy - practically unguessable
