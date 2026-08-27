# api/routers/stocks.py
"""Fast endpoints — yfinance data plus pure computation, no LLM calls."""

from __future__ import annotations
import math
from fastapi import APIRouter, HTTPException, Query

from api.deps import (
    search_companies, cached_quote, cached_stock,
    cached_price_history, cached_news,
)
from services.market_data import is_connectivity_error
from services.derived_metrics import compute_derived_metrics, compute_ev_ebitda
from services.comparison import cagr_from_fin
from services.formatters import fmt_crore, pct
from modules.health_score import compute_health_score
from modules.red_flags import detect_flags
from modules.risk_meter import compute_risk
from modules.sector_analysis import classify_sector, get_sector_display_name
from modules.news_sentiment import deduplicate_articles, enrich_articles, compute_overall_sentiment

router = APIRouter()

_REV_KEYS = ["Total Revenue", "Revenue", "Total Revenues"]
_PROFIT_KEYS = ["Net Income", "Net Income Common Stockholders"]


def _clean(v):
    """JSON-safe scalar. NaN/Inf are not valid JSON and would otherwise
    serialise as bare `NaN`, which strict parsers (including JS
    JSON.parse) reject outright."""
    if v is None:
        return None
    try:
        f = float(v)
    except (TypeError, ValueError):
        return v
    return f if math.isfinite(f) else None


def _load(ticker: str):
    """Fetch a ticker or raise the right HTTP status.

    A connectivity failure is 503 (our side / upstream is down, retry
    later); a ticker that simply has no price is 404. Collapsing both into
    500 would make the frontend unable to tell 'try again' from 'this
    stock does not exist'."""
    try:
        info, hist, fin, bs, cf = cached_stock(ticker)
    except Exception as e:
        if is_connectivity_error(e):
            raise HTTPException(503, "Upstream market data is unreachable. Try again shortly.")
        raise HTTPException(502, f"Could not fetch data for {ticker}.")
    if not info or not (info.get("currentPrice") or info.get("regularMarketPrice")):
        raise HTTPException(404, f"No market data found for {ticker}.")
    return info, hist, fin, bs, cf


@router.get("/search")
def search(q: str = Query(..., min_length=1, max_length=64)):
    """Company search over the bundled NSE listing.

    Returns every match rather than guessing: an ambiguous group name
    ("Tata", "HDFC", "Bajaj") maps to several genuinely distinct listed
    entities, and silently picking one is how you end up showing HDFC Life
    to someone who asked for HDFC Bank.
    """
    results = search_companies(q)
    return {"query": q, "count": len(results), "results": results,
            "ambiguous": len(results) > 1}


