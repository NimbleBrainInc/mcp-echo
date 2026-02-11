# Echo MCP Server

FastMCP echo server for testing MCP connections.

## Commands

```bash
uv run pytest           # Test
uv run ruff format .    # Format
uv run ruff check .     # Lint
uv run mypy .           # Type check
make check              # All of the above
make bump VERSION=x.y.z # Bump version in all files
```

## Release

See `mcp-servers/CLAUDE.md` for the full release workflow.

```bash
make bump VERSION=0.2.0
git add -A && git commit -m "Bump version to 0.2.0"
git tag v0.2.0 && git push origin main v0.2.0
gh release create v0.2.0 --title "v0.2.0" --notes "- changelog"
```
