# ADR 011 - Streaming Execution via SSE

## Status
Accepted

## Context

The `/exec` endpoint currently blocks until execution completes and returns all output as a single JSON response. For long-running commands and dep installs, this gives the user no feedback. Streaming output line-by-line improves UX significantly

## Decision

- **Replace `/exec`, don't add a new endpoint.** Pre-1.0, no real users, SDK is ours to update. No meaningful compatibility burden.
- **SSE over chunked response.** SSE is a proper protocol with event framing - easier to consume in the SDK and future UI. Chunked is just raw bytes with no structure.
- **Deps install is silent; exec output is streamed.** Deps install is infrastructure noise. The user cares about their code's output, not pip's. Keeps the stream clean.
- **Test mode streams too.** No reason to treat it differently - seeing pytest results line-by-line is more useful than waiting for the full suite to finish.
- **`subprocess.Popen` replaces `subprocess.run` for exec.** `Popen` gives us a live stdout handle to iterate over. `run` waits for completion.

## Consequences

- `executor.py`: add `run_stream()` generator using `Popen`, returning lines as they arrive
- `main.py`: `exec_sandbox` returns `StreamingResponse` with `text/event-stream` content type
- SDK `exec()` method will need updating in v0.7 to consume SSE
