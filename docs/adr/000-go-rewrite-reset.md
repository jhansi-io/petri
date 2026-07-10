# ADR-000: Go rewrite and version reset

Status: Accepted
Date: 2026-07-10

## Context

Petri was built in Python (FastAPI) through v0.11.0. We are rewriting it
in Go in the same repo (jhansi-io/petri). The driver is foundation, not
performance: single-binary distribution and container-runtime/distributed-systems depth. This ADR records the reset itself, not a technical decision.

## Decision

- The Python line is frozen at the `v0.11.0` tag (recoverable via
  `git checkout v0.11.0`). `main` becomes Go. The rewrite does not merge back.
- Python ADRs 001-015 belong to the frozen line. Go ADRs start fresh from
  ADR-001.
- The Go repo version resets to 0.1.0 and climbs toward a single-binary v1.0
- Component versions (Petri, SDK) run independently pre-1.0. They converge
  at 1.0 when the product is usable end-to-end.
- Featurebase tracks the jhansi product, not component versions, and is
  unaffected by this reset.

## Consequences

- Two ADR-001s exist in git hisroty (Python and Go lines); this record
  disambiguates them.
- No migration path from Python to Go - the rewrite is a clean line.
- The repo's next tag is 0.1.0.
