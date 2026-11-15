# ==============================================================================
# AutoSense Production Dockerfile
# Multi-stage optimized container for FastAPI Backend & Embedded React Dashboard
# ==============================================================================
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PORT=8000

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# Download required NLTK corpora
RUN python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True); nltk.download('vader_lexicon', quiet=True)"

# Copy application directories
COPY src/ /app/src/
COPY backend/ /app/backend/
COPY models/ /app/models/
COPY reports/ /app/reports/
COPY datasets/normalized/ /app/datasets/normalized/
COPY datasets/splits/ /app/datasets/splits/
COPY bigdata/logs/ /app/bigdata/logs/
COPY frontend/dist/ /app/frontend/dist/
COPY .env.example /app/.env.example

# Expose service port
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start Uvicorn ASGI server
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
