# services/comparison.py
"""
Compare Stocks scoring/formatting helpers. Extracted from app.py's
_cagr_from_fin() / _cmp_eps_cagr() / _val_badge() / _winner() / _cell() /
_fmt_pct() / _fmt_cagr() / _fmt_de() / _fmt_pe() / _score_stock()
verbatim — pure logic, no Streamlit dependency (they only ever called
classify_sector / compute_health_score / get_pe_bands, all already
Streamlit-free).

Note: fmt_de_compare() here is deliberately distinct from
services.formatters.fmt_de() — this one is the simpler 2-decimal-only
formatter the Compare Stocks table has always used, not the near-zero
3-decimal variant used on the main Stock Research page.
"""

from __future__ import annotations

from services.formatters import get_pe_bands
from services.financial_utils import is_quarterly_financials, trim_to_last_discontinuity

# Guarded exactly like app.py's own top-level modules/ import — if modules/
# fails to load, score_stock() falls back to the generic 4-pillar formula
# below instead of raising, matching the original app.py behaviour.
try:
    from modules.sector_analysis import classify_sector
    from modules.health_score import compute_health_score
    _MODULES_LOADED = True
except Exception:
    _MODULES_LOADED = False
    classify_sector = None
    compute_health_score = None


def cagr_from_fin(fin, row_keys):
    """Return (cagr_pct, yoy_pct, n_years) from a financials DataFrame for first matching row key."""
    if fin is None or fin.empty:
        return None, None, None

    # `fin` may silently be quarterly_financials instead of annual (see
    # fetch_stock's fallback) — treating quarter-spaced columns as
    # year-spaced would mislabel N quarters as "N-yr CAGR" and turn YoY
    # into an accidental quarter-over-quarter comparison. Same guard as
    # the main analysis page's CAGR block, via the shared classifier.
    fin_is_quarterly = is_quarterly_financials(fin)

    for key in row_keys:
        if key in fin.index:
            series = fin.loc[key].dropna().sort_index()
            if len(series) < 2:
                return None, None, None

            # Corporate-action guard (demerger/spinoff/major M&A stitching
            # a differently-sized entity's history onto one ticker) — see
            # trim_to_last_discontinuity docstring. Applied before both
            # branches below so neither CAGR nor YoY spans the break.
            series, _had_break = trim_to_last_discontinuity(series)
            if len(series) < 2:
                return None, None, None

            if fin_is_quarterly:
                # No genuine multi-year span to CAGR — leave it None rather
                # than mislabel quarters as years. True YoY needs the same
                # quarter a year ago (4 quarters back), not the adjacent
                # quarter (which would be QoQ, not YoY).
                yoy = None
                if len(series) >= 5:
                    year_ago_v, last_v = float(series.iloc[-5]), float(series.iloc[-1])
                    if year_ago_v and year_ago_v != 0:
                        yoy = ((last_v - year_ago_v) / abs(year_ago_v)) * 100
                return None, yoy, None

            oldest, newest = float(series.iloc[0]), float(series.iloc[-1])
            n = max(len(series) - 1, 1)
            yoy = None
            if len(series) >= 2:
                prev_v, last_v = float(series.iloc[-2]), float(series.iloc[-1])
                if prev_v and prev_v != 0:
                    yoy = ((last_v - prev_v) / abs(prev_v)) * 100
            cagr = None
            if oldest > 0 and newest > 0:
                cagr = ((newest / oldest) ** (1 / n) - 1) * 100
            return cagr, yoy, n
    return None, None, None


def cmp_eps_cagr(info, fin):
    """Approximate EPS CAGR from net income / shares outstanding."""
    if fin is None or fin.empty:
        return None
    shares = info.get("sharesOutstanding")
    if not shares:
        return None
    for key in ["Net Income", "Net Income Common Stockholders"]:
        if key in fin.index:
            series = fin.loc[key].dropna().sort_index()
            if len(series) < 2:
                return None
            eps_series = series / shares
            oldest_eps = float(eps_series.iloc[0])
            newest_eps = float(eps_series.iloc[-1])
            n = max(len(eps_series) - 1, 1)
            if oldest_eps > 0 and newest_eps > 0:
                return ((newest_eps / oldest_eps) ** (1 / n) - 1) * 100
    return None


