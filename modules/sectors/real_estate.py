# modules/sectors/real_estate.py
"""
Real Estate — Sector Module
"""

SECTOR_CONFIG: dict = {
    "slug": "real_estate",
    "display_name": "Real Estate",

    "key_metrics": [
        {"id": "presales_growth",   "label": "Pre-Sales Growth (YoY)",   "unit": "%",  "yf_key": None,            "higher_is_better": True},
        {"id": "collections_growth","label": "Collections Growth",       "unit": "%",  "yf_key": None,            "higher_is_better": True},
        {"id": "net_debt_equity",   "label": "Net Debt/Equity",          "unit": "x",  "yf_key": "debtToEquity", "higher_is_better": False},
        {"id": "inventory_months",  "label": "Unsold Inventory (Months)","unit": "mo", "yf_key": None,            "higher_is_better": False},
        {"id": "land_bank_years",   "label": "Land Bank (Years of Sales)","unit": "yr","yf_key": None,            "higher_is_better": True},
        {"id": "ebitda_margin",     "label": "EBITDA Margin",            "unit": "%",  "yf_key": "ebitdaMargins","higher_is_better": True},
        {"id": "roe",               "label": "Return on Equity",         "unit": "%",  "yf_key": "returnOnEquity","higher_is_better": True},
    ],

    "scoring_rules": [
        {"metric": "presales_growth",   "op": ">", "threshold": 25.0, "points": 20, "max": 20},
        {"metric": "presales_growth",   "op": ">", "threshold": 12.0, "points": 12, "max": 20},
        {"metric": "net_debt_equity",   "op": "<", "threshold": 0.3,  "points": 20, "max": 20},
        {"metric": "net_debt_equity",   "op": "<", "threshold": 0.6,  "points": 10, "max": 20},
        {"metric": "ebitda_margin",     "op": ">", "threshold": 28.0, "points": 15, "max": 15},
        {"metric": "ebitda_margin",     "op": ">", "threshold": 18.0, "points": 8,  "max": 15},
        {"metric": "inventory_months",  "op": "<", "threshold": 24.0, "points": 15, "max": 15},
        {"metric": "roe",               "op": ">", "threshold": 18.0, "points": 15, "max": 15},
        {"metric": "land_bank_years",   "op": ">", "threshold": 5.0,  "points": 15, "max": 15},
    ],
    "score_max": 100,

    "risk_factors": [
        "Interest rate sensitivity — home loan rates directly impact buyer affordability and demand",
        "Regulatory/RERA compliance risk and project execution delays",
        "High financial leverage from land acquisition and construction financing",
        "Cyclicality: residential real estate goes through multi-year up/down cycles",
        "Approval delays (environmental, municipal) can stall launches and inflate costs",
        "Inventory overhang risk if pre-sales slow while construction continues",
    ],

    "moat_factors": [
        {"factor": "Brand & Trust",          "description": "RERA-era consolidation favours trusted, delivery-track-record developers"},
        {"factor": "Land Bank",              "description": "Strategically located, low-cost land bank acquired early provides a structural cost edge"},
        {"factor": "Execution Track Record", "description": "Consistent on-time delivery builds buyer trust and commands a pricing premium"},
        {"factor": "Balance Sheet Strength", "description": "Low leverage allows aggressive land acquisition during downcycles when competitors are distressed"},
        {"factor": "Asset-Light JDA Model",  "description": "Joint Development Agreements reduce capital intensity while preserving development upside"},
    ],

    "bull_case": [
        "Multi-year residential upcycle driven by rising affordability and pent-up post-pandemic demand",
        "Consolidation favouring branded, RERA-compliant developers over unorganised players",
        "Office/commercial REIT demand recovering as hybrid work stabilises",
        "Pre-sales momentum + low leverage translating into strong free cash flow generation",
        "Premiumisation: rising share of luxury/premium housing improving realisation and margins",
    ],

    "bear_case": [
        "Rising interest rates choking affordability and slowing pre-sales momentum",
        "Inventory overhang building up if launches outpace absorption",
        "Execution delays causing buyer trust erosion and RERA penalties",
        "High leverage amplifying distress risk in a slowing pre-sales environment",
        "Land/approval cost inflation compressing project-level IRRs",
    ],

    "red_flags": [
        {"condition": "net_debt_equity > 1.0", "severity": "high",   "message": "Net Debt/Equity > 1x — high leverage in a cyclical, capital-intensive business"},
        {"condition": "inventory_months > 36", "severity": "medium", "message": "Unsold inventory > 36 months of sales — demand absorption concerns"},
        {"condition": "presales_growth < 0",   "severity": "high",   "message": "Pre-sales declining — demand momentum has reversed"},
        {"condition": "collections_growth < 0","severity": "medium", "message": "Collections declining — cash flow visibility weakening despite booked sales"},
        {"condition": "land_bank_years < 2",   "severity": "low",    "message": "Land bank < 2 years of sales — growth pipeline visibility is short"},
    ],

    "valuation": {
        "primary":   ["P/NAV (Price to Net Asset Value)"],
        "secondary": ["P/E Ratio", "EV/EBITDA"],
        "notes": (
            "Real estate developers are best valued on P/NAV — sum of discounted project cash flows "
            "against land bank, less net debt. Quality developers with strong brands trade closer to "
            "1.0-1.5x NAV; weaker/leveraged players trade at a discount to NAV. "
            "P/E is volatile due to lumpy project-completion-based revenue recognition."
        ),
        "bands": {
            "p_nav": {"attractive": (0, 0.8), "fair": (0.8, 1.2), "expensive": (1.2, 99)},
            # P/NAV is the textbook-correct metric per the notes above, but
            # yfinance never supplies NAV/RNAV data, so that band was
            # silently dead — every developer fell through to a raw P/E
            # score using get_pe_bands(), which for "real_estate" happened
            # to work by coincidence (yfinance's raw sector string "Real
            # Estate" matches a key in the unrelated generic industry-band
            # table) rather than through an intentional sector-specific
            # band. Making it explicit here, plus adding EV/EBITDA since
            # it's the secondary metric these notes already call out and
            # is more meaningful than P/E given lumpy project-completion
            # accounting.
            # NOTE: both are reasonable approximations for Indian listed
            # developers, not sourced from a verified comps dataset —
            # sanity-check if precision matters here.
            "pe_ratio":   {"attractive": (0, 20), "fair": (20, 35), "expensive": (35, 999)},
            "ev_ebitda":  {"attractive": (0, 12), "fair": (12, 20), "expensive": (20, 999)},
        },
    },

    "llm_context": (
        "This is a REAL ESTATE company. Focus on: pre-sales growth, collections growth, Net Debt/Equity, "
        "unsold inventory months, land bank visibility, and execution track record. "
        "Do NOT apply P/E as the primary lens — use P/NAV (Net Asset Value) given lumpy project-based "
        "revenue recognition. Leverage and inventory overhang are the key risk signals. "
        "Distinguish pre-sales (booking momentum) from collections (actual cash realisation) — "
        "a gap between the two is a red flag worth surfacing."
    ),
}
