# ADR-006: Auto Dependency Detection and Installation

**Status:** Accepted

## Context

Users upload and execute code in sandboxes. Currently they must manually ensure
dependencies are available. This creates friction — the platform should handle
it invisibly.

## Decision

At exec time, detect third-party imports in the file being run and install
missing dependencies inside the container, into the sandbox workspace. Dependencies
persist across runs on the same sandbox — install once, reuse on subsequent execs.

## Languages and Tools

| Language | Detection | Installation | Registry |
|----------|-----------|--------------|----------|
| Python | `pipreqs` | `pip install --target /sandbox/deps` | pypi.org |
| Node | Parse `require`/`import` | `npm install` | registry.npmjs.org |
| Go | Parse `import` block | `go get` | proxy.golang.org |
| Java | Parse `import` statements | `mvn dependency:resolve` | repo.maven.apache.org |

## Trust Boundary

jhansi.io guarantees isolation. The user is responsible for what their code does.

## Egress

Containers may reach official package registries only. All other egress is blocked
by default. Self-hosters own their own network policy.

## Convention

One sandbox = one project. Not enforced in v0.3 — SDK will enforce later.

## Consequences

- First exec is slower (install time). Subsequent execs are fast.
- Workspace grows over time as deps accumulate. Cleanup is out of scope for v0.3.
