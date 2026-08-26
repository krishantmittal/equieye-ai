# services/nse_database.py
"""
NSE company database loading and search/disambiguation.

Extracted from app.py's load_nse_database() / search_nse_matches() /
BRAND_ALIASES verbatim, minus Streamlit coupling:
  - load_nse_database() no longer carries @st.cache_data — caching is the
    caller's concern (app.py wraps it with @st.cache_data; a future
    FastAPI service would cache it as a module-level singleton instead).
  - search_nse_matches() now takes `database` as an explicit parameter
    instead of calling load_nse_database() itself, and no longer calls
    st.error() on an empty database — callers decide how to surface that.
"""

from __future__ import annotations
import csv
import os

# ── Brand aliases (single source of truth) ─────────────────────────────────
# Maps common consumer brand names → official NSE ticker symbols. Needed
# because some companies trade under a legal name that differs from their
# consumer brand (e.g. Zomato → Eternal Limited after its 2024 rename).
BRAND_ALIASES: dict[str, str] = {
    "zomato": "ETERNAL.NS",
    "eternal": "ETERNAL.NS",
    "paytm": "PAYTM.NS",
}

_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "nse_equity_list.csv")


def load_nse_database(path: str | None = None) -> list[tuple[str, str]]:
    """
    Loads the official NSE-published list of all listed equities
    (downloaded from nseindia.com -> Market Data -> Securities Available
    for Trading -> Securities available for Equity segment).

    This is the ground-truth source: ~2,374 companies, exact symbols and
    legal names. Using this instead of probing a search API means company
    search is instant, complete, and has zero dependency on a third party
    API being reachable, rate-limited, or ranking results a certain way.

    Returns an empty list on any failure (missing file, malformed CSV) —
    callers must check for that and surface their own error.
    """
    companies: list[tuple[str, str]] = []
    try:
        with open(path or _DATA_PATH, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                symbol = row.get("SYMBOL", "").strip()
                name = row.get("NAME OF COMPANY", "").strip()
                if symbol and name:
                    companies.append((symbol + ".NS", name))
    except FileNotFoundError:
        pass
    except Exception:
        pass
    return companies


def search_nse_matches(query: str, database: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """
    Searches the given NSE company database for any company whose name
    or symbol contains the query (case-insensitive).

    Also checks BRAND_ALIASES first — common consumer brand names that
    differ from the company's official listed legal name (e.g. "Zomato"
    is listed as "Eternal Limited" after its 2024 rename, "Paytm" is
    listed as "One 97 Communications Limited"). Plain text matching
    against the NSE database alone can't catch these, since the brand
    name literally doesn't appear in the legal name.

    Returns a list of (symbol, long_name) tuples, deduplicated by symbol,
    sorted with exact/prefix matches first so the most likely intended
    company appears at the top of the picker.
    """
    query_clean = query.strip().lower()
    if not query_clean:
        return []

    if not database:
        return []

    if query_clean in BRAND_ALIASES:
        alias_symbol = BRAND_ALIASES[query_clean]
        for symbol, name in database:
            if symbol == alias_symbol:
                return [(symbol, name)]

    exact_symbol_matches = []
    prefix_matches = []
    contains_matches = []
    query_no_dot = query_clean.replace(".ns", "").strip()

    for symbol, name in database:
        symbol_clean = symbol.replace(".NS", "").lower()
        name_clean = name.lower()

        if symbol_clean == query_no_dot:
            exact_symbol_matches.append((symbol, name))
        elif name_clean.startswith(query_clean) or symbol_clean.startswith(query_no_dot):
            prefix_matches.append((symbol, name))
        elif query_clean in name_clean:
            contains_matches.append((symbol, name))

    ordered = exact_symbol_matches + prefix_matches + contains_matches

    seen = set()
    results = []
    for symbol, name in ordered:
        if symbol not in seen:
            seen.add(symbol)
            results.append((symbol, name))

    return results[:12]  # cap at 12 choices to keep UI usable
