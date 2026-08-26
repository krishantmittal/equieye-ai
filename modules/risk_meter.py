# modules/risk_meter.py
"""
Risk Meter — Core Integration Layer
=====================================
Public API consumed by app.py (signature preserved exactly):

    compute_risk(
        pe=None, de_raw=None, beta=None,
        free_cf=None, operating_cf=None,
        profit_margin_raw=None, sector="", industry="",
    ) -> dict

Returns:
    {
        "level": 1 | 2 | 3 | 4,        # 1=Low .. 4=High (drives the meter bar)
        "label": "Low Risk" | "Moderate Risk" | "Elevated Risk" | "High Risk",
        "icon": str, "color": str,
        "sector_base": "Low"|"Moderate"|"Elevated"|"High",  # sector's inherent risk baseline
        "sector_context": str,          # one-line sector risk framing
        "factors": list[str],           # top risk factors to display (sector + triggered flags)
    }

Combines two sector-aware signals into a single 1-4 risk level:
  1. Triggered sector-specific red flags (concrete, threshold-based)
  2. The sector's inherent baseline risk level (qualitative — e.g.
     renewable energy and metals & mining carry a structurally higher
     baseline than FMCG, independent of any one company's numbers)

All sector knowledge comes from modules/sectors/<slug>.py; this file
contains no sector-specific branching.
"""

from __future__ import annotations
from modules.sectors import get_sector_config
from modules.sectors.engine import eval_red_flags, severity_to_risk_points
from modules.sector_analysis import classify_sector

_LEVEL_META = {
    # These colours are rendered as TEXT, so they use the darker
# accessible steps rather than the vivid mark colours. The vivid
# equivalents measure 2.13:1 (green) and 1.95:1 (amber) on a light
# surface — well below the 4.5:1 WCAG body-text minimum.
    1: {"label": "Low Risk",      "icon": "🟢", "color": "#166534"},
    2: {"label": "Moderate Risk", "icon": "🟡", "color": "#92400E"},
    3: {"label": "Elevated Risk", "icon": "🟠", "color": "#FB923C"},
    4: {"label": "High Risk",     "icon": "🔴", "color": "#B91C1C"},
}

# Sectors whose business model carries structurally higher inherent risk
# (high leverage, regulatory binary outcomes, commodity cyclicality)
# versus structurally lower-risk, cash-generative, asset-light sectors.
_SECTOR_BASELINE = {
    "banking":           2, "nbfc":              3, "insurance":         2,
    "fintech":           3, "renewable_energy":  3, "power_utilities":   2,
    "auto_ev":           2, "it_services":        1, "pharma":            2,
    "fmcg":              1, "telecom":            3, "metals_mining":     3,
    "real_estate":       3, "generic":            2,
    # engineering_rd (split from it_services): deliberately Moderate, not
    # Low like it_services — same asset-light delivery model, but demand
    # is tied to cyclical auto/aerospace/industrial R&D capex rather than
    # diversified enterprise IT budgets, and client concentration tends to
    # run higher (see modules/sectors/engineering_rd.py risk_factors).
    "engineering_rd":    2,
    # pharma sub-sectors (split from the old flat "pharma": 2) — see each
    # module's risk_factors for the reasoning behind the differentiation.
    "pharma_generics":   2,   # Moderate — the old default pharma risk profile
    "pharma_api":        2,   # Moderate — commodity/China-competition risk, but cash-generative
    "pharma_cdmo":       2,   # Moderate — relationship-locked revenue, but client-concentration risk
    "pharma_specialty":  3,   # Elevated — binary clinical/regulatory pipeline risk
    "biotech":           3,   # Elevated — binary clinical + manufacturing-complexity risk
    "diagnostics":       1,   # Low — asset-light, high-margin, non-discretionary demand
    "hospitals":         2,   # Moderate — capex-heavy with long occupancy-ramp gestation, but stable demand
    # Capital goods sub-sectors (split from the old flat "capital_goods",
    # which had no explicit baseline entry and silently defaulted to
    # Moderate for every company in the bucket regardless of how different
    # an automation major's risk profile is from a PSU-dependent heavy
    # equipment manufacturer's) — see each module's risk_factors.
    "industrial_automation": 1,  # Low — technology/product business, cleaner balance sheets, less working-capital intensive
    "epc_engineering":       3,  # Elevated — working-capital intensive, execution/project-delay risk, cyclical capex exposure
    "electrical_equipment":  2,  # Moderate — brand/distribution business, but copper price and housing-cycle exposure
    "heavy_engineering":     3,  # Elevated — PSU/government order dependence, capacity-utilization risk, thermal-equipment technology transition risk
    "defense_aerospace":     2,  # Moderate — single-customer (MoD) concentration and execution-delay risk offset by strong order visibility, policy tailwind, and typically low leverage
}


