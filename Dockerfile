FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies and uv
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir uv

# Copy project files
COPY pyproject.toml ./
COPY server.py ./
COPY README.md ./

# Install dependencies with uv
RUN uv pip install --system --no-cache .

# Create non-root user for security
RUN groupadd -g 1000 mcpuser && \
    useradd -m -u 1000 -g 1000 mcpuser && \
    chown -R mcpuser:mcpuser /app

# Switch to non-root user
USER mcpuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Run the server
CMD ["python", "server.py"]