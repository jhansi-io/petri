# ADR-002: HTTP Wire Contract

## Status: Accepted
Date: 2026-07-16

## Context:

The Go engine exposes an HTTP API consumed by the jhansi SDK. The SDK has no
live users yet, so there is no external contract to preserve.

## Decision

The engine owns the wire contract; the SDK follows the engine, not vice versa.

Response DTOs start minimal - `id` and `status` only - and grow fields (language,
etc.) only when the engine actually uses them. The DTO is a seperate translation
layer in the httpapi package; domain structs stay lean and are never serialized
directly.

Paths, verbs, and status codes carry over from Python v0.11 (POST /v1/sandboxes
-> 201, etc.). Response bodies are redesigned freely.

## Consequences

- Fast iteration on the API without SDK-coordination overhead, while it's safe.
- DTOs and domain structs diverge deliberately; mapping lives in httpapi.
- Once the SDK has live users, tis reverses: the contract becomes fixed and
  changes require versioning.