def val_badge(pe, sector, industry, pb=None, name="", description=""):
    """Return an HTML valuation badge based on sector-appropriate valuation.
    Thresholds match the main Stock Research health score badge exactly:
      score >= 7  -> Attractive (Undervalued)
      score < 3   -> Expensive  (Overvalued)
      else        -> Fairly Valued
    Banks/NBFC/Insurance are judged on P/B (via the same sector-aware
    scoring engine used elsewhere), not a PE-band fallback that doesn't
    apply to them.
    """
    slug = classify_sector(sector or "", industry or "", name or "", description or "")
    if slug in ("banking", "nbfc", "insurance"):
        if pb is None or pb <= 0:
            return "<span class='val-badge val-fair'>—</span>"
        s = round(min(10, max(0, 10 - (pb - 0.5) * 3.5)), 1)
        if s >= 7:
            return "<span class='val-badge val-attractive'>🟢 Attractive</span>"
        elif s < 3:
            return "<span class='val-badge val-expensive'>🔴 Expensive</span>"
        else:
            return "<span class='val-badge val-fair'>🟡 Fairly Valued</span>"
    if pe is None:
        return "<span class='val-badge val-fair'>—</span>"
    low, high = get_pe_bands(sector or "", industry or "", slug=slug)
    if pe < low:
        return "<span class='val-badge val-attractive'>🟢 Attractive</span>"
    elif pe > high:
        return "<span class='val-badge val-expensive'>🔴 Expensive</span>"
    else:
        return "<span class='val-badge val-fair'>🟡 Fairly Valued</span>"


def winner(val_a, val_b, higher_is_better=True, tie_pct=5.0):
    """Return 'a', 'b', 'tie', or 'na'. tie_pct: relative % threshold for a tie."""
    if val_a is None or val_b is None:
        return "na"
    if val_a == val_b:
        return "tie"
    denom = abs(val_a) if abs(val_a) > abs(val_b) else abs(val_b)
    if denom == 0:
        return "tie"
    diff_pct = abs(val_a - val_b) / denom * 100
    if diff_pct <= tie_pct:
        return "tie"
    if higher_is_better:
        return "a" if val_a > val_b else "b"
    else:
        return "a" if val_a < val_b else "b"


def cell(display_str, winner_side, this_side):
    """Return styled HTML for a compare-table value cell."""
    if winner_side == "na":
        return f"<div style='padding:10px; font-size:13px; color:#1F2937; border-bottom:1px solid #E5E7EB;'>{display_str}</div>"
    if winner_side == "tie":
        return f"<div style='padding:10px; font-size:13px; color:#1F2937; border-bottom:1px solid #E5E7EB;'>{display_str} <span class='cmp-tie'>≈ Tie</span></div>"
    if winner_side == this_side:
        cls = "cmp-winner-a" if this_side == "a" else "cmp-winner-b"
        return f"<div style='padding:10px; font-size:13px; border-bottom:1px solid #E5E7EB;' class='{cls}'>🏆 {display_str}</div>"
    return f"<div style='padding:10px; font-size:13px; color:#1F2937; border-bottom:1px solid #E5E7EB;'>{display_str}</div>"


def fmt_pct(v, scale=100):
    return f"{v*scale:.1f}%" if v is not None else "N/A"


def fmt_cagr(v, n_years=None):
    if v is None:
        return "N/A"
    prefix = f"{n_years}-yr " if n_years else ""
    return f"{prefix}{v:.1f}%"


def fmt_de_compare(v):
    # yfinance D/E already in percentage form — divide by 100 for display
    return f"{v/100:.2f}x" if v is not None else "N/A"


def fmt_pe(v):
    return f"{v:.1f}x" if v is not None else "N/A"


