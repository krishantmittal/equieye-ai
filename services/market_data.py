# services/market_data.py
"""
yfinance data fetching. Extracted from app.py's fetch_stock() /
fetch_quote() / fetch_price_history() / _is_connectivity_error() verbatim,
minus the @st.cache_data(ttl=300) decorators — caching stays app.py's
concern (a future FastAPI service would use Redis with the same TTL).
"""

from __future__ import annotations
import time
import yfinance as yf


def is_connectivity_error(exc: Exception) -> bool:
    """Best-effort check for whether a fetch failure was actually a lack of
    internet connectivity (DNS/connection-level failure) rather than a data
    problem (bad ticker, delisting, a genuine Yahoo Finance API error, etc).
    yfinance/requests don't expose one clean exception type for this across
    platforms, so this matches on the exception class name and message text
    patterns that DNS/socket/connection failures consistently produce,
    regardless of which underlying library raised them.
    """
    text = f"{type(exc).__name__} {exc}".lower()
    return any(s in text for s in (
        "connectionerror", "nameresolutionerror", "max retries exceeded",
        "failed to establish a new connection", "name or service not known",
        "temporary failure in name resolution", "network is unreachable",
        "connection refused", "getaddrinfo failed", "socket.gaierror",
        "no address associated with hostname",
    ))


def fetch_stock(ticker: str):
    t = yf.Ticker(ticker)
    info = t.info

    # Retry up to 2 more times if price data is missing — handles Yahoo throttling
    attempts = 0
    while not info.get("currentPrice") and not info.get("regularMarketPrice") and attempts < 2:
        time.sleep(1.5 + attempts)
        t = yf.Ticker(ticker)
        info = t.info
        attempts += 1

    # Fallback to fast_info if still missing — copy dict first to avoid
    # mutating the cached object which causes stale/corrupted cache across reruns
    if not info.get("currentPrice") and not info.get("regularMarketPrice"):
        try:
            fi = t.fast_info
            info = dict(info)  # shallow copy before mutation
            info["currentPrice"] = fi.last_price
            info["previousClose"] = fi.previous_close
            info["marketCap"] = fi.market_cap
        except Exception:
            pass

    try:
        fin = t.financials
        if fin is None or fin.empty:
            fin = t.quarterly_financials
    except Exception:
        fin = None

    try:
        hist = t.history(period="3y", interval="1mo")
    except Exception:
        hist = None

    try:
        bs = t.balance_sheet
    except Exception:
        bs = None

    try:
        cf = t.cashflow
    except Exception:
        cf = None

    return info, hist, fin, bs, cf


def fetch_quote(ticker: str):
    """Lightweight quote-only fetch — price/mcap/PE fields only, no
    financials/history/balance-sheet/cashflow. Use this instead of
    fetch_stock() anywhere only `info` fields are needed (watchlist rows,
    portfolio rows, price-target checks, chat live-data grounding), to
    avoid firing 3 extra yfinance HTTP requests that get fetched and
    immediately discarded. Same retry/fallback behaviour as fetch_stock()
    for a missing price, just without the extra endpoints.
    """
    t = yf.Ticker(ticker)
    info = t.info

    attempts = 0
    while not info.get("currentPrice") and not info.get("regularMarketPrice") and attempts < 2:
        time.sleep(1.5 + attempts)
        t = yf.Ticker(ticker)
        info = t.info
        attempts += 1

    if not info.get("currentPrice") and not info.get("regularMarketPrice"):
        try:
            fi = t.fast_info
            info = dict(info)
            info["currentPrice"] = fi.last_price
            info["previousClose"] = fi.previous_close
            info["marketCap"] = fi.market_cap
        except Exception:
            pass

    return info


def fetch_price_history(sym: str, period: str, interval: str):
    """Cached per (symbol, period, interval) by the caller so toggling
    1D/1M/3M doesn't fire a fresh Yahoo Finance request on every click."""
    t_obj = yf.Ticker(sym)
    return t_obj.history(period=period, interval=interval)
