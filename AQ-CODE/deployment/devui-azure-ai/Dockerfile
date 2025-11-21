# Dockerfile for Azure AI Agents DevUI Demo
# Deploys the DevUI gallery with 8 Azure AI agent demos

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
COPY python/packages/azure-ai/pyproject.toml ./python/packages/azure-ai/
COPY python/packages/devui/pyproject.toml ./python/packages/devui/
COPY AQ-CODE/requirements.txt ./requirements.txt

# Install agent framework packages
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy agent directories and resources
COPY --chown=appuser:appuser AQ-CODE/azure_ai/azure_agents/ ./azure_agents/
COPY --chown=appuser:appuser python/samples/getting_started/agents/resources/ ./resources/

# Create directories for generated content
RUN mkdir -p /app/generated_plots && chown -R appuser:appuser /app

# Expose DevUI port
EXPOSE 8100

# Run as non-root user
USER appuser

# Environment variables should be provided by Azure Container Apps:
# - AZURE_AI_PROJECT_ENDPOINT (required)
# - AZURE_AI_MODEL_DEPLOYMENT_NAME (required)
# - OPENWEATHER_API_KEY (optional - for weather agents)
# - BING_CONNECTION_ID (optional - for bing grounding agent)
# - FILE_SEARCH_VECTOR_STORE_ID (optional - for file search agent)
# - ENABLE_DEVUI_TRACING (optional - enable tracing)
# - ENABLE_OTEL (optional - enable OpenTelemetry)

CMD ["devui", "azure_agents", "--port", "8100", "--host", "0.0.0.0"]
