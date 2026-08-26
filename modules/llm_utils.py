"""
modules/llm_utils.py
--------------------
LLM utility helpers for EquiEye AI.

Key improvements:
1. ask_llm_cached() — @st.cache_data wrapper so identical prompts don't burn Groq tokens
2. trim_prompt() — trims context to stay within token limits
3. compact_metrics() — builds a compact metrics string for shorter prompts
4. Rate-limit-friendly retry with exponential backoff
5. Gemini fallback — when Groq's free-tier rate limit (or quota) is hit,
   transparently retries the same prompt against Google's Gemini API
   instead of failing outright. Requires GEMINI_API_KEY in secrets.toml;
   if it's absent, behavior is unchanged (Groq's own friendly error is
   returned, same as before this fallback existed).
6. Disk-backed cache (SQLite) — st.cache_data alone lives in process
   memory, so it's wiped whenever the app restarts (e.g. Streamlit Cloud
   waking a sleeping app). The SQLite layer below sits underneath it and
   survives restarts, so a popular stock analyzed yesterday doesn't cost
   a fresh Groq call today just because the app went to sleep overnight.
   TTL is 24 hours — long enough to be meaningfully durable, short enough
   that stale financials/news sentiment don't linger indefinitely.
"""

from __future__ import annotations
import time
import hashlib
import os
import sqlite3
import streamlit as st

_CACHE_TTL_SECONDS = 24 * 60 * 60  # 24 hours — shared by both cache layers


def _safe_secret(name: str, default: str = "") -> str:
    """Read a secret without ever raising.

    st.secrets raises StreamlitSecretNotFoundError when no secrets source
    exists at all, and it does so from `.get()` too — any access triggers
    the underlying file load, so `.get(name, "")` is NOT safe on its own.
    Mirrors app.py's `_secret()`; kept local so this module stays
    independently importable.
    """
    try:
        return st.secrets.get(name, default)
    except Exception:
        return default

# Cache DB lives next to this file's package root (repo root), not /tmp —
# on Streamlit Cloud /tmp can be cleared more aggressively than the app's
# working directory across a sleep/wake cycle.
_CACHE_DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    ".llm_cache", "cache.db"
)


def _disk_cache_conn():
    os.makedirs(os.path.dirname(_CACHE_DB_PATH), exist_ok=True)
    conn = sqlite3.connect(_CACHE_DB_PATH, check_same_thread=False, timeout=5)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS llm_cache ("
        "cache_key TEXT PRIMARY KEY, response TEXT NOT NULL, created_at REAL NOT NULL)"
    )
    return conn


def _disk_cache_get(cache_key: str):
    """Returns the cached response string, or None on miss/stale/any error.
    Deliberately fails silent+open: the disk cache is a pure optimization,
    never something that should be able to break the app if the file is
    locked, corrupted, or the filesystem is read-only in some environment.
    """
    try:
        conn = _disk_cache_conn()
        row = conn.execute(
            "SELECT response, created_at FROM llm_cache WHERE cache_key = ?", (cache_key,)
        ).fetchone()
        conn.close()
        if row is None:
            return None
        response, created_at = row
        if time.time() - created_at > _CACHE_TTL_SECONDS:
            return None  # stale — treat as a miss, will be overwritten on next successful call
        return response
    except Exception:
        return None


def _disk_cache_set(cache_key: str, response: str):
    """Best-effort write; failures are swallowed for the same reason as above."""
    try:
        conn = _disk_cache_conn()
        conn.execute(
            "INSERT INTO llm_cache (cache_key, response, created_at) VALUES (?, ?, ?) "
            "ON CONFLICT(cache_key) DO UPDATE SET response=excluded.response, created_at=excluded.created_at",
            (cache_key, response, time.time())
        )
        conn.commit()
        conn.close()
    except Exception:
        pass


def _hash_prompt(prompt: str, system: str) -> str:
    return hashlib.md5(f"{system}||{prompt}".encode()).hexdigest()


def _is_rate_limit_or_quota_error(error_text: str) -> bool:
    """
    True only for errors that mean 'Groq itself is throttling/exhausted' —
    the specific case the Gemini fallback exists for. Deliberately narrow:
    auth errors, malformed-request errors, etc. should surface normally
    rather than silently trying a second provider.
    """
    e = error_text.lower()
    return "rate limit" in e or "429" in e or "quota" in e


