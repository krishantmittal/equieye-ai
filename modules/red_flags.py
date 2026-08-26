# modules/red_flags.py
"""
Red Flag Detection — Core Integration Layer
=============================================
Public API consumed by app.py (signature preserved exactly):

    detect_flags(
        pe=None, roe_raw=None, de_raw=None, profit_margin_raw=None,
        free_cf=None, operating_cf=None, rev=None,
        revenue_growth_pct=None, profit_growth_pct=None,
        ebitda_margin_pct=None, sector="", industry="",
    ) -> list[dict]

Each returned flag:
    {"title": str, "detail": str, "severity": "high"|"medium"|"low",
     "color": "#EF4444"|"#F59E0B"|"#FCD34D", "icon": "🔴"|"🟡"|"⚠"}

Each sector module declares its own red_flags rule list as plain data
(see modules/sectors/<slug>.py). This file classifies the company,
maps legacy positional args onto that sector's metric vocabulary, and
evaluates everything through the shared rule engine — no sector-
specific branching lives here, and a generic cash-flow check (negative
FCF vs OCF) is layered on top for any sector since that signal is
universal.
"""

from __future__ import annotations
from modules.sectors import get_sector_config
from modules.sectors.engine import eval_red_flags
from modules.sector_analysis import classify_sector

_SEVERITY_STYLE = {
    "high":   {"color": "#EF4444", "icon": "🔴"},
    "medium": {"color": "#F59E0B", "icon": "🟡"},
    "low":    {"color": "#FCD34D", "icon": "⚠"},
}


def _build_metrics_dict(pe, roe_raw, de_raw, profit_margin_raw,
                         revenue_growth_pct, profit_growth_pct,
                         ebitda_margin_pct, current_ratio=None,
                         extra_metrics=None) -> dict:
    metrics: dict = {}
    if pe is not None:
        metrics["pe_ratio"] = pe
    if roe_raw is not None:
        metrics["roe"] = roe_raw * 100  # yfinance returnOnEquity is always a decimal fraction
    if de_raw is not None:
        # yfinance returns debtToEquity in percentage form for NSE stocks —
        # always divide by 100 (see risk_meter.py for why the old ">5"
        # heuristic was wrong for very-low-leverage companies).
        metrics["de_ratio"] = de_raw / 100
    if profit_margin_raw is not None:
        metrics["profit_margin"] = profit_margin_raw * 100  # yfinance profitMargins is always a decimal fraction
    if ebitda_margin_pct is not None:
        metrics["ebitda_margin"] = ebitda_margin_pct
    if revenue_growth_pct is not None:
        metrics["revenue_growth"] = revenue_growth_pct
    if profit_growth_pct is not None:
        metrics["profit_growth"] = profit_growth_pct
    if current_ratio is not None:
        metrics["current_ratio"] = current_ratio
    if extra_metrics:
        # Generic passthrough for metrics not worth a dedicated named
        # param (mirrors compute_health_score's extra_metrics design) —
        # e.g. net_debt_ebitda, interest_coverage, receivable_days,
        # inventory_months, derived upstream from balance sheet/financials
        # dataframes rather than the yfinance `info` dict.
        metrics.update({k: v for k, v in extra_metrics.items() if v is not None})
    return metrics


def detect_flags(
    pe=None, roe_raw=None, de_raw=None, profit_margin_raw=None,
    free_cf=None, operating_cf=None, rev=None,
    revenue_growth_pct=None, profit_growth_pct=None,
    ebitda_margin_pct=None, sector: str = "", industry: str = "",
    name: str = "", description: str = "", current_ratio=None,
    extra_metrics: dict | None = None,
) -> list[dict]:
    """
    Detects sector-specific + universal red flags for a company. Call
    signature matches the legacy generic-metric implementation app.py
    already calls — sector intelligence is applied transparently
    underneath via modules/sectors/<slug>.py.
    """
    slug = classify_sector(sector, industry, name, description)
    cfg = get_sector_config(slug)

    metrics = _build_metrics_dict(
        pe, roe_raw, de_raw, profit_margin_raw,
        revenue_growth_pct, profit_growth_pct, ebitda_margin_pct,
        current_ratio, extra_metrics,
    )

    sector_flags = eval_red_flags(metrics, cfg.get("red_flags", []))

    flags = [
        {
            "title": f["message"].split("—")[0].strip() if "—" in f["message"] else f["message"],
            "detail": f["message"],
            "severity": f["severity"],
            **_SEVERITY_STYLE.get(f["severity"], _SEVERITY_STYLE["medium"]),
        }
        for f in sector_flags
    ]

    # Universal cash-flow quality flag, applicable regardless of sector —
    # a company reporting profit but burning cash is a red flag everywhere.
    if free_cf is not None and operating_cf is not None:
        if free_cf < 0 and operating_cf > 0:
            flags.append({
                "title": "Negative Free Cash Flow",
                "detail": "Operating cash flow is positive but heavy capex is consuming all of it — "
                           "free cash flow is negative, limiting reinvestment flexibility.",
                "severity": "medium",
                **_SEVERITY_STYLE["medium"],
            })
        elif operating_cf < 0:
            flags.append({
                "title": "Negative Operating Cash Flow",
                "detail": "Core operations are not generating cash — a structural concern "
                           "regardless of reported accounting profit.",
                "severity": "high",
                **_SEVERITY_STYLE["high"],
            })

    # Sort highest severity first
    sev_order = {"high": 0, "medium": 1, "low": 2}
    flags.sort(key=lambda f: sev_order.get(f["severity"], 3))
    return flags
