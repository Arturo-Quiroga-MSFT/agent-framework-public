# Dockerfile for Redis Agents DevUI Demo
# Deploys the DevUI gallery with 4 Redis-backed agent demos

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       gcc \
       git \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -g 1000 appuser && useradd -u 1000 -g appuser -m appuser

# Copy requirements and install dependencies
COPY python/packages/core/pyproject.toml ./python/packages/core/
COPY python/packages/openai/pyproject.toml ./python/packages/openai/
COPY python/packages/devui/pyproject.toml ./python/packages/devui/
COPY AQ-CODE/requirements.txt ./requirements.txt

# Install agent framework packages
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir redis

# Copy agent directories
COPY --chown=appuser:appuser AQ-CODE/observability/redis_agents/ ./redis_agents/

# Create directories for generated content
RUN mkdir -p /app/data && chown -R appuser:appuser /app

# Expose DevUI port
EXPOSE 8200

# Run as non-root user
USER appuser

# Environment variables should be provided by Azure Container Apps:
# - AZURE_OPENAI_ENDPOINT (required)
# - AZURE_OPENAI_API_KEY (required) OR use managed identity
# - AZURE_OPENAI_DEPLOYMENT_NAME (required)
# - AZURE_OPENAI_API_VERSION (optional, default: 2024-08-01-preview)
# - REDIS_HOST (required)
# - REDIS_PORT (optional, default: 6380)
# - REDIS_PASSWORD (required for Azure Redis)
# - REDIS_SSL (optional, default: true)
# - ENABLE_DEVUI_TRACING (optional - enable tracing)
# - ENABLE_OTEL (optional - enable OpenTelemetry)

CMD ["devui", "redis_agents", "--port", "8200", "--host", "0.0.0.0"]