def _call_gemini(prompt: str, system: str, max_tokens: int = 1000) -> str:
    """
    Fallback call to Google's Gemini API, used only when Groq returns a
    rate-limit/quota error. Uses the REST endpoint directly (no new SDK
    dependency — `requests` is already in requirements.txt).

    Model: gemini-2.5-flash. Free tier as of mid-2026 gives this model a
    meaningfully higher daily request budget than Groq's free-tier
    openai/gpt-oss-120b model, so it's a reasonable second option rather
    than a downgrade.

    Raises on failure (missing key, HTTP error, unexpected response shape)
    so the caller can decide how to report it — this function does not
    swallow errors itself.
    """
    import requests

    api_key = _safe_secret("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not configured")

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        "gemini-2.5-flash:generateContent"
    )
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": max_tokens,
            "temperature": 0.3,
        },
    }
    if system:
        payload["systemInstruction"] = {"parts": [{"text": system}]}

    resp = requests.post(url, params={"key": api_key}, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    candidates = data.get("candidates") or []
    if not candidates:
        # Most common cause: the prompt was blocked by Gemini's safety
        # filters (finishReason == "SAFETY"), which has no "text" to return.
        raise RuntimeError(f"Gemini returned no candidates: {data}")
    parts = candidates[0].get("content", {}).get("parts", [])
    if not parts or "text" not in parts[0]:
        raise RuntimeError(f"Gemini response had no text: {data}")
    return parts[0]["text"]


@st.cache_data(ttl=_CACHE_TTL_SECONDS, show_spinner=False)
def _cached_llm_call(prompt_hash: str, prompt: str, system: str, client_key: str, max_tokens: int = 1000, model: str = "openai/gpt-oss-120b") -> str:
    """
    Cached LLM call — two layers:
    1. st.cache_data (in-process memory, fast, wiped on restart)
    2. SQLite disk cache underneath it (survives restarts/sleep-wake)
    Both share the same 24-hour TTL and the same cache key components:
    (prompt_hash, model, max_tokens). `client_key` is included in the
    st.cache_data key so different API keys don't share cache.
    `prompt_hash` is in the signature (not the full prompt text) so
    Streamlit's cache key stays small even for large prompts.

    max_tokens is a real parameter (not hardcoded) for two reasons:
    1. Callers with a larger JSON payload (e.g. the combined snapshot+bull+bear
       analysis) need a bigger budget or the response gets truncated mid-JSON,
       fails to parse, and silently falls back to a much more generic retry
       prompt — with no visible error to whoever is testing it.
    2. Because it's a real parameter, both cache layers include it in the
       cache key automatically. That matters: if this were still hardcoded
       while a caller asked for more tokens, a stale cache entry from an
       earlier max_tokens=1000 call could keep serving an old truncated
       response even after the code was fixed to ask for more.

    model defaults to openai/gpt-oss-120b, the primary analysis model
    (unchanged behavior for every existing call site — was
    llama-3.3-70b-versatile until Groq retired that model). Lightweight,
    less quality-sensitive call sites (sentiment tagging, one-sentence
    outlook retries, conversational Q&A) can pass model="openai/gpt-oss-20b"
    instead, which draws from a separate free-tier daily quota — routing
    those calls there relieves pressure on the primary model's budget
    without needing Gemini at all for the common case. Since exact RPD
    figures shift over time on Groq's side, check the current dashboard
    rather than trusting a hardcoded number here. Because model is part
    of the cache key, a cached lightweight-model response can never be
    served for a call that asked for the primary model or vice versa.

    Provider fallback: tries Groq first; if Groq is rate-limited or its
    quota is exhausted, transparently retries the same prompt against
    Gemini before giving up.

    Failure handling: raises (rather than returning the friendly error
    string) when both providers fail. This matters for correctness at a
    24-hour TTL — if a transient rate-limit blip returned a normal string,
    both cache layers would treat that error message as a valid cached
    "answer" and keep serving it for a full day. Raising means neither
    layer caches it; the caller (ask_llm_smart) catches the exception and
    falls through to its own direct-call retry path instead.
    """
    disk_key = f"{prompt_hash}:{model}:{max_tokens}"
    disk_hit = _disk_cache_get(disk_key)
    if disk_hit is not None:
        return disk_hit

    # Import here to avoid circular at module load time
    from groq import Groq
    default_system = (
        "You are EquiEye AI, an expert financial analyst focused on Indian "
        "stock markets. Be concise, insightful, and always add a disclaimer "
        "that this is not financial advice."
    )
    try:
        client = Groq(api_key=_safe_secret("GROQ_API_KEY"))
        msg = client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            temperature=0.3,
            messages=[
                {"role": "system", "content": system or default_system},
                {"role": "user", "content": prompt}
            ]
        )
        result = msg.choices[0].message.content
        _disk_cache_set(disk_key, result)
        return result
    except Exception as e:
        if _is_rate_limit_or_quota_error(str(e)):
            try:
                result = _call_gemini(prompt, system or default_system, max_tokens=max_tokens)
                _disk_cache_set(disk_key, result)
                return result
            except Exception:
                pass  # Gemini also unavailable — raise below so this isn't cached
        raise RuntimeError(str(e))


