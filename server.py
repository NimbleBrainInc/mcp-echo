#!/usr/bin/env python3
"""
Echo MCP Server - FastMCP Implementation
"""

import json
import time
from datetime import datetime, timezone

from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

# Create FastMCP server
mcp = FastMCP("Echo MCP Server")

@mcp.tool
def echo_message(message: str, uppercase: bool = False) -> str:
    """Echo back a message with optional formatting"""
    result_message = message.upper() if uppercase else message
    
    result = {
        "original_message": message,
        "echoed_message": result_message,
        "uppercase_applied": uppercase,
        "message_length": len(message),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    return json.dumps(result, indent=2)

@mcp.tool
def echo_with_delay(message: str, delay_seconds: float = 1.0) -> str:
    """Echo back a message after a simulated delay"""
    # Limit delay to maximum of 5 seconds for safety
    delay_seconds = min(float(delay_seconds), 5.0)
    
    start_time = datetime.now(timezone.utc)
    time.sleep(delay_seconds)
    end_time = datetime.now(timezone.utc)
    
    result = {
        "original_message": message,
        "echoed_message": message,
        "requested_delay": delay_seconds,
        "actual_delay": (end_time - start_time).total_seconds(),
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "timestamp": end_time.isoformat()
    }
    
    return json.dumps(result, indent=2)

@mcp.tool
def echo_json(data: dict) -> str:
    """Echo back structured JSON data with validation"""
    # Analyze the data structure
    analysis = {
        "key_count": len(data),
        "keys": list(data.keys()),
        "data_types": {key: type(value).__name__ for key, value in data.items()},
        "total_size": len(json.dumps(data))
    }
    
    result = {
        "original_data": data,
        "echoed_data": data,
        "analysis": analysis,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    return json.dumps(result, indent=2)

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request):
    return JSONResponse({"status": "healthy"})

def main():
    """Main entry point"""
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=8000,
    )

if __name__ == "__main__":
    main()