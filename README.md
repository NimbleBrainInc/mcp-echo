# Echo MCP Server

[![mpak](https://img.shields.io/badge/mpak-registry-blue)](https://mpak.dev/packages/@nimblebraininc/echo?utm_source=github&utm_medium=readme&utm_campaign=mcp-echo)
[![NimbleBrain](https://img.shields.io/badge/NimbleBrain-nimblebrain.ai-purple)](https://nimblebrain.ai?utm_source=github&utm_medium=readme&utm_campaign=mcp-echo)
[![Discord](https://img.shields.io/badge/Discord-community-5865F2)](https://nimblebrain.ai/discord?utm_source=github&utm_medium=readme&utm_campaign=mcp-echo)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A [Model Context Protocol](https://modelcontextprotocol.io) (MCP) server that echoes messages, delays, and structured JSON data. Useful for testing MCP client integrations, verifying protocol connectivity, and validating tool call behavior.

**[View on mpak registry](https://mpak.dev/packages/@nimblebraininc/echo?utm_source=github&utm_medium=readme&utm_campaign=mcp-echo)** | **Built by [NimbleBrain](https://nimblebrain.ai?utm_source=github&utm_medium=readme&utm_campaign=mcp-echo)**

## Install

Install with [mpak](https://mpak.dev?utm_source=github&utm_medium=readme&utm_campaign=mcp-echo):

```bash
mpak install @nimblebraininc/echo
```

### Claude Code

```bash
claude mcp add echo -- mpak run @nimblebraininc/echo
```

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "echo": {
      "command": "mpak",
      "args": ["run", "@nimblebraininc/echo"]
    }
  }
}
```

See the [mpak registry page](https://mpak.dev/packages/@nimblebraininc/echo?utm_source=github&utm_medium=readme&utm_campaign=mcp-echo) for full install options.

## Tools

### echo_message

Echo back a message with optional uppercase formatting.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `message` | `string` | Yes | The message to echo back |
| `uppercase` | `boolean` | No | Convert the message to uppercase (default: `false`) |

**Example call:**

```json
{
  "name": "echo_message",
  "arguments": {
    "message": "Hello Echo!",
    "uppercase": true
  }
}
```

**Example response:**

```json
{
  "original_message": "Hello Echo!",
  "echoed_message": "HELLO ECHO!",
  "uppercase_applied": true,
  "message_length": 11,
  "timestamp": "2025-01-15T12:00:00+00:00"
}
```

### echo_with_delay

Echo back a message after a simulated delay. Useful for testing timeout handling and async behavior.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `message` | `string` | Yes | The message to echo back |
| `delay_seconds` | `number` | No | Delay in seconds, max 5.0 (default: `1.0`) |

**Example call:**

```json
{
  "name": "echo_with_delay",
  "arguments": {
    "message": "Delayed echo",
    "delay_seconds": 2.0
  }
}
```

**Example response:**

```json
{
  "original_message": "Delayed echo",
  "echoed_message": "Delayed echo",
  "requested_delay": 2.0,
  "actual_delay": 2.001,
  "start_time": "2025-01-15T12:00:00+00:00",
  "end_time": "2025-01-15T12:00:02+00:00",
  "timestamp": "2025-01-15T12:00:02+00:00"
}
```

### echo_json

Echo back structured JSON data with validation and analysis.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `data` | `object` | Yes | JSON object to echo back |

**Example call:**

```json
{
  "name": "echo_json",
  "arguments": {
    "data": {
      "name": "test",
      "count": 42,
      "active": true
    }
  }
}
```

**Example response:**

```json
{
  "original_data": {"name": "test", "count": 42, "active": true},
  "echoed_data": {"name": "test", "count": 42, "active": true},
  "analysis": {
    "key_count": 3,
    "keys": ["name", "count", "active"],
    "data_types": {"name": "str", "count": "int", "active": "bool"},
    "total_size": 42
  },
  "timestamp": "2025-01-15T12:00:00+00:00"
}
```

## Quick Start

### Local Development

```bash
git clone https://github.com/NimbleBrainInc/mcp-echo.git
cd mcp-echo

# Install dependencies
uv sync

# Run the server (stdio mode)
uv run python -m mcp_echo.server

# Or run via FastMCP
uv run fastmcp run src/mcp_echo/server.py
```

The server supports HTTP transport with:
- Health check: `GET /health`
- MCP endpoint: `POST /mcp`

## Development

```bash
# Install with dev dependencies
uv sync --group dev

# Run unit tests
make test

# Run with coverage
make test-cov

# Run all checks (format, lint, typecheck, unit tests)
make check

# Format
uv run ruff format .

# Lint
uv run ruff check .
```

### E2E Tests

End-to-end tests validate the full MCPB bundle lifecycle: building the bundle, deploying it into a Docker container, and calling tools over HTTP.

**Prerequisites:** Docker running, `mcpb` CLI installed (`npm install -g @anthropic-ai/mcpb`)

```bash
make test-e2e
```

The tests:
1. Vendor dependencies for the Docker container's Linux architecture
2. Build a `.mcpb` bundle with `mcpb pack`
3. Serve the bundle over HTTP
4. Start a `nimbletools/mcpb-python` container that downloads and runs the bundle
5. Verify the `/health` endpoint, MCP tool listing, and tool invocation via streamable HTTP

## About

Echo MCP Server is published on the [mpak registry](https://mpak.dev?utm_source=github&utm_medium=readme&utm_campaign=mcp-echo) and built by [NimbleBrain](https://nimblebrain.ai?utm_source=github&utm_medium=readme&utm_campaign=mcp-echo). mpak is an open registry for [Model Context Protocol](https://modelcontextprotocol.io) servers.

- [mpak registry](https://mpak.dev?utm_source=github&utm_medium=readme&utm_campaign=mcp-echo)
- [NimbleBrain](https://nimblebrain.ai?utm_source=github&utm_medium=readme&utm_campaign=mcp-echo)
- [MCP specification](https://modelcontextprotocol.io)
- [Discord community](https://nimblebrain.ai/discord?utm_source=github&utm_medium=readme&utm_campaign=mcp-echo)

## License

MIT
