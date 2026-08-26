# services/news.py
"""
NewsAPI fetch + relevance filtering for a given ticker.

Extracted from app.py's fetch_relevant_news() / fetch_news_for_llm_context()
verbatim, minus Streamlit coupling: the NewsAPI key is now an explicit
parameter instead of being read from st.secrets inside the function, and
neither function carries an @st.cache_data decorator any more — caching
stays app.py's concern (15 min for the user-facing call, 1 hour for the
LLM-context call — see the docstring on fetch_news_for_llm_context below
for why those TTLs deliberately differ).
"""

from __future__ import annotations
import requests

# NewsAPI works best with the popular brand name, not the legal name.
# "Zomato" finds 10x more relevant articles than "Eternal Limited".
# "HDFC Bank" is cleaner than "HDFC Bank Limited".
NEWS_BRAND_ALIASES: dict[str, list[str]] = {
    "ETERNAL.NS":       ["Zomato", "Blinkit", "Eternal Limited"],
    "PAYTM.NS":         ["Paytm"],
    "INDUSTOWER.NS":    ["Indus Towers"],
    "HDFCBANK.NS":      ["HDFC Bank"],
    "ICICIBANK.NS":     ["ICICI Bank"],
    "SBIN.NS":          ["SBI", "State Bank of India"],
    "KOTAKBANK.NS":     ["Kotak Mahindra Bank", "Kotak Bank"],
    "AXISBANK.NS":      ["Axis Bank"],
    "INDUSINDBK.NS":    ["IndusInd Bank"],
    "FEDERALBNK.NS":    ["Federal Bank"],
    "BANDHANBNK.NS":    ["Bandhan Bank"],
    "IDFCFIRSTB.NS":    ["IDFC First Bank"],
    "PNB.NS":           ["Punjab National Bank", "PNB"],
    "BANKBARODA.NS":    ["Bank of Baroda"],
    "CANBK.NS":         ["Canara Bank"],
    "UNIONBANK.NS":     ["Union Bank of India"],
    "INDIANB.NS":       ["Indian Bank"],
    "HDFCLIFE.NS":      ["HDFC Life"],
    "SBILIFE.NS":       ["SBI Life"],
    "ICICIGI.NS":       ["ICICI Lombard"],
    "ICICIPRULI.NS":    ["ICICI Prudential"],
    "LICI.NS":          ["LIC", "Life Insurance Corporation"],
    "NIACL.NS":         ["New India Assurance"],
    "RELIANCE.NS":      ["Reliance Industries", "Reliance"],
    "ADANIENT.NS":      ["Adani Enterprises"],
    "ADANIPORTS.NS":    ["Adani Ports"],
    "ADANIGREEN.NS":    ["Adani Green"],
    "ADANIPOWER.NS":    ["Adani Power"],
    "ADANITRANS.NS":    ["Adani Transmission"],
    "TATAMOTORS.NS":    ["Tata Motors"],
    "TATASTEEL.NS":     ["Tata Steel"],
    "TCS.NS":           ["TCS", "Tata Consultancy Services"],
    "TATACONSUM.NS":    ["Tata Consumer Products", "Tata Consumer"],
    "TATACHEM.NS":      ["Tata Chemicals"],
    "TATAPOWER.NS":     ["Tata Power"],
    "TITAN.NS":         ["Titan Company", "Titan"],
    "TRENT.NS":         ["Trent"],
    "INFY.NS":          ["Infosys"],
    "WIPRO.NS":         ["Wipro"],
    "HCLTECH.NS":       ["HCL Technologies", "HCL Tech"],
    "TECHM.NS":         ["Tech Mahindra"],
    "LTIM.NS":          ["LTIMindtree"],
    "MPHASIS.NS":       ["Mphasis"],
    "COFORGE.NS":       ["Coforge"],
    "PERSISTENT.NS":    ["Persistent Systems"],
    "LTTS.NS":          ["L&T Technology Services"],
    "HINDUNILVR.NS":    ["Hindustan Unilever", "HUL"],
    "ITC.NS":           ["ITC"],
    "NESTLEIND.NS":     ["Nestle India"],
    "BRITANNIA.NS":     ["Britannia Industries", "Britannia"],
    "DABUR.NS":         ["Dabur"],
    "MARICO.NS":        ["Marico"],
    "COLPAL.NS":        ["Colgate Palmolive", "Colgate"],
    "GODREJCP.NS":      ["Godrej Consumer Products"],
    "EMAMILTD.NS":      ["Emami"],
    "MARUTI.NS":        ["Maruti Suzuki", "Maruti"],
    "M&M.NS":           ["Mahindra"],
    "BAJAJ-AUTO.NS":    ["Bajaj Auto"],
    "HEROMOTOCO.NS":    ["Hero MotoCorp"],
    "EICHERMOT.NS":     ["Eicher Motors", "Royal Enfield"],
    "ASHOKLEY.NS":      ["Ashok Leyland"],
    "MOTHERSON.NS":     ["Samvardhana Motherson"],
    "BALKRISIND.NS":    ["Balkrishna Industries", "BKT"],
    "SUNPHARMA.NS":     ["Sun Pharma", "Sun Pharmaceutical"],
    "DRREDDY.NS":       ["Dr Reddy's"],
    "CIPLA.NS":         ["Cipla"],
    "DIVISLAB.NS":      ["Divi's Laboratories", "Divi's"],
    "APOLLOHOSP.NS":    ["Apollo Hospitals"],
    "LUPIN.NS":         ["Lupin"],
    "TORNTPHARM.NS":    ["Torrent Pharma"],
    "BIOCON.NS":        ["Biocon"],
    "BAJFINANCE.NS":    ["Bajaj Finance"],
    "BAJAJFINSV.NS":    ["Bajaj Finserv"],
    "CHOLAFIN.NS":      ["Cholamandalam Finance"],
    "MUTHOOTFIN.NS":    ["Muthoot Finance"],
    "MANAPPURAM.NS":    ["Manappuram Finance"],
    "SHRIRAMFIN.NS":    ["Shriram Finance"],
    "M&MFIN.NS":        ["Mahindra Finance"],
    "LICHSGFIN.NS":     ["LIC Housing Finance"],
    "NYKAA.NS":         ["Nykaa", "FSN E-Commerce"],
    "POLICYBZR.NS":     ["PolicyBazaar", "PB Fintech"],
    "DELHIVERY.NS":     ["Delhivery"],
    "CARTRADE.NS":      ["CarTrade"],
    "IRCTC.NS":         ["IRCTC"],
    "DMART.NS":         ["DMart", "Avenue Supermarts"],
    "TATACOMM.NS":      ["Tata Communications"],
    "IDEA.NS":          ["Vodafone Idea", "Vi"],
    "BHARTIARTL.NS":    ["Airtel", "Bharti Airtel"],
    "JIOFINANCE.NS":    ["Jio Finance"],
    "NTPC.NS":          ["NTPC"],
    "POWERGRID.NS":     ["Power Grid"],
    "COALINDIA.NS":     ["Coal India"],
    "ONGC.NS":          ["ONGC", "Oil and Natural Gas"],
    "IOC.NS":           ["Indian Oil", "IOC"],
    "BPCL.NS":          ["BPCL", "Bharat Petroleum"],
    "HINDPETRO.NS":     ["HPCL", "Hindustan Petroleum"],
    "GAIL.NS":          ["GAIL"],
    "RECLTD.NS":        ["REC"],
    "PFC.NS":           ["Power Finance Corporation", "PFC"],
    "LT.NS":            ["Larsen & Toubro", "L&T"],
    "ULTRACEMCO.NS":    ["UltraTech Cement"],
    "GRASIM.NS":        ["Grasim"],
    "AMBUJACEM.NS":     ["Ambuja Cements"],
    "ACC.NS":           ["ACC"],
    "SHREECEM.NS":      ["Shree Cement"],
    "SIEMENS.NS":       ["Siemens India"],
    "ABB.NS":           ["ABB India"],
    "HAVELLS.NS":       ["Havells"],
    "JSWSTEEL.NS":      ["JSW Steel"],
    "HINDALCO.NS":      ["Hindalco"],
    "VEDL.NS":          ["Vedanta"],
    "NMDC.NS":          ["NMDC"],
    "SAIL.NS":          ["SAIL", "Steel Authority"],
    "BSE.NS":           ["BSE", "Bombay Stock Exchange"],
    "CDSL.NS":          ["CDSL"],
    "MCX.NS":           ["MCX"],
    "ANGELONE.NS":      ["Angel One"],
    "MOFSL.NS":         ["Motilal Oswal"],
    # ── Ambiguous ticker roots — bare acronym collides with an unrelated
    # common word/name, so we deliberately do NOT include the bare
    # ticker_root the way the auto-derive path below would. "HAL" alone
    # matched NewsAPI articles about an unrelated person named "Hal"
    # (obituaries, entertainment pieces) because NewsAPI's quoted-phrase
    # match is case-insensitive and "HAL" is also a common first-name
    # short form — the AND-clause keywords (market, results, etc.) were
    # coincidentally present in some of those unrelated articles too,
    # so they passed the filter. Same risk for "BEL" (a common name/word
    # in several languages). Mirrors the existing "SAIL" alias below,
    # which already worked around the identical problem for that ticker.
    "HAL.NS":           ["Hindustan Aeronautics"],
    "BEL.NS":           ["Bharat Electronics"],
}

