# ADR 007 - Test Mode

**Status:** Accepted

## Context

AI-generated code produces scripts, web apps, and backend services. Two problems
need solving:

1. **Servers can't run with plain exec** — `subprocess.run` waits for the process
   to exit. A server never exits, so Petri hangs indefinitely.
2. **Output alone is not enough** — you need to run a test suite against the code
   to verify it actually works before it touches production.

Test mode addresses both. For scripts, tests run after the process exits. For
servers, the process runs in the background, tests execute, then it is killed.

Serve mode — exposing a live preview URL for human interaction — is a separate
concern and is deferred to v0.5.

## Decision

Extend the exec endpoint with two changes:

1. **Replace `filename` with `command`** — the user passes the full command to run,
   mirroring what they would type in their terminal (e.g. `python script.py`,
   `uvicorn app:app`). This gives users full control and removes the assumption
   that Petri knows how to invoke their code.
2. **Add optional `test` boolean** — when `true`, Petri runs the language-appropriate
   test runner after the command completes or in parallel for servers, then returns
   results.

## Execution Behaviour

| Code type | `test: false`              | `test: true`                                      |
|-----------|----------------------------|---------------------------------------------------|
| Script    | Run command, return output | Run command, then run test suite, return results  |
| Server    | Hangs — not supported      | Start in background, run test suite, kill, return results |

Everything runs inside a single container.

## API Change

```json
POST /v1/sandboxes/{id}/exec

{
  "command": "uvicorn app:app",
  "test": true
}
```

`test` is optional and defaults to `false`. When omitted, behaviour is identical
to current exec — run the command, wait for it to exit, return output.

## Test Runners

Test discovery is automatic per language — no test file needs to be specified:

| Language | Runner  | Discovery          |
|----------|---------|--------------------|
| Python   | pytest  | `tests/` directory |
| Node     | jest    | `*.test.js` files  |
| Go       | go test | `./...`            |
| Java     | mvn test | Maven/Gradle standard |

## Convention

The user uploads the full project to the sandbox workspace — app code, test suite,
and any dependency manifests. One sandbox = one project.

## Consequences

- `filename` is replaced by `command` — a breaking change to the exec API.
- Existing script behaviour is preserved — `test: false` is the default.
- When `test: true`, Petri always waits 2 seconds before running the test suite.
  This ensures servers have time to start regardless of how they are invoked.
- Serve mode (long-running preview URL) is deferred to v0.5.
