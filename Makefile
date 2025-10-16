# Docker image configuration
IMAGE_NAME = nimbletools/mcp-echo
VERSION ?= 1.0.0

.PHONY: help install dev-install format lint lint-fix typecheck test test-cov clean check all build-push login release

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install the package
	uv pip install -e .

dev-install: ## Install with dev dependencies
	uv pip install -e . --group dev

format: ## Format code with ruff
	uv run ruff format src/ tests/

lint: ## Lint code with ruff
	uv run ruff check src/ tests/

lint-fix: ## Lint and fix code with ruff
	uv run ruff check --fix src/ tests/

typecheck: ## Type check with mypy
	uv run mypy src/

test: ## Run tests with pytest
	uv run pytest tests/ -v

test-cov: ## Run tests with coverage
	uv run pytest tests/ -v --cov=src/mcp_echo --cov-report=term-missing

test-e2e: ## Run end-to-end Docker tests
	uv run pytest e2e/ -v -s

clean: ## Clean up artifacts
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".coverage" -exec rm -rf {} + 2>/dev/null || true
	docker rmi $(IMAGE_NAME):$(VERSION) $(IMAGE_NAME):latest 2>/dev/null || true

run: ## Run the MCP server
	uv run python -m mcp_echo.server

run-stdio: ## Run in stdio mode (for Claude desktop)
	uv run fastmcp run src/mcp_echo/server.py

run-http: ## Run HTTP server with uvicorn
	uv run uvicorn mcp_echo.server:app --host 0.0.0.0 --port 8000

test-http: ## Test HTTP server is running
	@echo "Testing health endpoint..."
	@curl -s http://localhost:8000/health | grep -q "healthy" && echo "✓ Server is healthy" || echo "✗ Server not responding"

check: lint typecheck test ## Run all checks

all: clean install format lint typecheck test ## Full workflow

# Docker commands
docker-build: ## Build Docker image locally
	docker build -t $(IMAGE_NAME):$(VERSION) -t $(IMAGE_NAME):latest .

docker-run: ## Run Docker container
	docker run -p 8000:8000 $(IMAGE_NAME):$(VERSION)

login: ## Login to Docker Hub
	docker login

release: ## Build and push multi-platform Docker image
	docker buildx build --platform linux/amd64,linux/arm64 \
		-t $(IMAGE_NAME):$(VERSION) \
		-t $(IMAGE_NAME):latest \
		--push .

# Aliases
fmt: format
t: test
l: lint