def score_stock(pe, roe, de, pm, rev_cagr, profit_cagr, sector, industry, pb=None,
                 extra_metrics=None, name="", description=""):
    """
    Returns a 0-10 composite score, routed through the sector-aware
    compute_health_score() engine so a bank is scored against banking
    criteria, an IT services company against IT criteria, etc., instead
    of one fixed generic 4-pillar formula for every sector.

    Falls back to a generic 4-pillar formula when compute_health_score
    can't produce a score (e.g. truly no data).

    Return contract: (total_score 0-10, pillar_scores dict with keys
    "valuation"/"profitability"/"growth"/"balance_sheet").

    pb / extra_metrics: without pb, banks/NBFCs/insurers can never score
    a Valuation pillar (they're scored on P/B, not P/E), and without
    extra_metrics, Cash Generation / Asset Quality / Capital Adequacy
    pillars are always unavailable here even when they're populated on
    the main page for the same ticker.
    """
    try:
        health = compute_health_score(
            pe=pe, pb=pb, roe_raw=roe, de_raw=de, profit_margin_raw=pm,
            revenue_cagr=rev_cagr, profit_cagr=profit_cagr,
            sector=sector, industry=industry,
            name=name, description=description,
            extra_metrics=extra_metrics,
        )
        sub = health.get("sub_scores", {})
        pillar_scores = {
            "valuation":      sub.get("Valuation")     if sub.get("Valuation")     is not None else 5.0,
            "profitability":  sub.get("Profitability") if sub.get("Profitability") is not None else 5.0,
            "growth":         sub.get("Growth")         if sub.get("Growth")         is not None else 5.0,
            "balance_sheet":  sub.get("Balance Sheet")  if sub.get("Balance Sheet")  is not None else 5.0,
        }
        if health.get("score") is not None:
            return health["score"], pillar_scores
    except Exception:
        pass  # fall through to generic formula below

    scores = []
    # Valuation (25%) — lower PE relative to band is better
    if pe is not None and pe > 0:   # negative PE = loss-making trailing period → neutral
        _fallback_slug = classify_sector(sector or "", industry or "", name or "", description or "")
        low, high = get_pe_bands(sector or "", industry or "", slug=_fallback_slug)
        band = high - low
        val_score = max(0, min(10, 10 - ((pe - low) / band) * 10)) if band > 0 else 5.0
    else:
        val_score = 5.0   # unknown or negative PE → neutral
    scores.append(("valuation", val_score, 0.25))

    # Profitability (25%)
    # Divisors calibrated to Indian listed-company distribution:
    #   ROE: /4  -> 40% ROE = 10/10 (p95 of NSE universe ~= 35-45%)
    #   PM:  /3  -> 30% margin = 10/10 (high but achievable for pharma/IT)
    roe_score = min(10, max(0, (roe * 100 / 4))) if roe is not None else 5.0
    pm_score  = min(10, max(0, (pm  * 100 / 3))) if pm  is not None else 5.0
    scores.append(("profitability", round((roe_score + pm_score) / 2, 1), 0.25))

    # Growth (25%)
    # CAGR values are in percentage points (e.g. 15.0 for 15%).
    # /3 divisor: 30% CAGR = 10/10 — reasonable ceiling for sustained FY growth.
    # Profit CAGR for turnaround companies (loss->profit) can be extreme (>200%);
    # min(10,...) clamp already handles this correctly.
    rc_score = min(10, max(0, (rev_cagr    / 3))) if rev_cagr    is not None else 5.0
    pc_score = min(10, max(0, (profit_cagr / 3))) if profit_cagr is not None else 5.0
    scores.append(("growth", round((rc_score + pc_score) / 2, 1), 0.25))

    # Balance sheet (25%) — lower D/E is better; 0 = perfect
    # de comes from yfinance in percentage form (e.g. 14.8 → actual D/E 0.15)
    if de is not None:
        de_norm = de / 100
        bs_score = max(0, min(10, 10 - de_norm * 2))
    else:
        bs_score = 5.0
    scores.append(("balance_sheet", round(bs_score, 1), 0.25))

    total = sum(s * w for _, s, w in scores)
    pillar_scores = {k: round(s, 1) for k, s, _ in scores}
    return round(total, 1), pillar_scores
