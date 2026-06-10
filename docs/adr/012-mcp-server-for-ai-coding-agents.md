# ADR 012 - MCP Server for AI Coding Agents

## Status
Accepted

## Context

AI coding agents (Claude Code, Cursor) generates code but have no native way to execute it safely. Petri provides isolated execution, but agents can only use it if it's exposed as a tool they understand.

The Model Context Protocol (MCP) is an open standard for connecting AI models to external tools. Building an MCP server makes Petri natively usable by any MCP-compatible agent.

## Decision

Add an MCP server to the `jhansi` SDK as `jhansi/mcp_server.py`. It exposes three tools:

- `create_sandbox` - creates an isolated sandbox, returns the ID
- `exec_code` - executes a command in the sandbox, returns the output
- `delete_sandbox` - tears down the sandbox

The MCP server is a lightweight adapter. It has no state, no port, no persistence. It is spawned by the agent as a subprocess and communicates over stdin/stdout using the MCP protocol via `fastmcp`.

## Consequences

- Claude Code and Cursor users can run code in Petri sandboxes without writing any SDK code
- The MCP server is distributed as part of the `jhansi` package - no separate install
- Streaming output to the agent is deferred to a future release
- Sandbox TTL in Petri handles cleanup if the agent fails to call `delete_sandbox`
