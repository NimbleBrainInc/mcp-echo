FROM python:3.13-slim

WORKDIR /app

# Install uv
RUN apt-get update && apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir uv

# Copy project files
COPY pyproject.toml ./
COPY README.md ./
COPY src/ ./src/

# Install dependencies
RUN uv pip install --system --no-cache .

# Create non-root user
RUN groupadd -g 1000 mcpuser && \
    useradd -m -u 1000 -g 1000 mcpuser && \
    chown -R mcpuser:mcpuser /app

USER mcpuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

# Run with uvicorn
CMD ["uvicorn", "mcp_echo.server:app", "--host", "0.0.0.0", "--port", "8000"]
