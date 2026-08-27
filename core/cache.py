# core/cache.py
"""
Framework-agnostic TTL cache — the replacement for @st.cache_data.

Two layers, mirroring what the Streamlit app already did:
  1. in-process memory (fast, wiped on restart)
  2. SQLite on disk (survives restarts and sleep/wake cycles)

Only layer 1 is implemented here as a decorator; the SQLite layer already
exists in modules/llm_utils.py for LLM responses specifically, which is
the only payload big or expensive enough to justify disk persistence.

Deliberately dependency-free (no Redis) so the backend runs anywhere with
no infrastructure. The interface is narrow on purpose — swapping the body
of `ttl_cache` for a Redis-backed implementation later touches this file
only, and matters once there is more than one worker process, since an
in-process cache is per-worker.

Thread-safe: FastAPI runs sync endpoints in a threadpool, so concurrent
requests genuinely do hit this from multiple threads.
"""

from __future__ import annotations
import functools
import hashlib
import threading
import time
from typing import Any, Callable


class TTLCache:
    """Simple thread-safe TTL cache with a size bound."""

    def __init__(self, maxsize: int = 512):
        self._data: dict[str, tuple[float, Any]] = {}
        self._lock = threading.Lock()
        self._maxsize = maxsize

    def get(self, key: str) -> tuple[bool, Any]:
        """Returns (hit, value). `hit` distinguishes a cached None from a
        miss — a plain `None` return would conflate them."""
        with self._lock:
            entry = self._data.get(key)
            if entry is None:
                return False, None
            expires_at, value = entry
            if time.time() > expires_at:
                self._data.pop(key, None)
                return False, None
            return True, value

    def set(self, key: str, value: Any, ttl: int) -> None:
        with self._lock:
            if len(self._data) >= self._maxsize:
                # Evict the soonest-to-expire entry. Cheap approximation of
                # LRU that needs no access bookkeeping, and for this
                # workload (per-ticker data on fixed TTLs) it evicts the
                # least useful entry anyway.
                oldest = min(self._data.items(), key=lambda kv: kv[1][0])[0]
                self._data.pop(oldest, None)
            self._data[key] = (time.time() + ttl, value)

    def clear(self) -> None:
        with self._lock:
            self._data.clear()

    def stats(self) -> dict:
        with self._lock:
            now = time.time()
            live = sum(1 for exp, _ in self._data.values() if exp > now)
            return {"entries": len(self._data), "live": live, "maxsize": self._maxsize}


_GLOBAL = TTLCache()


def _make_key(fn: Callable, args: tuple, kwargs: dict) -> str:
    raw = f"{fn.__module__}.{fn.__qualname__}|{args!r}|{sorted(kwargs.items())!r}"
    # Hash rather than store the raw key: arguments include long prompt
    # strings, and keeping those as dict keys would bloat memory.
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def ttl_cache(ttl: int):
    """Cache a function's return value for `ttl` seconds.

    Exceptions are deliberately NOT cached — a transient upstream failure
    (Yahoo throttling, a rate-limited LLM call) must not be frozen in for
    the whole TTL. This mirrors the reasoning already documented in
    fetch_wikipedia_context, which raises rather than returning "" so a
    one-off blip can't lock every later caller into the failure.
    """
    def decorator(fn: Callable):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            key = _make_key(fn, args, kwargs)
            hit, value = _GLOBAL.get(key)
            if hit:
                return value
            result = fn(*args, **kwargs)
            _GLOBAL.set(key, result, ttl)
            return result

        wrapper.cache_clear = _GLOBAL.clear      # type: ignore[attr-defined]
        wrapper.cache_stats = _GLOBAL.stats      # type: ignore[attr-defined]
        return wrapper
    return decorator


def cache_stats() -> dict:
    return _GLOBAL.stats()


def cache_clear() -> None:
    _GLOBAL.clear()
