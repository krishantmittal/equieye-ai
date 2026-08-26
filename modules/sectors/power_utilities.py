# modules/sectors/power_utilities.py
"""
Power Utilities — Sector Module (thermal/hydro generation, transmission, distribution)
"""

SECTOR_CONFIG: dict = {
    "slug": "power_utilities",
    "display_name": "Power Utilities",

    "key_metrics": [
        {"id": "plf",               "label": "Plant Load Factor",        "unit": "%",  "yf_key": None,            "higher_is_better": True},
        {"id": "installed_capacity_gw","label": "Installed Capacity (GW)","unit": "GW","yf_key": None,            "higher_is_better": True},
        {"id": "aggregate_tech_loss","label": "AT&C Loss (Discoms)",     "unit": "%",  "yf_key": None,            "higher_is_better": False},
        {"id": "regulated_equity_pct","label": "Regulated Equity Mix",   "unit": "%",  "yf_key": None,            "higher_is_better": True},
        {"id": "debt_equity",       "label": "Debt/Equity",              "unit": "x",  "yf_key": "debtToEquity", "higher_is_better": False},
        {"id": "fuel_security_pct", "label": "Fuel Security (Linked Coal)","unit":"%", "yf_key": None,            "higher_is_better": True},
        {"id": "roe",               "label": "Return on Equity",         "unit": "%",  "yf_key": "returnOnEquity","higher_is_better": True},
        {"id": "receivable_days",   "label": "Receivable Days (Discoms)", "unit": "days","yf_key": None,          "higher_is_better": False},
    ],

    "scoring_rules": [
        {"metric": "plf",                "op": ">", "threshold": 75.0, "points": 20, "max": 20},
        {"metric": "plf",                "op": ">", "threshold": 60.0, "points": 10, "max": 20},
        {"metric": "regulated_equity_pct","op": ">", "threshold": 70.0, "points": 20, "max": 20},
        {"metric": "regulated_equity_pct","op": ">", "threshold": 50.0, "points": 10, "max": 20},
        {"metric": "debt_equity",        "op": "<", "threshold": 1.5,  "points": 20, "max": 20},
        {"metric": "debt_equity",        "op": "<", "threshold": 2.5,  "points": 10, "max": 20},
        {"metric": "roe",                "op": ">", "threshold": 14.0, "points": 15, "max": 15},
        {"metric": "fuel_security_pct",  "op": ">", "threshold": 80.0, "points": 15, "max": 15},
        {"metric": "receivable_days",    "op": "<", "threshold": 60.0, "points": 10, "max": 10},
    ],
    "score_max": 100,

    "risk_factors": [
        "Discom payment delays — receivables can balloon and strain working capital",
        "Fuel availability/cost risk for thermal generation (coal linkage, import dependency)",
        "Regulatory risk: tariff-setting by state regulators can lag cost inflation",
        "High leverage from long-gestation, capital-intensive generation/transmission assets",
        "Stranded asset risk for thermal plants as renewable mandates expand",
        "PPA renewal risk once initial long-term contracts expire",
    ],

    "moat_factors": [
        {"factor": "Regulated Equity Model",  "description": "Cost-plus regulated-equity framework guarantees a fixed return on equity, providing earnings stability"},
        {"factor": "Long-term PPAs",          "description": "25-year power purchase agreements with state discoms provide multi-decade revenue visibility"},
        {"factor": "Scale & Diversification", "description": "Diversified generation mix (thermal+hydro+renewable) smooths earnings across fuel cycles"},
        {"factor": "Transmission Monopoly",   "description": "Transmission assets often operate as regulated monopolies in their service territory"},
        {"factor": "Execution Track Record",  "description": "Reliable project execution at scale is rare and commands regulatory/government trust for new projects"},
    ],

    "bull_case": [
        "India's power demand growing at 6-8% CAGR driven by industrialisation and electrification",
        "Regulated-equity-model utilities offer bond-like, predictable ROE-linked earnings",
        "Transmission and distribution capex cycle from grid modernisation and renewable integration",
        "Discom reforms (UDAY-successor schemes) gradually improving payment discipline",
        "Hybrid generation portfolios (thermal + renewable) capturing both baseload and growth demand",
    ],

    "bear_case": [
        "Discom receivables ballooning, straining generator working capital and cash flow",
        "Coal supply disruptions or cost spikes squeezing thermal generation margins",
        "Regulatory tariff orders lagging cost increases, compressing realised returns",
        "Stranded thermal asset risk as the energy transition accelerates",
        "High leverage limiting flexibility to fund growth capex without equity dilution",
    ],

    "red_flags": [
        {"condition": "receivable_days > 120", "severity": "high",   "message": "Receivable days > 120 — severe discom payment delays straining cash flow"},
        {"condition": "debt_equity > 2.5",     "severity": "high",   "message": "D/E > 2.5x — high leverage for a capital-intensive regulated business"},
        {"condition": "plf < 55",              "severity": "medium", "message": "PLF < 55% — generation asset under-utilised, fixed costs poorly absorbed"},
        {"condition": "fuel_security_pct < 60","severity": "medium", "message": "Fuel security < 60% — exposed to spot coal/import price volatility"},
        {"condition": "regulated_equity_pct < 40","severity": "low", "message": "Low regulated-equity mix — earnings less predictable, more merchant/market exposure"},
    ],

    "valuation": {
        "primary":   ["EV/EBITDA", "P/B Ratio"],
        "secondary": ["P/E Ratio", "Regulated RoE Multiple"],
        "notes": (
            "Regulated utilities are valued like infrastructure/bond proxies — P/B anchored to allowed "
            "regulatory ROE (typically 1.5-2.5x book for a stable ~15% RoE business). "
            "EV/EBITDA useful for comparing generation assets across fuel types. "
            "Discom receivable trends are as important as the income statement for true cash quality."
        ),
        "bands": {
            "ev_ebitda": {"attractive": (0, 7), "fair": (7, 11), "expensive": (11, 999)},
        },
    },

    "llm_context": (
        "This is a POWER UTILITIES company (generation/transmission/distribution). Focus on: PLF, "
        "regulated equity mix, Debt/Equity, fuel security, and discom receivable days. "
        "Distinguish regulated-equity-model earnings (stable, bond-like) from merchant power exposure "
        "(volatile, market-priced). Discom payment delays are a critical, sector-specific cash-flow risk. "
        "Use EV/EBITDA and P/B (anchored to regulated ROE) rather than generic P/E."
    ),
}
