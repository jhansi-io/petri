# ADR-001: Sandbox domain model

## Status: Accepted
Date: 2026-07-16

## Context

Agent workflows create a sandbox once and run many executions inside it
over the sandbox's life. A single failed execution must not tear down the
sandbox, or every iterative agent loop pays a cold-start per step. This
ADR fixes the aggregate boundary and the state machines; behaviour layered
on top (timeouts, concurrency, serving) is deferred.

## Decision

- Sandbox is the aggregate. Runs live inside it.
- Sandbox states: CREATING → READY → EXPIRED | DELETED | ERROR
- Run states: PREPARING → RUNNING → SUCCEEDED | FAILED | TIMED_OUT | ERROR
- Serial execution: one live Run per sandbox. A new exec while a Run is
  RUNNING is rejected, not queued.
- Failed run ≠ failed sandbox: a Run reaching FAILED/TIMED_OUT/CANCELLED
  leaves the sandbox in READY.

## Consequences

- Enables iterative agent loops without cold-start per exec.
- Concurrency, idle-vs-execution timeouts, and long-lived serving are
  deferred to later ADRs; none require changing this boundary.
- Sandbox and Run are seperate entities with seperate lifecycles from day one.
