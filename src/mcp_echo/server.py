"""Echo MCP Server - FastMCP Implementation."""

import time
from datetime import UTC, datetime
from typing import Any

from dotenv import load_dotenv
from fastapi import Request
from fastapi.responses import JSONResponse
from mcp.server.fastmcp import Context, FastMCP

from .api_models import DataAnalysis, EchoDelayResponse, EchoJsonResponse, EchoMessageResponse

# Load environment variables from .env file
load_dotenv()

# Create MCP server
mcp = FastMCP("Echo")


# Health endpoint for HTTP transport
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> JSONResponse:
    """Health check endpoint for monitoring."""
    return JSONResponse({"status": "healthy", "service": "mcp-echo"})


# MCP Tools
@mcp.tool()
async def echo_message(
    message: str, uppercase: bool = False, ctx: Context[Any, Any, Any] | None = None
) -> EchoMessageResponse:
    """Echo back a message with optional formatting.

    Args:
        message: The message to echo back
        uppercase: Whether to convert the message to uppercase
        ctx: MCP context

    Returns:
        Complete echo response with metadata
    """
    if ctx:
        ctx.info(f"Echoing message (uppercase={uppercase}): {message[:50]}...")

    result_message = message.upper() if uppercase else message

    return EchoMessageResponse(
        original_message=message,
        echoed_message=result_message,
        uppercase_applied=uppercase,
        message_length=len(message),
        timestamp=datetime.now(UTC).isoformat(),
    )


@mcp.tool()
async def echo_with_delay(
    message: str, delay_seconds: float = 1.0, ctx: Context[Any, Any, Any] | None = None
) -> EchoDelayResponse:
    """Echo back a message after a simulated delay.

    Args:
        message: The message to echo back
        delay_seconds: Delay duration in seconds (max 5.0 seconds)
        ctx: MCP context

    Returns:
        Echo response with timing information
    """
    # Limit delay to maximum of 5 seconds for safety
    delay_seconds = min(float(delay_seconds), 5.0)

    if ctx:
        ctx.info(f"Echoing with {delay_seconds}s delay: {message[:50]}...")

    start_time = datetime.now(UTC)
    time.sleep(delay_seconds)
    end_time = datetime.now(UTC)

    return EchoDelayResponse(
        original_message=message,
        echoed_message=message,
        requested_delay=delay_seconds,
        actual_delay=(end_time - start_time).total_seconds(),
        start_time=start_time.isoformat(),
        end_time=end_time.isoformat(),
        timestamp=end_time.isoformat(),
    )


@mcp.tool()
async def echo_json(
    data: dict[str, Any], ctx: Context[Any, Any, Any] | None = None
) -> EchoJsonResponse:
    """Echo back structured JSON data with validation and analysis.

    Args:
        data: The JSON data to echo back
        ctx: MCP context

    Returns:
        Echo response with data analysis
    """
    import json

    if ctx:
        ctx.info(f"Echoing JSON data with {len(data)} keys...")

    # Analyze the data structure
    analysis = DataAnalysis(
        key_count=len(data),
        keys=list(data.keys()),
        data_types={key: type(value).__name__ for key, value in data.items()},
        total_size=len(json.dumps(data)),
    )

    return EchoJsonResponse(
        original_data=data,
        echoed_data=data,
        analysis=analysis,
        timestamp=datetime.now(UTC).isoformat(),
    )


# Create ASGI application for uvicorn
app = mcp.streamable_http_app()


# Cleanup on shutdown
@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Clean up resources on server shutdown."""
    # Echo server doesn't maintain persistent connections
    # but we include this for consistency
    pass