@router.get("/stock/{ticker}")
def stock(ticker: str):
    """Core snapshot — price, valuation multiples, and derived metrics."""
    info, hist, fin, bs, cf = _load(ticker)

    price = info.get("currentPrice") or info.get("regularMarketPrice")
    prev = info.get("previousClose")
    mkt_cap = info.get("marketCap")
    sector = info.get("sector") or ""
    industry = info.get("industry") or ""
    name = info.get("longName") or info.get("shortName") or ticker
    description = info.get("longBusinessSummary") or ""

    derived = compute_derived_metrics(info, fin, bs)
    ev_ebitda = compute_ev_ebitda(info, mkt_cap, derived["total_debt"],
                                  derived["cash"], derived["ebitda"])
    slug = classify_sector(sector, industry, name, description)
    rev_cagr, rev_yoy, rev_n = cagr_from_fin(fin, _REV_KEYS)
    pft_cagr, pft_yoy, pft_n = cagr_from_fin(fin, _PROFIT_KEYS)

    return {
        "ticker": ticker,
        "name": name,
        "sector": sector,
        "industry": industry,
        "sector_slug": slug,
        "sector_display": get_sector_display_name(slug),
        "price": {
            "current": _clean(price),
            "previous_close": _clean(prev),
            "change_pct": _clean(pct(price, prev)),
            "day_high": _clean(info.get("dayHigh")),
            "day_low": _clean(info.get("dayLow")),
            "week52_high": _clean(info.get("fiftyTwoWeekHigh")),
            "week52_low": _clean(info.get("fiftyTwoWeekLow")),
        },
        "metrics": {
            "market_cap": _clean(mkt_cap),
            "market_cap_display": fmt_crore(mkt_cap),
            "pe": _clean(info.get("trailingPE")),
            "pb": _clean(info.get("priceToBook")),
            "roe": _clean(info.get("returnOnEquity")),
            "roa": _clean(info.get("returnOnAssets")),
            "debt_to_equity": _clean(info.get("debtToEquity")),
            "profit_margin": _clean(info.get("profitMargins")),
            "ebitda_margin": _clean(info.get("ebitdaMargins")),
            "current_ratio": _clean(info.get("currentRatio")),
            "dividend_yield": _clean(info.get("dividendYield")),
            "beta": _clean(info.get("beta")),
            "free_cash_flow": _clean(info.get("freeCashflow")),
            "total_revenue": _clean(info.get("totalRevenue")),
            "ev_ebitda": _clean(ev_ebitda),
            **{k: _clean(v) for k, v in derived.items()},
        },
        "growth": {
            "revenue_cagr": _clean(rev_cagr), "revenue_cagr_years": rev_n,
            "revenue_yoy": _clean(rev_yoy),
            "profit_cagr": _clean(pft_cagr), "profit_cagr_years": pft_n,
            "profit_yoy": _clean(pft_yoy),
        },
        "description": description,
    }


def _metrics_bundle(info, fin, bs):
    """Assemble the extra_metrics dict the scoring engine expects."""
    derived = compute_derived_metrics(info, fin, bs)
    mkt_cap = info.get("marketCap")
    return derived, {
        "fcf": info.get("freeCashflow"),
        "ocf": info.get("operatingCashflow"),
        "revenue": info.get("totalRevenue"),
        "roa": info.get("returnOnAssets"),
        "pb_ratio": info.get("priceToBook"),
        "ev_ebitda": compute_ev_ebitda(info, mkt_cap, derived["total_debt"],
                                       derived["cash"], derived["ebitda"]),
        "price_to_sales": info.get("priceToSalesTrailing12Months"),
        "net_debt_ebitda": derived["net_debt_ebitda"],
        "interest_coverage": derived["interest_coverage"],
        "receivable_days": derived["receivable_days"],
        "inventory_months": derived["inventory_months"],
    }


@router.get("/stock/{ticker}/health")
def health_score(ticker: str):
    """Sector-aware financial health score."""
    info, _, fin, bs, _ = _load(ticker)
    _, extra = _metrics_bundle(info, fin, bs)
    rev_cagr, _, _ = cagr_from_fin(fin, _REV_KEYS)
    pft_cagr, _, _ = cagr_from_fin(fin, _PROFIT_KEYS)

    result = compute_health_score(
        pe=info.get("trailingPE"), pb=info.get("priceToBook"),
        roe_raw=info.get("returnOnEquity"), de_raw=info.get("debtToEquity"),
        profit_margin_raw=info.get("profitMargins"),
        revenue_cagr=rev_cagr, profit_cagr=pft_cagr,
        current_ratio=info.get("currentRatio"),
        sector=info.get("sector") or "", industry=info.get("industry") or "",
        name=info.get("longName") or ticker,
        description=info.get("longBusinessSummary") or "",
        extra_metrics=extra,
    )
    return {
        "ticker": ticker,
        "score": _clean(result.get("score")),
        "explanation": result.get("explanation"),
        "color": result.get("color"),
        "sub_scores": {k: _clean(v) for k, v in (result.get("sub_scores") or {}).items()},
        "weights": result.get("_weights", {}),
        "metrics_missing": result.get("metrics_missing", []),
    }


