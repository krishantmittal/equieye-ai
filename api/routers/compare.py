# api/routers/compare.py
"""Head-to-head comparison — fast (no LLM); the AI verdict is separate."""

from __future__ import annotations
import math
from fastapi import APIRouter, HTTPException, Query

from api.deps import cached_stock
from services.market_data import is_connectivity_error
from services.comparison import cagr_from_fin, cmp_eps_cagr, score_stock, winner
from services.derived_metrics import compute_derived_metrics, compute_ev_ebitda
from services.formatters import fmt_crore
from modules.sector_analysis import classify_sector, get_sector_display_name

router = APIRouter()

_REV_KEYS = ["Total Revenue", "Revenue", "Total Revenues"]
_PROFIT_KEYS = ["Net Income", "Net Income Common Stockholders"]


def _clean(v):
    if v is None:
        return None
    try:
        f = float(v)
    except (TypeError, ValueError):
        return v
    return f if math.isfinite(f) else None


def _side(ticker: str) -> dict:
    try:
        info, _, fin, bs, _ = cached_stock(ticker)
    except HTTPException:
        raise
    except Exception as e:
        if is_connectivity_error(e):
            raise HTTPException(503, "Upstream market data is unreachable.")
        raise HTTPException(502, f"Could not fetch data for {ticker}.")
    if not info or not (info.get("currentPrice") or info.get("regularMarketPrice")):
        raise HTTPException(404, f"No market data found for {ticker}.")

    name = info.get("longName") or info.get("shortName") or ticker
    sector, industry = info.get("sector") or "", info.get("industry") or ""
    desc = info.get("longBusinessSummary") or ""
    mkt_cap = info.get("marketCap")

    derived = compute_derived_metrics(info, fin, bs)
    rev_cagr, rev_yoy, rev_n = cagr_from_fin(fin, _REV_KEYS)
    pft_cagr, pft_yoy, pft_n = cagr_from_fin(fin, _PROFIT_KEYS)

    extra = {
        "fcf": info.get("freeCashflow"), "ocf": info.get("operatingCashflow"),
        "revenue": info.get("totalRevenue"), "roa": info.get("returnOnAssets"),
        "pb_ratio": info.get("priceToBook"),
        "ev_ebitda": compute_ev_ebitda(info, mkt_cap, derived["total_debt"],
                                       derived["cash"], derived["ebitda"]),
        "price_to_sales": info.get("priceToSalesTrailing12Months"),
        **{k: derived[k] for k in
           ("net_debt_ebitda", "interest_coverage", "receivable_days", "inventory_months")},
    }
    score, pillars = score_stock(
        pe=info.get("trailingPE"), roe=info.get("returnOnEquity"),
        de=info.get("debtToEquity"), pm=info.get("profitMargins"),
        rev_cagr=rev_cagr, profit_cagr=pft_cagr,
        sector=sector, industry=industry, pb=info.get("priceToBook"),
        extra_metrics=extra, name=name, description=desc,
    )
    slug = classify_sector(sector, industry, name, desc)
    return {
        "ticker": ticker, "name": name,
        "sector": sector, "industry": industry,
        "sector_slug": slug, "sector_display": get_sector_display_name(slug),
        "score": _clean(score),
        "pillars": {k: _clean(v) for k, v in pillars.items()},
        "metrics": {
            "price": _clean(info.get("currentPrice") or info.get("regularMarketPrice")),
            "market_cap": _clean(mkt_cap),
            "market_cap_display": fmt_crore(mkt_cap),
            "pe": _clean(info.get("trailingPE")),
            "pb": _clean(info.get("priceToBook")),
            "roe": _clean(info.get("returnOnEquity")),
            "profit_margin": _clean(info.get("profitMargins")),
            "debt_to_equity": _clean(info.get("debtToEquity")),
            "total_revenue": _clean(info.get("totalRevenue")),
            "revenue_display": fmt_crore(info.get("totalRevenue")),
            "eps_cagr": _clean(cmp_eps_cagr(info, fin)),
        },
        "growth": {
            "revenue_cagr": _clean(rev_cagr), "revenue_cagr_years": rev_n,
            "revenue_yoy": _clean(rev_yoy),
            "profit_cagr": _clean(pft_cagr), "profit_cagr_years": pft_n,
            "profit_yoy": _clean(pft_yoy),
        },
    }


@router.get("/compare")
def compare(a: str = Query(..., min_length=1), b: str = Query(..., min_length=1)):
    """Compare two tickers.

    `winners` is computed server-side so both the web and any future
    client agree on who won a row — the tie threshold is a judgement call
    (5% relative), and duplicating it per client is how they drift apart.
    """
    sa, sb = _side(a), _side(b)

    winners = {
        "pe":             winner(sa["metrics"]["pe"], sb["metrics"]["pe"], higher_is_better=False),
        "roe":            winner(sa["metrics"]["roe"], sb["metrics"]["roe"]),
        "profit_margin":  winner(sa["metrics"]["profit_margin"], sb["metrics"]["profit_margin"]),
        "total_revenue":  winner(sa["metrics"]["total_revenue"], sb["metrics"]["total_revenue"]),
        "debt_to_equity": winner(sa["metrics"]["debt_to_equity"], sb["metrics"]["debt_to_equity"], higher_is_better=False),
        "revenue_cagr":   winner(sa["growth"]["revenue_cagr"], sb["growth"]["revenue_cagr"]),
        "profit_cagr":    winner(sa["growth"]["profit_cagr"], sb["growth"]["profit_cagr"]),
        "score":          winner(sa["score"], sb["score"]),
    }
    # Overall verdict. A sub-0.5 gap on a 0-10 composite is inside the
    # noise of the inputs, so it is reported as too-close-to-call rather
    # than manufacturing a winner from a rounding difference.
    gap = abs((sa["score"] or 0) - (sb["score"] or 0))
    overall = "tie" if gap < 0.5 else ("a" if (sa["score"] or 0) > (sb["score"] or 0) else "b")

    return {
        "a": sa, "b": sb, "winners": winners,
        "overall": overall, "score_gap": round(gap, 2),
        "cross_sector": sa["sector_slug"] != sb["sector_slug"],
    }