def _build_metrics_dict(pe, de_raw, beta, profit_margin_raw,
                         ebitda_margin_pct=None, revenue_growth_pct=None,
                         profit_growth_pct=None, current_ratio=None,
                         extra_metrics=None) -> dict:
    metrics: dict = {}
    if pe is not None:
        metrics["pe_ratio"] = pe
    if de_raw is not None:
        # yfinance returns debtToEquity in percentage form for NSE stocks
        # (e.g. 3.29 meaning D/E of 0.0329x) — always divide by 100. The old
        # ">5" heuristic here assumed small values were already a plain ratio,
        # but that's wrong for genuinely very-low-leverage companies (ITC's
        # raw value ~3.29 is well under 5, so it was left unconverted and
        # misread as D/E=3.29x — triggering a false "unusual leverage" flag
        # for a company that's actually near debt-free at 0.03x).
        metrics["de_ratio"] = de_raw / 100
    if beta is not None:
        metrics["beta"] = beta
    if profit_margin_raw is not None:
        metrics["profit_margin"] = profit_margin_raw * 100  # yfinance profitMargins is always a decimal fraction
    # Previously missing entirely — every sector's red_flags rules keyed on
    # ebitda_margin/revenue_growth/rnd_pct_revenue/us_revenue_pct/etc. (see
    # modules/sectors/*.py) could never fire inside the Risk Meter, since
    # this dict never had those keys. Only pe_ratio/de_ratio/beta/profit_margin
    # -based rules could ever trigger. Mirrors red_flags.py's _build_metrics_dict
    # so the same rule set fires consistently in both places.
    if ebitda_margin_pct is not None:
        metrics["ebitda_margin"] = ebitda_margin_pct
    if revenue_growth_pct is not None:
        metrics["revenue_growth"] = revenue_growth_pct
    if profit_growth_pct is not None:
        metrics["profit_growth"] = profit_growth_pct
    if current_ratio is not None:
        metrics["current_ratio"] = current_ratio
    if extra_metrics:
        metrics.update({k: v for k, v in extra_metrics.items() if v is not None})
    return metrics


def compute_risk(
    pe=None, de_raw=None, beta=None,
    free_cf=None, operating_cf=None,
    profit_margin_raw=None, sector: str = "", industry: str = "",
    name: str = "", description: str = "",
    ebitda_margin_pct=None, revenue_growth_pct=None, profit_growth_pct=None,
    current_ratio=None, extra_metrics: dict | None = None,
) -> dict:
    """
    Computes a sector-aware risk level for a company. Call signature
    matches the legacy generic-metric implementation app.py already
    calls — sector intelligence is applied transparently underneath.
    New optional kwargs (ebitda_margin_pct, revenue_growth_pct,
    profit_growth_pct, current_ratio, extra_metrics) let callers pass the
    same fuller metric set already given to detect_flags(), so sector red
    flag rules keyed on those metrics can actually trigger here too.
    """
    slug = classify_sector(sector, industry, name, description)
    cfg = get_sector_config(slug)

    metrics = _build_metrics_dict(
        pe, de_raw, beta, profit_margin_raw,
        ebitda_margin_pct, revenue_growth_pct, profit_growth_pct,
        current_ratio, extra_metrics,
    )
    triggered = eval_red_flags(metrics, cfg.get("red_flags", []))

    flag_points = sum(severity_to_risk_points(f["severity"]) for f in triggered)

    # Cash-burn nudge — universal signal, layered on top of sector flags
    if free_cf is not None and operating_cf is not None and operating_cf < 0:
        flag_points += 15

    baseline_level = _SECTOR_BASELINE.get(slug, 2)
    flag_bump = 0 if flag_points < 12 else 1 if flag_points < 35 else 2
    # Convert flag_points (roughly 0-80+) into a 0-2 level bump on top of baseline.
    # flag_bump=0 (no flags triggered) must leave level == baseline_level — the
    # previous "+ flag_bump - 1" here meant a Moderate-baseline (2) sector with
    # zero triggered flags always computed to 2 + 0 - 1 = 1 (Low Risk), silently
    # understating every company's risk by one full level regardless of its
    # actual numbers, and contradicting the "Base: Moderate (sector)" label
    # shown right next to it.
    level = min(4, max(1, baseline_level + flag_bump))
    meta = _LEVEL_META[level]

    sector_base_label = _LEVEL_META[baseline_level]["label"].replace(" Risk", "")
    sector_context = _build_sector_context(cfg, baseline_level)

    factors = [f["message"] for f in triggered[:4]]
    # Pad with generic sector risk factors if few/no flags triggered, so
    # the panel always has useful context rather than looking empty.
    if len(factors) < 3:
        for rf in cfg.get("risk_factors", []):
            if rf not in factors:
                factors.append(rf)
            if len(factors) >= 5:
                break

    return {
        "level": level,
        "label": meta["label"],
        "icon": meta["icon"],
        "color": meta["color"],
        "sector_base": sector_base_label,
        "sector_context": sector_context,
        "factors": factors,
        "sector_slug": slug,
        "sector_display_name": cfg["display_name"],
    }


def _build_sector_context(cfg: dict, baseline_level: int) -> str:
    baseline_label = _LEVEL_META[baseline_level]["label"].replace(" Risk", "").lower()
    return (
        f"{cfg['display_name']} carries a {baseline_label} structural risk baseline. "
        f"Score is adjusted further based on company-specific red flags detected against "
        f"{cfg['display_name'].lower()}-specific thresholds."
    )