@router.get("/stock/{ticker}/red-flags")
def red_flags(ticker: str):
    info, _, fin, bs, cf = _load(ticker)
    derived, _ = _metrics_bundle(info, fin, bs)
    rev_cagr, _, _ = cagr_from_fin(fin, _REV_KEYS)
    pft_cagr, _, _ = cagr_from_fin(fin, _PROFIT_KEYS)
    ebitda_m = info.get("ebitdaMargins")
    flags = detect_flags(
        pe=info.get("trailingPE"), roe_raw=info.get("returnOnEquity"),
        de_raw=info.get("debtToEquity"),
        profit_margin_raw=info.get("profitMargins"),
        free_cf=info.get("freeCashflow"),
        operating_cf=info.get("operatingCashflow"),
        rev=info.get("totalRevenue"),
        revenue_growth_pct=rev_cagr,
        profit_growth_pct=pft_cagr,
        ebitda_margin_pct=(ebitda_m * 100) if ebitda_m is not None else None,
        current_ratio=info.get("currentRatio"),
        sector=info.get("sector") or "", industry=info.get("industry") or "",
        name=info.get("longName") or ticker,
        description=info.get("longBusinessSummary") or "",
        extra_metrics=derived,
    )
    return {"ticker": ticker, "flags": flags, "count": len(flags or [])}


@router.get("/stock/{ticker}/risk")
def risk(ticker: str):
    info, _, fin, bs, _ = _load(ticker)
    derived, _ = _metrics_bundle(info, fin, bs)
    rev_cagr, _, _ = cagr_from_fin(fin, _REV_KEYS)
    pft_cagr, _, _ = cagr_from_fin(fin, _PROFIT_KEYS)
    ebitda_m = info.get("ebitdaMargins")
    result = compute_risk(
        pe=info.get("trailingPE"), de_raw=info.get("debtToEquity"),
        beta=info.get("beta"),
        free_cf=info.get("freeCashflow"),
        operating_cf=info.get("operatingCashflow"),
        profit_margin_raw=info.get("profitMargins"),
        sector=info.get("sector") or "", industry=info.get("industry") or "",
        name=info.get("longName") or ticker,
        description=info.get("longBusinessSummary") or "",
        ebitda_margin_pct=(ebitda_m * 100) if ebitda_m is not None else None,
        revenue_growth_pct=rev_cagr, profit_growth_pct=pft_cagr,
        current_ratio=info.get("currentRatio"),
        extra_metrics=derived,
    )
    return {"ticker": ticker, **result}


@router.get("/stock/{ticker}/price-history")
def price_history(
    ticker: str,
    period: str = Query("1mo", pattern="^(1d|5d|1mo|3mo|6mo|1y|2y|3y|5y|max)$"),
    interval: str = Query("1d", pattern="^(1m|5m|15m|30m|1h|1d|1wk|1mo)$"),
):
    try:
        hist = cached_price_history(ticker, period, interval)
    except Exception as e:
        if is_connectivity_error(e):
            raise HTTPException(503, "Upstream market data is unreachable.")
        raise HTTPException(502, f"Could not fetch price history for {ticker}.")
    if hist is None or hist.empty:
        return {"ticker": ticker, "period": period, "interval": interval, "points": []}

    points = [
        {"t": idx.isoformat(), "close": _clean(row.get("Close")),
         "volume": _clean(row.get("Volume"))}
        for idx, row in hist.iterrows()
    ]
    return {"ticker": ticker, "period": period, "interval": interval,
            "count": len(points), "points": points}


@router.get("/stock/{ticker}/news")
def news(ticker: str):
    """Headlines with sentiment. Never fails the request: news is
    supplementary, so a missing key or a rate limit returns an empty list
    plus a reason, and the page still renders."""
    info = cached_quote(ticker)
    name = info.get("longName") or info.get("shortName") or ticker
    payload = cached_news(ticker, name)
    articles = payload.get("relevant_articles") or []
    if articles:
        articles = enrich_articles(deduplicate_articles(articles))
    overall = compute_overall_sentiment(articles) if articles else None
    return {
        "ticker": ticker,
        "error": payload.get("error"),
        "error_detail": payload.get("error_detail"),
        "overall_sentiment": overall,
        "count": len(articles),
        "articles": articles[:10],
    }