# Tickers whose brand/legal name collides with an unrelated common word or
# phrase — an article can pass the corporate-signal check by coincidence
# (a stock-market word appearing near an unrelated story) without actually
# being about the company. Only these tickers get the stricter treatment
# of discarding results entirely rather than falling back to unvalidated ones.
_GEO_AMBIGUOUS_TICKERS: dict[str, list[str]] = {
    "BRITANNIA.NS": ["united kingdom", "uk government", "brexit", "britain's",
                     "downing street", "parliament", "prime minister",
                     "british government", "british politics", "cold snap",
                     "frigid", "weather", "climate", "winter"],
    "TITAN.NS":     ["greek myth", "saturn moon", "nasa", "space"],
    "ITC.NS":       ["itc hotel", "international trade"],
}
_CORPORATE_SIGNALS = [
    "nse", "bse", "sensex", "nifty", "sebi", "stock", "shares", "equity",
    "rupee", "rupees", "₹", "crore", "lakh", "quarterly", "earnings",
    "revenue", "profit", "dividend", "ipo", "india", "indian",
    "market cap", "analyst", "investor", "portfolio",
]


def _is_corporate_article(article: dict, ticker_sym: str) -> bool:
    combined = (
        (article.get("title") or "") + " " +
        (article.get("description") or "")
    ).lower()
    has_corporate_signal = any(sig in combined for sig in _CORPORATE_SIGNALS)
    if not has_corporate_signal:
        return False
    blocklist = _GEO_AMBIGUOUS_TICKERS.get(ticker_sym, [])
    if blocklist and any(term in combined for term in blocklist):
        return False
    return True


