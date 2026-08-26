# modules/sectors/generic.py
"""
Generic Fallback — Sector Module
Used when sector detection cannot confidently classify a company into one
of the specialised modules. Mirrors the legacy generic-metric approach
(P/E, ROE, D/E, Revenue Growth, Margins) so behaviour never regresses
for unmapped sectors.
"""

SECTOR_CONFIG: dict = {
    "slug": "generic",
    "display_name": "General / Unclassified",

    "key_metrics": [
        {"id": "revenue_growth", "label": "Revenue Growth (YoY)",  "unit": "%", "yf_key": "revenueGrowth",  "higher_is_better": True},
        {"id": "ebitda_margin",  "label": "EBITDA Margin",         "unit": "%", "yf_key": "ebitdaMargins",  "higher_is_better": True},
        {"id": "pe_ratio",       "label": "P/E Ratio",             "unit": "x", "yf_key": "trailingPE",     "higher_is_better": False},
        {"id": "roe",            "label": "Return on Equity",      "unit": "%", "yf_key": "returnOnEquity", "higher_is_better": True},
        {"id": "de_ratio",       "label": "Debt/Equity",           "unit": "x", "yf_key": "debtToEquity",   "higher_is_better": False},
        {"id": "current_ratio",  "label": "Current Ratio",         "unit": "x", "yf_key": "currentRatio",   "higher_is_better": True},
    ],

    "scoring_rules": [
        {"metric": "revenue_growth", "op": ">", "threshold": 15.0, "points": 20, "max": 20},
        {"metric": "revenue_growth", "op": ">", "threshold": 8.0,  "points": 12, "max": 20},
        {"metric": "ebitda_margin",  "op": ">", "threshold": 20.0, "points": 20, "max": 20},
        {"metric": "ebitda_margin",  "op": ">", "threshold": 12.0, "points": 12, "max": 20},
        {"metric": "roe",            "op": ">", "threshold": 18.0, "points": 20, "max": 20},
        {"metric": "roe",            "op": ">", "threshold": 12.0, "points": 12, "max": 20},
        {"metric": "de_ratio",       "op": "<", "threshold": 0.5,  "points": 20, "max": 20},
        {"metric": "de_ratio",       "op": "<", "threshold": 1.0,  "points": 10, "max": 20},
        {"metric": "current_ratio",  "op": ">", "threshold": 1.5,  "points": 20, "max": 20},
    ],
    "score_max": 100,

    "risk_factors": [
        "Generic market and competitive risk — sector-specific framework not available for this company",
        "Earnings cyclicality should be assessed against the company's specific industry conditions",
        "Leverage and liquidity risk should be benchmarked against direct industry peers",
    ],

    "moat_factors": [
        {"factor": "Brand & Market Position", "description": "Assess relative market share and brand strength within its specific industry"},
        {"factor": "Cost Structure",          "description": "Evaluate cost advantages versus direct competitors"},
        {"factor": "Capital Efficiency",      "description": "Consistent ROE/ROCE above cost of capital signals a durable competitive edge"},
    ],

    "bull_case": [
        "Revenue and earnings growth sustaining above sector/economy average",
        "Margin expansion from operating leverage or cost discipline",
        "Strong balance sheet providing flexibility for growth investments",
    ],

    "bear_case": [
        "Slowing growth relative to historical trend or peer set",
        "Margin compression from competitive or input cost pressure",
        "Elevated leverage limiting financial flexibility",
    ],

    "red_flags": [
        {"condition": "de_ratio > 1.5",      "severity": "high",   "message": "D/E > 1.5x — elevated leverage warrants scrutiny"},
        {"condition": "revenue_growth < 0",  "severity": "high",   "message": "Negative revenue growth — top-line contraction"},
        {"condition": "roe < 8",             "severity": "medium", "message": "ROE < 8% — capital efficiency below typical cost of equity"},
        {"condition": "current_ratio < 1.0", "severity": "medium", "message": "Current ratio < 1.0x — potential short-term liquidity stress"},
    ],

    "valuation": {
        "primary":   ["P/E Ratio", "ROE"],
        "secondary": ["EV/EBITDA", "P/B Ratio"],
        "notes": (
            "Sector-specific framework unavailable — using standard generic metrics "
            "(P/E, ROE, D/E, Revenue Growth, Margins). Compare against direct industry "
            "peers rather than broad market averages for a more meaningful read."
        ),
        "bands": {
            "pe_ratio": {"attractive": (0, 18), "fair": (18, 40), "expensive": (40, 999)},
        },
    },

    "llm_context": (
        "This company could not be confidently classified into a specific sector module. "
        "Apply general fundamental analysis using P/E, ROE, Debt/Equity, Revenue Growth, and Margins. "
        "Where possible, infer the likely industry from the business description and apply reasonable "
        "sector judgement even without a dedicated framework."
    ),
}
