"""End-to-end tests for MCPB bundle deployment."""

import subprocess
import tempfile
import time
from pathlib import Path

import pytest
import requests
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from pytest_httpserver import HTTPServer
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs

from .conftest import (
    BASE_IMAGE,
    BUILD_SCRIPT,
    BUNDLE_NAME,
    BUNDLE_VERSION,
    CONTAINER_PORT,
)


def build_bundle(output_dir: Path) -> Path:
    """Build MCPB bundle using the build script."""
    result = subprocess.run(
        [str(BUILD_SCRIPT), str(output_dir), BUNDLE_VERSION],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Bundle build failed: {result.stderr}")

    bundle_path = output_dir / f"{BUNDLE_NAME}-v{BUNDLE_VERSION}.mcpb"
    if not bundle_path.exists():
        raise RuntimeError(f"Bundle not found at {bundle_path}")

    return bundle_path


@pytest.fixture(scope="module")
def bundle_path():
    """Build the MCPB bundle once for all tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        path = build_bundle(Path(tmpdir))
        # Read bundle content to memory so it survives tmpdir cleanup
        content = path.read_bytes()
        yield path.name, content


@pytest.fixture(scope="module")
def bundle_server(bundle_path):
    """Serve the bundle over HTTP."""
    bundle_name, bundle_content = bundle_path

    # Start HTTP server on a random port
    server = HTTPServer(host="0.0.0.0", port=0)
    server.expect_request(f"/{bundle_name}").respond_with_data(
        bundle_content,
        content_type="application/octet-stream",
    )
    server.start()

    yield server

    server.stop()


@pytest.fixture(scope="module")
def mcpb_container(bundle_server, bundle_path):
    """Run the MCPB container."""
    bundle_name, _ = bundle_path
    bundle_url = f"http://host.docker.internal:{bundle_server.port}/{bundle_name}"

    container = (
        DockerContainer(BASE_IMAGE)
        .with_env("BUNDLE_URL", bundle_url)
        .with_bind_ports(CONTAINER_PORT, None)  # Random host port
        .with_kwargs(extra_hosts={"host.docker.internal": "host-gateway"})
    )

    container.start()

    try:
        # Wait for server to be ready (wait for uvicorn startup message)
        wait_for_logs(container, "Uvicorn running on", timeout=60)

        # Give uvicorn a moment to fully initialize
        time.sleep(1)

        # Get the mapped port
        host_port = container.get_exposed_port(CONTAINER_PORT)
        base_url = f"http://localhost:{host_port}"

        # Wait for health endpoint
        for _ in range(30):
            try:
                resp = requests.get(f"{base_url}/health", timeout=2)
                if resp.status_code == 200:
                    break
            except requests.RequestException:
                time.sleep(0.5)
        else:
            logs = container.get_logs()
            raise RuntimeError(f"Container not healthy. Logs: {logs}")

        yield base_url

    finally:
        container.stop()


def test_health_endpoint(mcpb_container):
    """Test that the health endpoint returns successfully."""
    base_url = mcpb_container

    response = requests.get(f"{base_url}/health", timeout=5)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "mcp-echo"


@pytest.mark.asyncio
async def test_mcp_tools_list(mcpb_container):
    """Test that the MCP tools/list endpoint returns all expected tools."""
    base_url = mcpb_container

    async with streamablehttp_client(f"{base_url}/mcp") as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools_response = await session.list_tools()
            tools = tools_response.tools

            assert tools, "No tools returned from MCP server"

            tool_names = {tool.name for tool in tools}
            expected_tools = {"echo_message", "echo_with_delay", "echo_json"}

            assert expected_tools.issubset(tool_names), (
                f"Missing tools: {expected_tools - tool_names}"
            )

            for tool in tools:
                assert tool.name
                assert tool.description
                assert tool.inputSchema


@pytest.mark.asyncio
async def test_mcp_tool_call(mcpb_container):
    """Test calling an MCP tool."""
    base_url = mcpb_container

    async with streamablehttp_client(f"{base_url}/mcp") as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.call_tool(
                "echo_message",
                {"message": "Hello from MCPB!", "uppercase": True},
            )

            assert result.content
            assert len(result.content) > 0

            # Verify the response contains expected data
            text_content = result.content[0].text
            assert "HELLO FROM MCPB!" in text_content
