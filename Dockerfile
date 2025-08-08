FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libxml2-dev \
    libxslt-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Try installing with uv first, fall back to pip if it fails
COPY requirements.txt ./
RUN pip install --no-cache-dir uv && \
    (uv pip install --no-cache -r requirements.txt || \
     pip install --no-cache-dir -r requirements.txt)

COPY . .

# Non-root user
RUN useradd -m app && chown -R app:app /app
USER app

EXPOSE ${PORT:-10000}

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-10000}/health || exit 1

ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PORT=${PORT:-10000}

CMD ["python", "bot.py"]
