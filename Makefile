# Docker image configuration
IMAGE_NAME = nimbletools/mcp-echo
VERSION ?= latest

.PHONY: build-push login help test clean release all

# Default target
help:
	@echo "Available targets:"
	@echo "  build-push - Build multi-arch image and push to registry"
	@echo "  login   - Login to Docker Hub"
	@echo "  test    - Run tests before building"
	@echo "  clean   - Remove local Docker images"
	@echo "  all     - Test and build-push"
	@echo "  release - Test and build-push with version prompt"
	@echo ""
	@echo "Environment variables:"
	@echo "  VERSION - Image version tag (default: latest)"

# Run tests
test:
	uv run pytest

build-push:
	docker buildx build --platform linux/amd64,linux/arm64 \
		-t $(IMAGE_NAME):$(VERSION) \
		-t $(IMAGE_NAME):latest \
		--push .

# Login to Docker Hub
login:
	docker login

# Clean up local images
clean:
	docker rmi $(IMAGE_NAME):$(VERSION) $(IMAGE_NAME):latest 2>/dev/null || true

# Test and build-push
all: test build-push

# Build and push with version tag
release: test
	@read -p "Enter version (e.g., v1.0.0): " version; \
	make build-push VERSION=$$version