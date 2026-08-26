# modules/moat_analysis.py
"""
Moat Analysis — Core Integration Layer
========================================
Public API consumed by app.py (signature preserved exactly, including
the TypeError-tolerant call pattern app.py uses — extra kwargs are all
optional so both the full call and the reduced fallback call succeed):

    get_moat_analysis(
        sector, industry,
        roe_raw=None, de_raw=None, revenue_cagr=None,
        name="", ticker="", profit_margin_raw=None, pe=None,
        mkt_cap_cr=None, ask_llm_fn=None,
    ) -> dict

Returns:
    {
        "rating": "Weak" | "Moderate" | "Strong",
        "score": float (0-10),
        "factors": list of {"factor": str, "description": str, "strength": str},
        "bull_case": list[str],
        "bear_case": list[str],
        "llm_verdict": str or None,
    }

Each sector module declares its own moat_factors / bull_case / bear_case
as plain data. This file classifies the company, derives a quantitative
moat-strength score from available financials (ROE, margin, revenue
CAGR — proxies for how durable the company's economics actually are),
and optionally asks an LLM for a short company-specific verdict.
"""

from __future__ import annotations
import json
from modules.sectors import get_sector_config
from modules.sectors.conglomerates import get_blended_commodity_weight
from modules.sector_analysis import classify_sector

# Sectors treated as commodity-price-driven for the moat quant score's
# cyclicality discount (see _quant_moat_score). Module-level so
# get_moat_analysis can also pass it to get_blended_commodity_weight().
_COMMODITY_CYCLICAL_SLUGS = ("metals_mining", "oil_gas")


def get_moat_analysis(
    sector: str = "", industry: str = "",
    roe_raw=None, de_raw=None, revenue_cagr=None,
    name: str = "", ticker: str = "",
    profit_margin_raw=None, pe=None,
    mkt_cap_cr=None, ask_llm_fn=None,
    description: str = "",
) -> dict:
    """
    Returns the sector-aware moat framework for a company, with a
    quantitative strength rating derived from its actual financials
    and (optionally) a company-specific LLM verdict layered on top.
    """
    slug = classify_sector(sector, industry, name, description)
    cfg = get_sector_config(slug)

    # For registered conglomerates (Reliance etc.), scale the commodity-
    # cyclicality discount by the actual EBITDA share sitting in
    # commodity-cyclical segments, instead of applying it at full strength
    # just because classify_sector()'s single primary-sector label happens
    # to be oil_gas/metals_mining. Falls straight through to the old
    # all-or-nothing behaviour (None) for every non-registered company.
    commodity_weight = get_blended_commodity_weight(name, _COMMODITY_CYCLICAL_SLUGS)
    quant_score = _quant_moat_score(roe_raw, profit_margin_raw, revenue_cagr, de_raw, slug,
                                     commodity_weight=commodity_weight)

    llm_verdict = None
    per_factor_ratings = None
    if ask_llm_fn is not None:
        llm_verdict, per_factor_ratings = _generate_llm_verdict(
            cfg, name or ticker or "This company", ask_llm_fn, description=description
        )

    # Prefer the LLM's per-factor judgment (it actually reasons about which
    # specific factors apply to this company) over blanket-applying one
    # company-wide quant score to every factor. Only fall back to the quant
    # rating for factors the LLM didn't return, or when there's no LLM call.
    factors = [
        {**factor, "strength": (per_factor_ratings or {}).get(factor["factor"], None)}
        for factor in cfg["moat_factors"]
    ]
    for f in factors:
        if f["strength"] is None:
            f["strength"] = "Strong" if quant_score >= 7 else "Moderate" if quant_score >= 4.5 else "Weak"

    # The headline rating/score must agree with the checklist it sits above —
    # previously the headline was always the pure quant score (ROE/margin/
    # growth/D-E only), so a numerically-flattering but qualitatively weak
    # business (e.g. a turnaround/cyclical name the LLM correctly flags as
    # "struggling") could show "Strong Moat 8.8/10" directly above a
    # checklist full of Weak/Moderate factors and prose calling it
    # "struggling" — a visible, confusing contradiction. When the LLM
    # provided per-factor ratings, blend them into the headline instead of
    # relying on the quant score alone.
    if per_factor_ratings:
        _points = {"Strong": 9.0, "Moderate": 5.5, "Weak": 2.0}
        _factor_avg = sum(_points[f["strength"]] for f in factors) / len(factors)
        # Average the LLM's qualitative read with the quant score rather than
        # replacing it outright — the quant score still reflects real,
        # verifiable financials and shouldn't be discarded entirely.
        score = round((quant_score + _factor_avg) / 2, 1)
    else:
        score = quant_score
    rating = "Strong" if score >= 7 else "Moderate" if score >= 4.5 else "Weak"

    return {
        "rating": rating,
        "score": score,
        "factors": factors,
        "bull_case": cfg["bull_case"],
        "bear_case": cfg["bear_case"],
        "llm_verdict": llm_verdict,
        "sector_slug": slug,
        "sector_display_name": cfg["display_name"],
    }


