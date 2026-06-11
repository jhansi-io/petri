# ADR 014 - Observability and Execution History

## Status
Accepted

## Context

Petri's exec endpoint streams raw stdout lines to the caller. There is no structured signal for success or failure - the caller must parse text to infer outcome. This works poorly for AI agents (Claude Code, Cursor) which need a clean, machine-readable result to decide whether to retry, fix code, or report success.

Additionally, every execution is ephemeral. Once the stream ends, the output is gone. There is no record of what ran, when, how long it took, or whether it succeeded. This makes debugging impossible and prevents any meaningful usage analysis.

Petri is an execution primitive used by multiple AI agents. Its response contract must be generic - agent-agnostic structured output that any caller can act on without parsing text.

## Decision

Replace the raw SSE line stream with two typed event types:

- `event: output` - one event per line of stdout/stderr during execution
- `event: done` - a single terminal event with structured JSON payload

The `done` payload:
```json
{
	"exit_code": 0,
	"duration_ms": 234,
	"output": "hello world\n",
	"error": null
}
```

On failure, `error` contains the last meaningful error line (e.g. `ModuleNotFoundError: No module named 'pandas'`). This gives any agent a clean signal to act on without text parsing.

Every execution is stored as a run against its sandbox. Runs are never overwritten or deleted. Each run record stores `run_id`, `sandbox_id`, `started_at`, `completed_at`, `duration_ms`, `exit_code`, `error`, and full `output`. Multiple runs against the same sandbox are stored independently -  a high run count signals an gent retry loop.

Sandboxes are no longer hard deleted. On `DELETE /v1/sandboxes/{id}`, the sandbox is marked `status: deleted` with a `deleted_at` timestamp. The row is retained in SQLite. A composite index on `(status, created_at)` keeps queries fast as the table grows. A separate archive table is deferred.

Two optional fields added to `CreateSandboxRequest`:

- `agent` - the calling agent (e.g. `claude-code`, `cursor`)
- `created_by` - the user or identifier passed by the caller, defaults to `unknown`

When auth lands, `created_by` will be populated from the API key identity automatically.

`GET /v1/metrics` returns a JSON snapshot of Petri's current state - active sandboxes, total sandboxes, total runs, failed runs, success rate, average duration,  and breakdown by agent. All data queried from SQLite at request time.

Run output is stored as flat files under `PETRI_WORKSPACE_ROOT/{sandbox_id}/runs/{run_id}.log`. A configurable cap `PETRI_LOG_MAX_MB` (default: `500`) limits total log storage. When the cap is exceeded, the oldest run logs are evicted first. The run record in SQLite is retained  -only the output file is deleted.

## Consequences
 
- Any AI agent receives a structured, machine-readable execution result — no text parsing required
- Agents can reliably detect success vs failure and act accordingly (retry, fix, report)
- Full execution history is queryable — run counts, failure rates, duration trends
- Operators can observe sandbox usage split by agent and creator
- Log storage is bounded and self-managing
- No new infrastructure dependencies — SQLite and flat files only
- Soft delete is a one-way schema change; hard deletes are no longer supported
- `PETRI_LOG_MAX_MB` must be documented in self-hosting config