def ask_llm_smart(
    client,
    prompt: str,
    system: str = "",
    use_cache: bool = True,
    max_tokens: int = 1000,
    retries: int = 2,
    model: str = "openai/gpt-oss-120b",
) -> str:
    """
    Smart LLM caller with:
    - Optional prompt-level caching (avoids re-calling for identical prompts)
    - Retry with backoff on rate limits
    - Gemini fallback if Groq is still rate-limited/quota-exhausted after retries
    - Friendly error messages on failure
    - max_tokens default reduced from 1500→1000 to save Groq quota
    - model defaults to openai/gpt-oss-120b (the primary model); pass
      "openai/gpt-oss-20b" for lightweight calls to draw from that
      model's separate free-tier daily quota instead.
    """
    if use_cache:
        h = _hash_prompt(prompt, system)
        try:
            cached = _cached_llm_call(h, prompt, system, "groq", max_tokens=max_tokens, model=model)
            return cached
        except Exception:
            pass  # Fall through to direct call

    last_error = ""
    for attempt in range(retries + 1):
        try:
            msg = client.chat.completions.create(
                model=model,
                max_tokens=max_tokens,
                temperature=0.3,
                messages=[
                    {"role": "system", "content": system or "You are EquiEye AI, an expert financial analyst for Indian markets."},
                    {"role": "user", "content": prompt}
                ]
            )
            return msg.choices[0].message.content
        except Exception as e:
            last_error = str(e)
            if _is_rate_limit_or_quota_error(last_error):
                if attempt < retries:
                    time.sleep(3 * (attempt + 1))  # 3s, 6s backoff
                    continue
                # Retries exhausted and Groq is still rate-limited/out of
                # quota — try Gemini before giving up entirely.
                try:
                    return _call_gemini(prompt, system, max_tokens=max_tokens)
                except Exception:
                    pass
            return _friendly_error(last_error)

    return "⚠ AI analysis temporarily unavailable. Please try again in a moment."


def _friendly_error(error_text: str) -> str:
    e = error_text.lower()
    if "api key" in e or "authentication" in e or "unauthorized" in e:
        return "⚠ AI analysis is unavailable — API key issue. Check your Groq API key in secrets.toml."
    if "rate limit" in e or "429" in e:
        return "⚠ Groq rate limit reached (and Gemini fallback unavailable or also exhausted). Please wait 30 seconds and try again."
    if "credit" in e or "quota" in e or "billing" in e:
        return "⚠ Groq API quota exhausted (and Gemini fallback unavailable or also exhausted). Please check your Groq account for available credits."
    if "timeout" in e or "connection" in e:
        return "⚠ Connection timeout. Please check your internet connection and retry."
    return "⚠ AI analysis couldn't be generated right now. Please try again in a moment."


def trim_prompt(text: str, max_chars: int = 6000) -> str:
    """Trim a text block to max_chars to reduce token usage."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n[...truncated for brevity...]"


def compact_metrics(name: str, ticker: str, sector: str, pe=None, roe_raw=None,
                    de_raw=None, profit_margin_raw=None, mkt_cap_str="", rev_str="",
                    revenue_cagr=None, profit_cagr=None) -> str:
    """
    Build a compact metrics string for LLM prompts.
    Keeps prompts short to reduce Groq token usage.
    """
    parts = [f"Company: {name} ({ticker})", f"Sector: {sector}"]
    if pe is not None:
        parts.append(f"P/E={pe:.1f}x")
    if roe_raw is not None:
        parts.append(f"ROE={roe_raw*100:.1f}%")
    if de_raw is not None:
        parts.append(f"D/E={de_raw/100:.2f}x")
    if profit_margin_raw is not None:
        parts.append(f"NetMargin={profit_margin_raw*100:.1f}%")
    if mkt_cap_str:
        parts.append(f"MCap={mkt_cap_str}")
    if rev_str:
        parts.append(f"Rev={rev_str}")
    if revenue_cagr is not None:
        parts.append(f"RevCAGR={revenue_cagr:.1f}%")
    if profit_cagr is not None:
        parts.append(f"ProfitCAGR={profit_cagr:.1f}%")
    return " | ".join(parts)


def parse_json_safe(raw: str) -> dict:
    """
    Safely parse JSON from LLM output, stripping markdown fences.
    Returns empty dict on failure.
    """
    import json
    if not raw:
        return {}
    raw = raw.strip()
    # Strip ```json ... ``` fences
    if raw.startswith("```"):
        raw = raw.lstrip("`")
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()
        if raw.endswith("```"):
            raw = raw[:-3].strip()
    # Isolate JSON object
    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start != -1 and end > start:
        raw = raw[start:end]
    try:
        return json.loads(raw)
    except Exception:
        return {}
