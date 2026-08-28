# api/main.py
"""
EquiEye FastAPI backend.

Wraps the existing services/ and modules/ packages — no analysis logic
lives here. Routers own HTTP concerns (validation, status codes, response
shape); everything below them is the same framework-agnostic code the
Streamlit app runs, so the two hosts can't drift apart.

Endpoints are split FAST vs SLOW on purpose:

  fast  (~1-3s, yfinance + pure computation)
        /search, /stock/{t}, /stock/{t}/health, /stock/{t}/risk,
        /stock/{t}/red-flags, /stock/{t}/price-history, /compare

  slow  (LLM round trips, seconds to tens of seconds)
        /stock/{t}/analysis, /stock/{t}/moat, /chat

The Streamlit app blocks on everything, which is why a stock page takes
~20s to appear. Splitting them lets a frontend paint real numbers almost
immediately and stream the AI commentary in afterwards — the single
biggest perceived-performance win available, and something Streamlit's
top-to-bottom rerun model cannot express.
"""

from __future__ import annotations
import os
import sys
import time
import logging

# Make the project root importable so `services`/`modules`/`core` resolve
# regardless of the working directory uvicorn is launched from.
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.config import get_settings
from core.cache import cache_stats
from core.db import init_db, DATABASE_URL
from api.routers import stocks, compare, ai, account

log = logging.getLogger("equieye")

settings = get_settings()

@asynccontextmanager
async def lifespan(_: FastAPI):
    """Create tables if absent. Safe on every boot — create_all only
    adds missing tables and never alters existing ones."""
    init_db()
    yield


app = FastAPI(
    lifespan=lifespan,
    title="EquiEye API",
    description="AI-powered equity research for Indian markets.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.middleware("http")
async def timing_header(request: Request, call_next):
    """Surface server-side duration so the fast/slow split is measurable
    from the client rather than assumed."""
    started = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Response-Time-ms"] = f"{(time.perf_counter() - started) * 1000:.0f}"
    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Never leak a stack trace to the client.

    Upstream data sources here are genuinely flaky — yfinance is an
    unofficial scraper that throttles, and the LLM provider rate-limits —
    so unhandled failures are expected in normal operation, not just in
    bugs. Log the detail, return a stable shape.
    """
    log.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"error": "internal_error",
                 "detail": "Something went wrong handling this request."},
    )


app.include_router(stocks.router,  prefix="/api", tags=["stocks"])
app.include_router(compare.router, prefix="/api", tags=["compare"])
app.include_router(ai.router,      prefix="/api", tags=["ai"])
app.include_router(account.router, prefix="/api", tags=["account"])


@app.get("/api/health", tags=["meta"])
def health():
    """Liveness + capability probe. Reports whether AI is configured so a
    frontend can disable those sections up front instead of rendering
    placeholders that will never fill — the same degraded-mode contract
    the Streamlit app uses."""
    return {
        "status": "ok",
        "ai_enabled": settings.ai_enabled,
        "news_enabled": bool(settings.news_api_key),
        "models": {
            "primary": settings.llm_model_primary,
            "light": settings.llm_model_light,
        },
        "cache": cache_stats(),
        "persistence": {
            "enabled": True,
            # Surfaced because SQLite means an ephemeral filesystem on
            # most PaaS hosts — i.e. data is wiped on redeploy, which is
            # the exact bug this feature exists to fix. Worth being able
            # to see at a glance which engine a deployment is actually on.
            "engine": "sqlite" if DATABASE_URL.startswith("sqlite") else "postgres",
        },
    }
