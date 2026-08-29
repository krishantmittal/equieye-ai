# api/deps.py
"""
Cached wrappers around the service layer.

These are the FastAPI equivalent of app.py's @st.cache_data shims: the
service functions themselves stay pure and uncached, and each host applies
its own caching with the same TTLs. Keeping the TTLs in core.config means
the two hosts can't silently diverge.
"""

from __future__ import annotations
from functools import lru_cache

from fastapi import HTTPException

from core.config import get_settings
from core.cache import ttl_cache
from services import market_data, news as news_svc, wikipedia as wiki_svc
from services.nse_database import load_nse_database, search_nse_matches

_s = get_settings()


def _is_degraded_quote(info: dict) -> bool:
    """True when yfinance returned a price but almost nothing else.

    Observed in production on a hosted deploy: currentPrice and marketCap
    present, but longName/shortName/sector/trailingPE all empty — the
    signature of Yahoo Finance throttling the full quoteSummary scrape
    from a datacenter IP while still serving the lightweight price-only
    endpoint. Requiring BOTH name and sector absent (not just one) avoids
    misclassifying a genuinely thin instrument as degraded.
    """
    has_name = bool(info.get("longName") or info.get("shortName"))
    has_sector = bool(info.get("sector"))
    return not has_name and not has_sector


# The NSE list is a bundled static CSV (~2,374 rows) — load once per
# process rather than per request. Not a TTL cache: the file cannot change
# without a redeploy.
@lru_cache(maxsize=1)
def nse_database() -> list[tuple[str, str]]:
    return load_nse_database()


def search_companies(query: str) -> list[dict]:
    matches = search_nse_matches(query, nse_database())
    return [{"symbol": sym, "name": name} for sym, name in matches]


@ttl_cache(ttl=_s.quote_ttl)
def cached_quote(ticker: str) -> dict:
    info = market_data.fetch_quote(ticker)
    if info and (info.get("currentPrice") or info.get("regularMarketPrice")) and _is_degraded_quote(info):
        # Raise rather than return degraded data — ttl_cache never caches
        # an exception, so the next call gets a genuine fresh attempt
        # instead of being stuck behind this one for the full TTL.
        raise HTTPException(503, "Market data provider returned incomplete data. Try again shortly.")
    return info


@ttl_cache(ttl=_s.quote_ttl)
def cached_stock(ticker: str):
    """Full fetch: info + history + financials + balance sheet + cashflow.

    Raises when the response looks degraded (see _is_degraded_quote)
    instead of returning it as if it were a normal, complete result —
    every caller previously trusted "price present" as the only signal of
    success, so a stock page could render with a blank name and every
    metric empty while still returning HTTP 200. Not caching the failure
    also means a possibly-transient block gets retried on the next
    request rather than being frozen in for the full TTL.
    """
    info, hist, fin, bs, cf = market_data.fetch_stock(ticker)
    if info and (info.get("currentPrice") or info.get("regularMarketPrice")) and _is_degraded_quote(info):
        raise HTTPException(503, "Market data provider returned incomplete data for this "
                                  "ticker (price only, no company details). Try again shortly.")
    return info, hist, fin, bs, cf


@ttl_cache(ttl=_s.quote_ttl)
def cached_price_history(symbol: str, period: str, interval: str):
    return market_data.fetch_price_history(symbol, period, interval)


@ttl_cache(ttl=_s.news_ttl)
def cached_news(ticker: str, name: str) -> dict:
    return news_svc.fetch_relevant_news(ticker, name, _s.news_api_key)


@ttl_cache(ttl=_s.news_llm_ttl)
def cached_news_for_llm(ticker: str, name: str) -> dict:
    """Same fetch, longer TTL — see core.config.news_llm_ttl for why the
    prompt-grounding copy deliberately refreshes 4x less often."""
    return news_svc.fetch_relevant_news(ticker, name, _s.news_api_key)


@ttl_cache(ttl=_s.wiki_ttl)
def cached_wikipedia(company_name: str) -> str:
    """Raises when nothing is found — ttl_cache does not cache exceptions,
    so a transient Wikipedia blip can't freeze the weakest fallback tier
    in place for 24 hours."""
    return wiki_svc.fetch_wikipedia_context(company_name)
