"""E2E test configuration and fixtures."""

from pathlib import Path

# Test configuration
BASE_IMAGE = "ghcr.io/nimblebrain/mcpb-python:3.14"
CONTAINER_PORT = 8000
BUNDLE_NAME = "mcp-echo"
BUNDLE_VERSION = "0.0.1"

PROJECT_ROOT = Path(__file__).parent.parent
BUILD_SCRIPT = PROJECT_ROOT / "scripts" / "build-bundle.sh"
