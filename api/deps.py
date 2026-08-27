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

from core.config import get_settings
from core.cache import ttl_cache
from services import market_data, news as news_svc, wikipedia as wiki_svc
from services.nse_database import load_nse_database, search_nse_matches

_s = get_settings()


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
    return market_data.fetch_quote(ticker)


@ttl_cache(ttl=_s.quote_ttl)
def cached_stock(ticker: str):
    """Full fetch: info + history + financials + balance sheet + cashflow."""
    return market_data.fetch_stock(ticker)


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
