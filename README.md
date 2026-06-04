# Petri

Sandboxed execution engine for untrusted code.

Petri is the execution layer behind [Jhansi.io](https://jhansi.io) — 
it runs AI-generated code safely in isolated Docker containers, 
streams output, and tears down cleanly. No eval(). No escape.

---

## Why Petri?

AI agents generate code. Running it is dangerous:

- `eval()` = Remote Code Execution risk
- Secrets can be exfiltrated
- No audit trail for compliance (FCA, SOC2, EU AI Act)

Petri solves the runtime problem — hard-isolated execution, 
one container per run, zero trust by default.

---

## Quick Start

**Requirements:** Python 3.12+, Docker, Poetry

```bash
git clone https://github.com/jhansi-io/petri.git
cd petri
poetry install
make run
```

Petri is now running at `http://localhost:8000`.

---

## API

### Create a sandbox
```bash
curl -X POST http://localhost:8000/v1/sandboxes \
  -H "Content-Type: application/json" \
  -d '{"language": "python"}'
```

### Run code
```bash
curl -X POST http://localhost:8000/v1/sandboxes/<id>/exec \
  -H "Content-Type: application/json" \
  -d '{"code": "print(\"hello from petri!\")"}'
```

### Get status
```bash
curl http://localhost:8000/v1/sandboxes/<id>
```

### Delete sandbox
```bash
curl -X DELETE http://localhost:8000/v1/sandboxes/<id>
```

---

## Multi-Language Support

| Language | Parameter  |
|----------|------------|
| Python   | `python`   |
| Node.js  | `node`     |
| Go       | `go`       |

---

## Development

```bash
make test       # run tests
make lint       # check code style
make fmt        # format code
make typecheck  # run mypy
make clean      # remove cache files
```

Tests are split into unit tests (no Docker needed) and integration 
tests (`test_executor.py` requires Docker running locally).

---

## Architecture Decisions

All design decisions are documented in [`docs/adr/`](docs/adr/).

---

## License

Apache 2.0 — see [LICENSE](LICENSE).

Part of the [Jhansi.io](https://jhansi.io) platform.
