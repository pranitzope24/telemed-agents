# Use official Python runtime as base image
FROM python:3.12-slim

# Set working directory in container
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .
# COPY .env .
# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY pyproject.toml ./

# Create necessary directories
RUN mkdir -p app/rag/vector_store app/rag/ayurveda app/rag/medical app/rag/safety

# Expose port (will use PORT env variable)
EXPOSE ${PORT}

# Run the application
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
