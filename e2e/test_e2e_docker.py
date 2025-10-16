"""End-to-end tests for Docker container deployment."""

import subprocess
import time

import pytest
import requests
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

# Test configuration
IMAGE_NAME = "mcp-echo"
CONTAINER_NAME = "mcp-echo-test"
PORT = 8000
BASE_URL = f"http://localhost:{PORT}"


@pytest.fixture(scope="module")
def docker_container():
    """Build and run Docker container for testing."""
    # Build the image
    print("Building Docker image...")
    build_result = subprocess.run(
        ["docker", "build", "-t", IMAGE_NAME, "."],
        capture_output=True,
        text=True,
    )
    assert build_result.returncode == 0, f"Docker build failed: {build_result.stderr}"

    # Run the container
    print("Starting Docker container...")
    subprocess.run(
        [
            "docker",
            "run",
            "-d",
            "--name",
            CONTAINER_NAME,
            "-p",
            f"{PORT}:{PORT}",
            IMAGE_NAME,
        ],
        check=True,
    )

    # Wait for container to be ready
    print("Waiting for container to be ready...")
    max_attempts = 30
    for _ in range(max_attempts):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                print("Container is ready!")
                break
        except requests.RequestException:
            pass
        time.sleep(1)
    else:
        # Cleanup on failure
        subprocess.run(["docker", "stop", CONTAINER_NAME], check=False)
        subprocess.run(["docker", "rm", CONTAINER_NAME], check=False)
        pytest.fail("Container failed to start within timeout")

    yield

    # Cleanup
    print("Stopping and removing container...")
    subprocess.run(["docker", "stop", CONTAINER_NAME], check=True)
    subprocess.run(["docker", "rm", CONTAINER_NAME], check=True)


def test_health_endpoint(docker_container):
    """Test that the health endpoint returns successfully."""
    response = requests.get(f"{BASE_URL}/health", timeout=5)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "mcp-echo"


@pytest.mark.asyncio
async def test_mcp_tools_list(docker_container):
    """Test that the MCP tools/list endpoint returns all expected tools using MCP client."""
    # Use the official MCP Python SDK client
    async with streamablehttp_client(f"{BASE_URL}/mcp") as (read, write, _):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()

            # List all tools
            tools_response = await session.list_tools()
            tools_list = tools_response.tools

            assert tools_list, "No tools returned from MCP server"

            tool_names = {tool.name for tool in tools_list}

            # Verify all expected tools are registered
            expected_tools = {
                "echo_message",
                "echo_with_delay",
                "echo_json",
            }

            assert expected_tools.issubset(tool_names), (
                f"Missing tools: {expected_tools - tool_names}"
            )

            # Verify each tool has required fields
            for tool in tools_list:
                assert tool.name
                assert tool.description
                assert tool.inputSchema

            print(f"✓ Successfully verified {len(tools_list)} MCP tools")


def test_container_shutdown(docker_container):
    """Test that container shuts down gracefully."""
    # Stop container
    result = subprocess.run(
        ["docker", "stop", CONTAINER_NAME],
        capture_output=True,
        text=True,
        timeout=10,
    )

    assert result.returncode == 0, "Container did not stop gracefully"

    # Verify container is stopped
    result = subprocess.run(
        ["docker", "ps", "-a", "-f", f"name={CONTAINER_NAME}", "--format", "{{.Status}}"],
        capture_output=True,
        text=True,
    )

    assert "Exited" in result.stdout, "Container is not in exited state"
    print("✓ Container shut down gracefully")
