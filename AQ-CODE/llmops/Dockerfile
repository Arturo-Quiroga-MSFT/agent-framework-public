# Multi-stage build for LLMOps Production Agent
FROM python:3.11-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY ui/requirements-ui.txt /app/ui/requirements-ui.txt

# Create a combined requirements file
RUN echo "# Combined requirements for LLMOps Production Agent" > /app/requirements-combined.txt && \
    echo "streamlit" >> /app/requirements-combined.txt && \
    echo "python-dotenv" >> /app/requirements-combined.txt && \
    echo "pillow" >> /app/requirements-combined.txt && \
    echo "pydantic" >> /app/requirements-combined.txt && \
    echo "httpx" >> /app/requirements-combined.txt && \
    echo "agent-framework" >> /app/requirements-combined.txt && \
    echo "azure-identity" >> /app/requirements-combined.txt && \
    echo "azure-ai-agents" >> /app/requirements-combined.txt && \
    echo "plotly" >> /app/requirements-combined.txt && \
    echo "pandas" >> /app/requirements-combined.txt && \
    echo "opentelemetry-api" >> /app/requirements-combined.txt && \
    echo "opentelemetry-sdk" >> /app/requirements-combined.txt && \
    echo "azure-monitor-opentelemetry" >> /app/requirements-combined.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements-combined.txt

# Copy application code
COPY __init__.py /app/
COPY core/ /app/core/
COPY examples/ /app/examples/
COPY ui/ /app/ui/

# Create session directory
RUN mkdir -p /app/ui/session_files_from_ui

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Set environment variables for Streamlit
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
ENV PYTHONUNBUFFERED=1

# Run the Streamlit app
CMD ["streamlit", "run", "ui/streamlit_production_ui.py", "--server.port=8501", "--server.address=0.0.0.0"]
