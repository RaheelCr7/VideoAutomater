FROM python:3.11-slim

# Install system dependencies (ffmpeg is mandatory for Beyond 80 video rendering)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsm6 \
    libxext6 \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency definition
COPY pyproject.toml poetry.lock* /app/

# Install python dependencies
RUN pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root || true \
    && pip install --no-cache-dir fastapi uvicorn[standard] aiofiles starlette edge-tts pillow numpy soundfile

# Copy application source code
COPY . /app

# Ensure output directories exist
RUN mkdir -p /app/output/platform_db /app/output/episode_001

EXPOSE 8000

ENV PORT=8000
ENV PYTHONPATH=/app/src
ENV APP_ENV=production

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/api/health || exit 1

CMD ["uvicorn", "videoautomater.server.app:app", "--host", "0.0.0.0", "--port", "8000"]
