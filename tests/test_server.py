#!/usr/bin/env python3
"""Tests for echo MCP server"""

import json
import pytest
from fastmcp import Client
from server import mcp


@pytest.fixture
def mcp_server():
    """Return the MCP server instance"""
    return mcp


@pytest.mark.asyncio
async def test_echo_message_tool(mcp_server):
    """Test echo_message tool functionality"""
    async with Client(mcp_server) as client:
        result = await client.call_tool("echo_message", {
            "message": "Hello World", 
            "uppercase": True
        })
        
        # Parse the JSON result
        result_data = json.loads(result.data)
        assert result_data["original_message"] == "Hello World"
        assert result_data["echoed_message"] == "HELLO WORLD" 
        assert result_data["uppercase_applied"] == True
        assert result_data["message_length"] == 11
        assert "timestamp" in result_data


@pytest.mark.asyncio
async def test_echo_message_tool_basic(mcp_server):
    """Test echo_message tool without uppercase"""
    async with Client(mcp_server) as client:
        result = await client.call_tool("echo_message", {"message": "hello world"})
        
        # Parse the JSON result
        result_data = json.loads(result.data)
        assert result_data["original_message"] == "hello world"
        assert result_data["echoed_message"] == "hello world"
        assert result_data["uppercase_applied"] == False
        assert result_data["message_length"] == 11
        assert "timestamp" in result_data


@pytest.mark.asyncio
async def test_echo_with_delay_tool(mcp_server):
    """Test echo_with_delay tool functionality"""
    async with Client(mcp_server) as client:
        result = await client.call_tool("echo_with_delay", {
            "message": "Delayed message",
            "delay_seconds": 0.1
        })
        
        # Parse the JSON result
        result_data = json.loads(result.data)
        assert result_data["original_message"] == "Delayed message"
        assert result_data["echoed_message"] == "Delayed message"
        assert result_data["requested_delay"] == 0.1
        assert result_data["actual_delay"] >= 0.1
        assert "start_time" in result_data
        assert "end_time" in result_data
        assert "timestamp" in result_data


@pytest.mark.asyncio
async def test_echo_with_delay_max_limit(mcp_server):
    """Test echo_with_delay respects maximum delay limit"""
    async with Client(mcp_server) as client:
        result = await client.call_tool("echo_with_delay", {
            "message": "Long delay test",
            "delay_seconds": 10.0  # Above the 5s limit
        })
        
        # Parse the JSON result
        result_data = json.loads(result.data)
        # Should be capped at 5 seconds
        assert result_data["requested_delay"] == 5.0
        assert result_data["original_message"] == "Long delay test"
        assert result_data["echoed_message"] == "Long delay test"


@pytest.mark.asyncio
async def test_echo_json_tool(mcp_server):
    """Test echo_json tool functionality"""
    test_data = {
        "key1": "value1",
        "key2": 123,
        "key3": True,
        "nested": {"a": 1, "b": 2}
    }
    
    async with Client(mcp_server) as client:
        result = await client.call_tool("echo_json", {"data": test_data})
        
        # Parse the JSON result
        result_data = json.loads(result.data)
        assert result_data["original_data"] == test_data
        assert result_data["echoed_data"] == test_data
        assert "analysis" in result_data
        assert "timestamp" in result_data
        
        analysis = result_data["analysis"]
        assert analysis["key_count"] == len(test_data)
        assert set(analysis["keys"]) == set(test_data.keys())
        assert "data_types" in analysis
        assert "total_size" in analysis


@pytest.mark.asyncio
async def test_tools_list(mcp_server):
    """Test that tools are properly registered"""
    async with Client(mcp_server) as client:
        tools = await client.list_tools()
        
        assert len(tools) == 3
        tool_names = [tool.name for tool in tools]
        expected_tools = ["echo_message", "echo_with_delay", "echo_json"]
        for expected_tool in expected_tools:
            assert expected_tool in tool_names
        
        # Check tool descriptions
        echo_message_tool = next(t for t in tools if t.name == "echo_message")
        assert "Echo back a message with optional formatting" in echo_message_tool.description
        
        echo_delay_tool = next(t for t in tools if t.name == "echo_with_delay")
        assert "Echo back a message after a simulated delay" in echo_delay_tool.description
        
        echo_json_tool = next(t for t in tools if t.name == "echo_json")
        assert "Echo back structured JSON data with validation" in echo_json_tool.description


@pytest.mark.asyncio
async def test_invalid_tool(mcp_server):
    """Test calling invalid tool"""
    async with Client(mcp_server) as client:
        try:
            await client.call_tool("invalid_tool", {})
            assert False, "Should have raised an exception"
        except Exception as e:
            # Should raise an exception for invalid tool
            assert "invalid_tool" in str(e).lower() or "not found" in str(e).lower()


@pytest.mark.asyncio
async def test_echo_message_missing_required_param(mcp_server):
    """Test echo_message with missing required message parameter"""
    async with Client(mcp_server) as client:
        try:
            await client.call_tool("echo_message", {"uppercase": True})
            assert False, "Should have raised an exception"
        except Exception as e:
            # Should raise an exception for missing required parameter
            assert "message" in str(e).lower() or "required" in str(e).lower()