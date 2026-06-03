# ADR 004 - Executor stderr Handling

## Status
Accepted

## Context
When docker pulls an image for the first time, it writes progress
output to stderr on the host. This was leaking into the captured
output and failing tests.

We also need to capture stderr from the code itself (e.g. syntax
errors, runtime exceptions) - not just stdout.

## Decision
Use `sh -c "runner /code.ext 2>&1"` inside the container.
Set `stderr=subprocess.DEVNULL` on the host subprocess call.

- `2>&1` - merges code's stderr into stdout inside the container
- `DEVNULL` - discards the Docker's own host-level stderr (pull noise)

## Alternatives Considered
- **capture_output=True** - captures everything including Docker pull
  noise, leaks into output and breaks tests.
- **stderr=subprocess.PIPE seperately** - still captures Docker noise,
  no clean way to seperate it from code stderr.

## Consequences
- Code stderr (errors, exceptions) is captured and returned to caller
- Docker pull noise is silently discarded
- Host-level Docker errors (e.g. image not found) are also discarded - 
  acceptable for MVP, revisit when we add proper error handling

## Future
- Pre-pull images at startup to avoid first-run noise entirely
- Add structured error handling to distinguish Docker errors from code errors
