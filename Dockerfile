# Dockerfile — portable backend image.
#
# render.yaml uses Render's native Python runtime and does NOT need this
# file. It exists so the API isn't locked to one host: the same image runs
# on Fly.io, Railway, Cloud Run, or any container platform.
#
# Build:  docker build -t equieye-api .
# Run:    docker run -p 8000:8000 --env-file .env equieye-api

FROM python:3.12-slim

# - PYTHONDONTWRITEBYTECODE: no .pyc in a throwaway container layer
# - PYTHONUNBUFFERED: logs stream immediately instead of sitting in a
#   buffer, so a crash loop is actually diagnosable from host logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Dependencies first, as their own layer: application code changes far more
# often than the dependency list, so this keeps the expensive pip install
# cached across ordinary code edits.
COPY requirements-backend.txt .
RUN pip install --no-cache-dir -r requirements-backend.txt

COPY . .

# Run as non-root. A container process that doesn't need root shouldn't
# have it, and some platforms reject root containers outright.
RUN useradd --create-home --uid 10001 appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Single worker — see the WEB_CONCURRENCY note in render.yaml: the TTL
# cache is per-process, so extra workers lower the hit rate and multiply
# upstream yfinance calls from one IP.
CMD ["sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]
