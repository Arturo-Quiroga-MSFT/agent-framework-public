# Multi-stage Dockerfile for Streamlit Azure AI demo
# - Builds a minimal image
# - Does not bake in .env; expects secrets to be provided by Azure Container Apps

# Build stage: install dependencies
FROM python:3.11-slim AS build

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install build deps
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       gcc \
       git \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements and install to a wheel cache
COPY AQ-CODE/requirements.txt ./requirements.txt
RUN pip install --upgrade pip setuptools wheel
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# Runtime stage: copy wheels and app, install from wheels
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Create non-root user
RUN groupadd -g 1000 appuser && useradd -u 1000 -g appuser -m appuser

# Create directories with proper ownership BEFORE copying files
RUN mkdir -p /app/generated_plots && chown -R appuser:appuser /app

# Copy wheels from builder and install
COPY --from=build /wheels /wheels
RUN pip install --no-cache-dir /wheels/* || true

# Copy application code
COPY --chown=appuser:appuser AQ-CODE/streamlit_azure_ai_demo.py ./streamlit_azure_ai_demo.py
COPY --chown=appuser:appuser AQ-CODE/sample_documents/ ./sample_documents/
COPY --chown=appuser:appuser AQ-CODE/MCP_EXPLAINED.md ./MCP_EXPLAINED.md
COPY --chown=appuser:appuser AQ-CODE/streamlit_azure_ai_demo_backup_20251025_1110.py ./

# Expose Streamlit default port
EXPOSE 8501

# Run as non-root user
USER appuser

# Note: environment variables (secrets) should be provided by Azure Container Apps
# Example variables to set in Container App service: AZURE_AI_PROJECT_ENDPOINT, AZURE_AI_MODEL_DEPLOYMENT_NAME, OPENWEATHER_API_KEY, BING_CONNECTION_ID, FIRECRAWL_API_KEY

CMD ["streamlit", "run", "streamlit_azure_ai_demo.py", "--server.port=8501", "--server.address=0.0.0.0"]
