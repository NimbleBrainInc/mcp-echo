# MCP Echo Service

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
uv run python server.py

# Or install in editable mode
uv pip install -e .
python server.py
```

The server will start on `http://localhost:8000` with:
- Health check: `GET /health`
- MCP endpoint: `POST /mcp/` (note the trailing slash)

### Docker

```bash
# Build the image
docker build -t nimbletools/mcp-echo .

# Run the container
docker run -p 8000:8000 nimbletools/mcp-echo
```

## MCP Protocol Support

This server implements the full MCP (Model Context Protocol) specification:

- **Transport**: Streamable HTTP with Server-Sent Events (SSE)
- **Session Management**: Proper initialization handshake required
- **Protocol Version**: 2024-11-05
- **Framework**: FastMCP 2.11.2
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
INIT_RESPONSE=$(curl -s -i -X POST http://localhost:8000/mcp/ \
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
curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  -d '{"jsonrpc": "2.0", "method": "notifications/initialized"}'

# Step 3: List available tools
curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 2}'

# Step 4: Call echo_message tool
curl -X POST http://localhost:8000/mcp/ \
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

# Step 5: Call echo_with_delay tool  
curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "echo_with_delay",
      "arguments": {"message": "Delayed Echo", "delay_seconds": 1}
    },
    "id": 4
  }'

# Step 6: Call echo_json tool
curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "echo_json", 
      "arguments": {"data": {"test": "value", "number": 42}}
    },
    "id": 5
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

# Run tests (includes async MCP client tests)
uv run python -m pytest

# Run with coverage
uv run python -m pytest --cov=server

# Run specific test
uv run python -m pytest tests/test_server.py::test_echo_message_tool -v
```

### Building and Deployment

```bash
# Build Docker image
docker build -t mcp-echo .

# Test the container
docker run -d --name mcp-test -p 8000:8000 mcp-echo

# Check health
curl http://localhost:8000/health

# Clean up
docker stop mcp-test && docker rm mcp-test
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
