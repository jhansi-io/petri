# ADR 001 - Code Execution Strategy

## Status
Accepted

## Context
Petri needs to execute untrusted code inside isolated Docker containers.
Two approaches were considered for passing code the container.

## Decision
Write code to a temp file on the host, mount into the container, execute it.

## Alternatives Considered
- **Stdin injection** - pipe code directly into the container via stdin.
  Cleaner but harder to debug and awkward for multi-file code.

## Consequences
- Temp files must be cleaned up after every execution
- Easy to inspect what ran - good for debugging and audit
- Will revisit when moving to Firecracker microVMS at scale

## Future
If disk footprint becomes a security or performance concern at scale, 
switch to stdin or redesign for Firecracker.
