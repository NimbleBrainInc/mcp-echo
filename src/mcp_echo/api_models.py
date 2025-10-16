"""Pydantic models for Echo MCP Server responses."""

from typing import Any

from pydantic import BaseModel, Field


class EchoMessageResponse(BaseModel):
    """Response model for echo_message tool."""

    original_message: str = Field(..., description="The original message sent")
    echoed_message: str = Field(..., description="The echoed message (possibly transformed)")
    uppercase_applied: bool = Field(..., description="Whether uppercase transformation was applied")
    message_length: int = Field(..., description="Length of the original message")
    timestamp: str = Field(..., description="ISO 8601 timestamp of the echo operation")


class EchoDelayResponse(BaseModel):
    """Response model for echo_with_delay tool."""

    original_message: str = Field(..., description="The original message sent")
    echoed_message: str = Field(..., description="The echoed message")
    requested_delay: float = Field(..., description="Requested delay in seconds")
    actual_delay: float = Field(..., description="Actual delay experienced in seconds")
    start_time: str = Field(..., description="ISO 8601 timestamp when delay started")
    end_time: str = Field(..., description="ISO 8601 timestamp when delay ended")
    timestamp: str = Field(..., description="ISO 8601 timestamp of the operation")


class DataAnalysis(BaseModel):
    """Analysis metadata for JSON data."""

    key_count: int = Field(..., description="Number of keys in the data")
    keys: list[str] = Field(..., description="List of all keys in the data")
    data_types: dict[str, str] = Field(..., description="Mapping of keys to their data types")
    total_size: int = Field(..., description="Total size of the JSON data in bytes")


class EchoJsonResponse(BaseModel):
    """Response model for echo_json tool."""

    original_data: dict[str, Any] = Field(..., description="The original JSON data sent")
    echoed_data: dict[str, Any] = Field(..., description="The echoed JSON data")
    analysis: DataAnalysis = Field(..., description="Analysis of the data structure")
    timestamp: str = Field(..., description="ISO 8601 timestamp of the operation")
