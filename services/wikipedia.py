# services/wikipedia.py
"""
Wikipedia company-context lookup. Extracted from app.py's
fetch_wikipedia_context() verbatim, minus the @st.cache_data(ttl=86400)
decorator — caching stays app.py's concern.
"""

from __future__ import annotations
import requests


def fetch_wikipedia_context(company_name: str) -> str:
    """
    Fetches a structured company description from Wikipedia's free public API.
    This is the most reliable source for 'what does this company actually do'
    including subsidiaries and business segments — far more accurate than
    yfinance's longBusinessSummary which is often stale corporate boilerplate.

    Returns the Wikipedia extract (first ~1500 chars) if found.
    No API key required — Wikipedia's REST API is fully free and public.

    Search strategy: try multiple query variants to maximize hit rate:
    1. "{company_name} company India" — catches renamed companies like Eternal
    2. "{company_name}" — direct match
    3. "{company_name} Limited" — catches BSE/NSE legal name format

    Raises ValueError if nothing is found for any variant. Callers should
    NOT cache a caught exception from this — a single transient Wikipedia
    timeout/rate-limit blip would otherwise lock a cached failure in place
    for the full TTL. The caller's own try/except should turn this back
    into "" for that one call only, so the next call gets a fresh attempt.
    """
    headers = {"User-Agent": "EquiEyeAI/1.0 (educational stock research app)"}
    base_url = "https://en.wikipedia.org/api/rest_v1/page/summary/"

    clean_name = company_name.replace(" Limited", "").replace(" Ltd", "").replace(" Ltd.", "").strip()

    search_url = "https://en.wikipedia.org/w/api.php"

    def try_direct(title: str) -> str:
        try:
            r = requests.get(base_url + requests.utils.quote(title), headers=headers, timeout=5)
            if r.status_code == 200:
                data = r.json()
                if data.get("type") != "disambiguation":
                    extract = data.get("extract", "")
                    if extract and len(extract) > 100:
                        return extract[:2000]
        except Exception:
            pass
        return ""

    def try_search(query: str) -> str:
        try:
            params = {
                "action": "query", "list": "search",
                "srsearch": query, "srlimit": 3,
                "format": "json", "srinfo": "suggestion"
            }
            r = requests.get(search_url, params=params, headers=headers, timeout=5)
            if r.status_code == 200:
                results = r.json().get("query", {}).get("search", [])
                for result in results:
                    title = result.get("title", "")
                    extract = try_direct(title)
                    if extract:
                        return extract
        except Exception:
            pass
        return ""

    for attempt in [
        clean_name,
        f"{clean_name} company",
        f"{clean_name} India",
        company_name,
    ]:
        result = try_direct(attempt)
        if result:
            return result

    result = try_search(f"{clean_name} India company")
    if result:
        return result

    raise ValueError(f"No Wikipedia extract found for '{company_name}'")
