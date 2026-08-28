# core/config.py
"""
Framework-agnostic settings.

Secrets resolve from OS environment variables first, falling back to
Streamlit's st.secrets when the app happens to be running under Streamlit.
That ordering matters: it lets the SAME modules/ and services/ code run
unchanged under both the existing Streamlit app and the FastAPI backend,
rather than forking the code per host.

The Streamlit fallback is imported lazily and defensively — importing
streamlit from a FastAPI worker would be wasteful, and st.secrets raises
StreamlitSecretNotFoundError when no secrets source exists at all (it
raises from .get() too, not just subscripting).
"""

from __future__ import annotations
import os
from functools import lru_cache


_STREAMLIT = None       # cached module handle
_STREAMLIT_CHECKED = False


def _streamlit_module():
    """Return the streamlit module, or None when it isn't importable.

    Resolved once and cached. Without this, every secret miss retried the
    import — a settings read touches several keys, so a single request
    attempted it dozens of times. On a backend host where streamlit is
    genuinely absent that is dozens of raised-and-swallowed ImportErrors
    per request, which is both wasteful and noisy in any import trace.
    """
    global _STREAMLIT, _STREAMLIT_CHECKED
    if not _STREAMLIT_CHECKED:
        _STREAMLIT_CHECKED = True
        try:
            import streamlit as st  # noqa: PLC0415 — lazy on purpose
            _STREAMLIT = st
        except Exception:
            _STREAMLIT = None
    return _STREAMLIT


def _from_streamlit(name: str) -> str | None:
    """Read a secret from st.secrets, or None if unavailable for any
    reason (streamlit not installed, no secrets file, key absent)."""
    st = _streamlit_module()
    if st is None:
        return None
    try:
        val = st.secrets.get(name, None)
        return str(val) if val else None
    except Exception:
        return None


def get_secret(name: str, default: str | None = None) -> str | None:
    """Environment variable first, then Streamlit secrets, then default.
    Never raises."""
    val = os.environ.get(name)
    if val:
        return val
    val = _from_streamlit(name)
    if val:
        return val
    return default


class Settings:
    """Application settings. Instantiated once via get_settings()."""

    # ── API keys ──────────────────────────────────────────────────────────
    @property
    def groq_api_key(self) -> str | None:
        return get_secret("GROQ_API_KEY")

    @property
    def news_api_key(self) -> str | None:
        return get_secret("NEWS_API_KEY")

    @property
    def gemini_api_key(self) -> str | None:
        return get_secret("GEMINI_API_KEY")

    # ── Models ────────────────────────────────────────────────────────────
    # Kept as settings rather than hardcoded constants: Groq retired
    # llama-3.3-70b-versatile with no warning, which silently broke every
    # AI call in the app. Being able to re-point the model via an env var
    # turns a repeat of that into a config change, not a redeploy.
    @property
    def llm_model_primary(self) -> str:
        return get_secret("LLM_MODEL_PRIMARY", "openai/gpt-oss-120b")

    @property
    def llm_model_light(self) -> str:
        return get_secret("LLM_MODEL_LIGHT", "openai/gpt-oss-20b")

    # ── Cache TTLs (seconds) ──────────────────────────────────────────────
    quote_ttl: int = 300        # 5 min  — price/metrics
    news_ttl: int = 900         # 15 min — user-facing news
    news_llm_ttl: int = 3600    # 1 hour — headlines embedded in LLM prompts;
                                #          deliberately longer so the prompt
                                #          text (and thus the response-cache
                                #          key) doesn't churn 4x per hour
    wiki_ttl: int = 86400       # 24 h   — company descriptions
    llm_ttl: int = 86400        # 24 h   — LLM responses

    # ── Feature flags ─────────────────────────────────────────────────────
    @property
    def ai_enabled(self) -> bool:
        return bool(self.groq_api_key)

    # ── CORS ──────────────────────────────────────────────────────────────
    @property
    def cors_origins(self) -> list[str]:
        raw = get_secret("CORS_ORIGINS", "http://localhost:3000")
        return [o.strip() for o in (raw or "").split(",") if o.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