def _quant_moat_score(roe_raw, profit_margin_raw, revenue_cagr, de_raw, slug: str = "",
                       commodity_weight: float | None = None) -> float:
    """
    Derives a 0-10 moat strength proxy from available fundamentals.
    High, durable ROE + healthy margins + consistent growth + manageable
    leverage are the classic quantitative signatures of a wide-moat
    business (Buffett/Munger style screening), used here as a sensible
    default when no sector-specific moat score is independently computed.

    Margin and growth brackets are tiered by sector (mirroring the same
    "mature, structurally lower-margin/growth" cohort already used in
    health_score.py's own Profitability/Growth pillars) — a flat 20%-for-
    perfect margin bar and an 8%+-for-decent growth bar are software/pharma-
    tier benchmarks. Applied uniformly, they scored Britannia (13.2% net
    margin, 5.7% revenue CAGR — both genuinely strong for a bakery/staples
    FMCG business) at only 7/10 and 4/10 respectively, dragging down an
    otherwise excellent moat profile (53% ROE, 0.27x D/E).
    """
    _mature_tier = slug in ("fmcg", "power_utilities", "metals_mining")
    points = []

    if roe_raw is not None:
        roe_pct = roe_raw * 100  # yfinance returnOnEquity is always a decimal fraction
        if roe_pct >= 25:
            points.append(10)
        elif roe_pct >= 18:
            points.append(8)
        elif roe_pct >= 12:
            points.append(6)
        elif roe_pct >= 8:
            points.append(4)
        else:
            points.append(2)

    if profit_margin_raw is not None:
        margin_pct = profit_margin_raw * 100  # yfinance profitMargins is always a decimal fraction
        if _mature_tier:
            if margin_pct >= 16:
                points.append(10)
            elif margin_pct >= 10:
                points.append(8)
            elif margin_pct >= 6:
                points.append(6)
            else:
                points.append(3)
        else:
            if margin_pct >= 20:
                points.append(10)
            elif margin_pct >= 12:
                points.append(7)
            elif margin_pct >= 6:
                points.append(5)
            else:
                points.append(3)

    if revenue_cagr is not None:
        if _mature_tier:
            if revenue_cagr >= 10:
                points.append(9)
            elif revenue_cagr >= 5:
                points.append(7)
            elif revenue_cagr >= 0:
                points.append(5)
            else:
                points.append(2)
        else:
            if revenue_cagr >= 15:
                points.append(9)
            elif revenue_cagr >= 8:
                points.append(6)
            elif revenue_cagr >= 0:
                points.append(4)
            else:
                points.append(1)

    if de_raw is not None:
        # yfinance returns debtToEquity in percentage form for NSE stocks —
        # always divide by 100 (see health_score.py / risk_meter.py for the
        # same fix and why the old ">5" heuristic was wrong).
        de_ratio = de_raw / 100
        if de_ratio < 0.3:
            points.append(9)
        elif de_ratio < 0.8:
            points.append(6)
        elif de_ratio < 1.5:
            points.append(4)
        else:
            points.append(2)

    if not points:
        return 5.0  # neutral default when no financials are available

    raw_score = sum(points) / len(points)

    # Commodity-cyclicality discount: for a genuinely commodity-price-driven
    # business (metals & mining, oil & gas), a strong trailing margin/growth
    # snapshot mostly reflects WHERE THE COMMODITY CYCLE CURRENTLY SITS, not
    # a durable competitive advantage the way it does for a pricing-power or
    # brand business (FMCG, consumer). Scoring Vedanta's 22.6% margin / 24.5%
    # CAGR at face value (same curve treatment as a stable, structurally
    # protected business) produced an 8.2/10 "Strong Moat" that reads as
    # comparable to Asian Paints/Titan/HDFC Bank-tier pricing-power moats —
    # overstating what cost leadership + captive-integration actually buys a
    # commodity producer, whose margins are still ultimately price-takers on
    # the underlying metal/ore. This does NOT zero out the real structural
    # advantages (captive raw material, integration, scale, logistics) that
    # a moat can legitimately rest on for a cost-leadership commodity
    # producer — it discounts the current-year-fundamentals-derived portion
    # of the score, which is exactly the part a through-cycle assessment
    # should discount. Deliberately excludes power_utilities (regulated,
    # contracted tariffs — genuinely durable, not commodity-price-driven)
    # even though it shares the "mature tier" margin/growth brackets above.
    # `commodity_weight` (0-1), when supplied by a registered conglomerate
    # entry, scales the discount by the actual EBITDA share sitting in
    # commodity-cyclical segments (e.g. Reliance's O2C+E&P is ~36% of
    # EBITDA, not 100%) rather than applying the full -1.5 just because the
    # single primary-sector label happens to be oil_gas/metals_mining. For
    # every non-registered company, commodity_weight is None and this falls
    # straight through to the old all-or-nothing behaviour.
    if commodity_weight is not None:
        raw_score = max(1.0, raw_score - 1.5 * commodity_weight)
    elif slug in _COMMODITY_CYCLICAL_SLUGS:
        raw_score = max(1.0, raw_score - 1.5)

    return round(raw_score, 1)