def fetch_relevant_news(ticker: str, name: str, news_api_key: str | None) -> dict:
    """
    Fetch + filter NewsAPI articles for a ticker. Pure data function — no
    Streamlit UI calls. Callers inspect the returned "error" field and
    render their own UI for it.

    Returns:
        {
          "search_terms": [...],
          "relevant_articles": [...],   # title-matched + corporate-validated
          "error": None | "rate_limit" | "invalid_key" | "http_error" |
                   "api_error" | "no_key",
          "error_detail": str | None,   # extra context for http_error/api_error
        }
    On any failure, relevant_articles is [] — callers must treat that as
    "no news available" and proceed without it; this must never block the
    main stock analysis.
    """
    empty = {"search_terms": [], "relevant_articles": [], "error": None, "error_detail": None}
    if not news_api_key:
        return {**empty, "error": "no_key"}

    # ── Step 1: Resolve the best search term for this ticker ──────────────
    if ticker in NEWS_BRAND_ALIASES:
        search_terms = NEWS_BRAND_ALIASES[ticker]
    else:
        _clean = name
        for suffix in [
            " Limited", " Ltd.", " Ltd", " Private", " Pvt",
            " Corporation", " Corp", " Industries", " Industry",
            " Enterprises", " Enterprise", " International",
            " Solutions", " Services", " Technologies", " Technology",
            " Ventures", " Holdings", " Group",
        ]:
            _clean = _clean.replace(suffix, "")
        _clean = _clean.strip()
        ticker_root = ticker.replace(".NS", "")
        if _clean and _clean != ticker_root:
            search_terms = [_clean, ticker_root]
        else:
            search_terms = [ticker_root]

    # ── Step 2: Build the NewsAPI query ────────────────────────────────────
    quoted_terms = " OR ".join(f'"{t}"' for t in search_terms)
    search_query = (
        f'({quoted_terms}) AND '
        f'(stock OR shares OR NSE OR BSE OR earnings OR revenue OR '
        f'quarterly OR investors OR market OR profit OR results OR IPO)'
    )
    news_url = (
        f"https://newsapi.org/v2/everything"
        f"?q={requests.utils.quote(search_query)}"
        f"&language=en&sortBy=publishedAt&pageSize=20&apiKey={news_api_key}"
    )
    try:
        news_response = requests.get(news_url, timeout=5)
    except Exception as e:
        return {**empty, "search_terms": search_terms, "error": "http_error", "error_detail": str(e)}

    if news_response.status_code == 429:
        return {**empty, "search_terms": search_terms, "error": "rate_limit"}
    elif news_response.status_code == 401:
        return {**empty, "search_terms": search_terms, "error": "invalid_key"}
    elif news_response.status_code != 200:
        return {**empty, "search_terms": search_terms, "error": "http_error",
                "error_detail": str(news_response.status_code)}

    news_data = news_response.json()
    if news_data.get("status") == "error":
        return {**empty, "search_terms": search_terms, "error": "api_error",
                "error_detail": news_data.get("message", "unknown error")}
    articles = news_data.get("articles", [])

    # ── Step 3: Filter — keyword must appear in the article TITLE ─────────
    kw_lower = [t.lower() for t in search_terms]

    def title_matches(article):
        title = (article.get("title") or "").lower()
        return any(kw in title for kw in kw_lower)

    def title_or_desc_matches(article):
        combined = (
            (article.get("title") or "") + " " +
            (article.get("description") or "")
        ).lower()
        return any(kw in combined for kw in kw_lower)

    relevant_articles = [a for a in articles if a.get("title") and title_matches(a)]
    if not relevant_articles:
        relevant_articles = [a for a in articles if a.get("title") and title_or_desc_matches(a)]

    # ── Step 4: Geo-ambiguity & corporate entity validator ─────────────────
    validated = [a for a in relevant_articles if _is_corporate_article(a, ticker)]
    is_geo_ambiguous = ticker in _GEO_AMBIGUOUS_TICKERS
    if validated:
        relevant_articles = validated
    elif not is_geo_ambiguous:
        pass
    else:
        relevant_articles = []

    return {"search_terms": search_terms, "relevant_articles": relevant_articles,
            "error": None, "error_detail": None}


def fetch_news_for_llm_context(ticker: str, name: str, news_api_key: str | None) -> dict:
    """Same data as fetch_relevant_news() — kept as a separate call site
    (rather than callers reusing fetch_relevant_news() directly) so app.py
    can cache this one for a full hour instead of 15 minutes.

    Why that distinction exists: the combined-analysis LLM prompt embeds
    the top-3 headlines so bull/bear can reference current events. The
    Groq response for that prompt is itself cached for 1 hour. If the
    embedded headlines came from a 15-min-TTL fetch, the prompt text — and
    therefore the cache key — would change roughly 4x more often than the
    response cache's own TTL, forcing a fresh Groq call almost every 15
    minutes instead of every hour for a stock people keep coming back to.
    """
    return fetch_relevant_news(ticker, name, news_api_key)
