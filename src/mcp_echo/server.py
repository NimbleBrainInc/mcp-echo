"""Echo MCP Server - FastMCP Implementation."""

import logging
import signal
import sys
import time
from datetime import UTC, datetime
from typing import Any

from dotenv import load_dotenv
from fastmcp import Context, FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

from .api_models import DataAnalysis, EchoDelayResponse, EchoJsonResponse, EchoMessageResponse

# Debug logging for container diagnostics
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("mcp_echo")


# Signal handler for debugging
def _signal_handler(signum: int, frame: object) -> None:
    logger.warning("Received signal %s (%s)", signum, signal.Signals(signum).name)


# Register signal handlers to see what signals we receive
for sig in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
    try:
        signal.signal(sig, _signal_handler)
        logger.debug("Registered handler for %s", sig.name)
    except (ValueError, OSError) as e:
        logger.debug("Could not register handler for %s: %s", sig.name, e)

logger.info("Echo server module loading...")

# Load environment variables from .env file
load_dotenv()

# Create MCP server
logger.debug("Creating FastMCP instance...")
mcp = FastMCP("Echo")
logger.debug("FastMCP instance created")


# Health endpoint for HTTP transport
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> JSONResponse:
    """Health check endpoint for monitoring."""
    return JSONResponse({"status": "healthy", "service": "mcp-echo"})


# MCP Tools
@mcp.tool()
async def echo_message(
    message: str, uppercase: bool = False, ctx: Context | None = None
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
        await ctx.info(f"Echoing message (uppercase={uppercase}): {message[:50]}...")

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
    message: str, delay_seconds: float = 1.0, ctx: Context | None = None
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
        await ctx.info(f"Echoing with {delay_seconds}s delay: {message[:50]}...")

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
async def echo_json(data: dict[str, Any], ctx: Context | None = None) -> EchoJsonResponse:
    """Echo back structured JSON data with validation and analysis.

    Args:
        data: The JSON data to echo back
        ctx: MCP context

    Returns:
        Echo response with data analysis
    """
    import json

    if ctx:
        await ctx.info(f"Echoing JSON data with {len(data)} keys...")

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


# Create ASGI application for HTTP deployment
logger.debug("Creating http_app()...")
app = mcp.http_app()
logger.info("ASGI app created successfully, ready for uvicorn")

# Stdio entrypoint for Claude Desktop / mpak
if __name__ == "__main__":
    logger.info("Running in stdio mode")
    mcp.run()
