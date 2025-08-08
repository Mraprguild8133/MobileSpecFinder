# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies and cleanup in one layer
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libxml2-dev \
    libxslt-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv (new package installer)
RUN pip install --no-cache-dir uv

# Copy requirements files
COPY requirements.txt ./

# Install Python dependencies using uv
RUN uv pip install --no-cache -r requirements.txt

# Copy application code (using .dockerignore to exclude unnecessary files)
COPY . .

# Create and switch to non-root user
RUN useradd -m app && chown -R app:app /app
USER app

# Expose port (with default for local development)
EXPOSE ${PORT:-10000}

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-10000}/health || exit 1

# Environment variables
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PORT=${PORT:-10000}

# Command to run the application (adjust based on your needs)
CMD ["python", "render_app.py"]
