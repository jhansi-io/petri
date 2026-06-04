# ADR 005 - Persistent Workspace Model

## Status
Accepted

## Context
In v0.1, code is sent as a raw string in the request body on every execution. This has three problems:

1. Single file only - no multi-file projects, no dependencies
2. Code resent on every exec - wasteful, adds latency
3. No delta sync - even one character change requires a full send

## Decision
Introduce a persistent workspace per sandbox - a dedicated folder on disk that survives between executions.

Users upload files once. Exec targets a named file inside the workspace. Only changed files need to be re-uploaded.

The sandbox container mounts the workspace folder at `/sandbox` on each run.

## Consequences
- Multi-file projects are now possible
- Exec requests no longer carry code - just filename
- Delta sync becomes possible - upload only what changed
- Workspace must be on a host-mounted volume when Petri runs in a container
- A new endpoint is needed: POST /v1/sandboxes/{id}/files

## Architecture

### v0.1 — Ephemeral execution
```mermaid
sequenceDiagram
    Client->>Petri: POST /exec (code as string)
    Petri->>TempFile: write code
    Petri->>Container: docker run (mount temp file)
    Container->>Petri: output
    Petri->>TempFile: delete
    Petri->>Client: output
```

### v0.2 — Persistent workspace
```mermaid
sequenceDiagram
    Client->>Petri: POST /files (upload main.py)
    Petri->>Workspace: save to sb_abc123/main.py
    Client->>Petri: POST /exec (filename: main.py)
    Petri->>Container: docker run (mount sb_abc123/)
    Container->>Petri: output
    Petri->>Client: output
```
