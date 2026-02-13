# Echo MCP Server

FastMCP echo server for testing MCP connections.

## Commands

```bash
make test               # Unit tests
make test-e2e           # E2E tests (requires Docker + mcpb CLI)
make check              # Format + lint + typecheck + unit tests
make bump VERSION=x.y.z # Bump version in all files
```

## E2E Tests

`e2e/` contains end-to-end tests that build and deploy the actual MCPB bundle in a Docker container, then verify health, tool listing, and tool invocation over HTTP.

**Prerequisites:** Docker running, `mcpb` CLI installed

The tests automatically vendor Linux-compatible deps (matching the Docker daemon's architecture) using `uv pip install --python-platform`, so they work on macOS and Linux hosts.

**Config:** `e2e/conftest.py` has `BASE_IMAGE`, `PYTHON_VERSION`, `CONTAINER_PORT`, and `BUNDLE_NAME`.

## Release

See `mcp-servers/CLAUDE.md` for the full release workflow.

```bash
make bump VERSION=0.2.0
git add -A && git commit -m "Bump version to 0.2.0"
git tag v0.2.0 && git push origin main v0.2.0
gh release create v0.2.0 --title "v0.2.0" --notes "- changelog"
```