def _generate_llm_verdict(cfg: dict, company_name: str, ask_llm, description: str = "") -> tuple[str | None, dict | None]:
    """Returns (verdict_text, per_factor_ratings). per_factor_ratings maps each
    factor name to 'Strong'/'Moderate'/'Weak' — this is what actually drives
    the checklist icons. Without this, every factor was shown with the same
    checkmark (derived from one company-wide quant score), even when the
    verdict's own prose said a factor was weak for this company — a direct
    contradiction visible on the same card.

    `description` (the same business_context app.py builds from Wikipedia /
    company filing) is what actually lets this differ between two companies
    in the same sector module — e.g. Bharat Electronics vs Hindustan
    Aeronautics both get the "defense_aerospace" framework, but BEL is
    primarily an electronics/radar/EW business while HAL is primarily an
    aircraft/engine manufacturer. Previously this function only received
    the company name and the generic sector framework, so it had no actual
    basis to differentiate them and the verdict ended up restating the
    framework with the name substituted in.
    """
    factor_names = [m["factor"] for m in cfg["moat_factors"]]
    factors_str = "; ".join(f"{m['factor']}: {m['description']}" for m in cfg["moat_factors"])
    _desc = (description or "").strip()
    company_context = (
        f"Company-specific business description (use this to differentiate {company_name} from other "
        f"companies in the same sector — do not write a verdict that would apply equally to any peer in "
        f"this sector; if this description names a specific product line, platform, or business segment, "
        f"reference it):\n{_desc[:900]}\n\n"
        if _desc else
        "No company-specific business description is available. Write the verdict from the standard "
        "framework only, and do not invent specific products, platforms, or segments for this company.\n\n"
    )
    prompt = (
        f"{cfg['llm_context']}\n\n"
        f"Company: {company_name}\n\n"
        f"{company_context}"
        f"The standard moat framework for {cfg['display_name']} companies is:\n{factors_str}\n\n"
        "Respond with ONLY a JSON object, no markdown fences, no preamble, in this exact shape:\n"
        '{"ratings": {"<factor name>": "Strong"|"Moderate"|"Weak", ...for every factor above...}, '
        '"verdict": "2-3 sentence company-specific assessment of which factors are genuinely '
        'strong versus generic/weak for THIS company specifically, grounded in the business description '
        'above where one is provided — avoid a verdict generic enough to apply to any other company in '
        'the same sector."}'
    )
    try:
        raw = ask_llm(prompt)
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            cleaned = cleaned[cleaned.find("{"):cleaned.rfind("}") + 1]
        parsed = json.loads(cleaned)
        verdict = parsed.get("verdict")
        raw_ratings = parsed.get("ratings", {})
        # Defensive: only keep ratings for factors that actually exist in this
        # sector's framework, with a valid value — ignore anything else the
        # model hallucinated.
        ratings = {
            name: raw_ratings[name]
            for name in factor_names
            if raw_ratings.get(name) in ("Strong", "Moderate", "Weak")
        }
        return verdict, (ratings or None)
    except Exception:
        return None, None
