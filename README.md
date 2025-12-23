# MCP Echo Service

[![NimbleTools Registry](https://img.shields.io/badge/NimbleTools-Registry-green)](https://github.com/nimbletoolsinc/mcp-registry)
[![NimbleBrain Platform](https://img.shields.io/badge/NimbleBrain-Platform-blue)](https://www.nimblebrain.ai)
[![Discord](https://img.shields.io/badge/Discord-%235865F2.svg?logo=discord&logoColor=white)](https://www.nimblebrain.ai/discord?utm_source=github&utm_medium=readme&utm_campaign=mcp-echo&utm_content=discord-badge)

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/NimbleBrainInc/mcp-echo/actions/workflows/build-bundle.yml/badge.svg)](https://github.com/NimbleBrainInc/mcp-echo/actions)

## About

A Model Context Protocol (MCP) service that provides echo tools for testing MCP protocol functionality.

## Features

- **echo_message**: Echo back a message with optional uppercase formatting
- **echo_with_delay**: Echo back a message after a simulated delay (max 5 seconds)
- **echo_json**: Echo back structured JSON data with analysis

## Quick Start

### Local Development

```bash
# Clone the repository
git clone https://github.com/NimbleBrainInc/mcp-echo.git
cd mcp-echo

# Install dependencies with uv
uv sync

# Run the server
uv run python -m mcp_echo.server

# Or run via FastMCP
uv run fastmcp run src/mcp_echo/server.py
```

The server will start on `http://localhost:8000` with:
- Health check: `GET /health`
- MCP endpoint: `POST /mcp`

### Building MCPB Bundle

This server is distributed as an MCPB bundle. To build locally:

```bash
# Install mcpb CLI (requires Node.js)
npm install -g @anthropic-ai/mcpb

# Build the bundle
mcpb pack . mcp-echo.mcpb
```

## MCP Protocol Support

This server implements the full MCP (Model Context Protocol) specification:

- **Transport**: Streamable HTTP with Server-Sent Events (SSE)
- **Session Management**: Proper initialization handshake required
- **Protocol Version**: 2024-11-05
- **Framework**: FastMCP
- **Python Version**: 3.13+

### Session Management

The server requires proper MCP initialization:

1. **Initialize**: Send `initialize` request to establish session
2. **Initialized**: Send `notifications/initialized` notification
3. **Tools**: Use session ID for all subsequent requests

## API Usage

### Complete MCP Example

```bash
# Step 1: Initialize session
INIT_RESPONSE=$(curl -s -i -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": {"name": "example-client", "version": "1.0.0"}
    },
    "id": 1
  }')

# Extract session ID
SESSION_ID=$(echo "$INIT_RESPONSE" | grep -i "mcp-session-id" | cut -d' ' -f2 | tr -d '\r')

# Step 2: Send initialized notification
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  -d '{"jsonrpc": "2.0", "method": "notifications/initialized"}'

# Step 3: List available tools
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 2}'

# Step 4: Call echo_message tool
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "echo_message",
      "arguments": {"message": "Hello Echo!", "uppercase": true}
    },
    "id": 3
  }'
```

### Simple Health Check

```bash
curl http://localhost:8000/health
```

## Development

### Testing

```bash
# Install with dev dependencies
uv sync --group dev

# Run unit tests
uv run pytest tests/

# Run with coverage
uv run pytest tests/ --cov=mcp_echo
```

### E2E Tests

E2E tests require the [mcpb CLI](https://github.com/modelcontextprotocol/mcpb) and Docker:

```bash
# Install mcpb CLI
npm install -g @anthropic-ai/mcpb

# Run e2e tests
uv run pytest e2e/
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## About

Part of the [NimbleTools](https://www.nimbletools.ai) ecosystem.
From the makers of [NimbleBrain](https://www.nimblebrain.ai).

## License

MIT License - see LICENSE file for details.

## Links

Part of the [NimbleTools Registry](https://github.com/nimbletoolsinc/mcp-registry), an open source collection of production-ready MCP servers. For enterprise deployment, check out [NimbleBrain](https://www.nimblebrain.ai).

- [MCPB CLI](https://github.com/modelcontextprotocol/mcpb)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [MCP Documentation](https://modelcontextprotocol.io)
