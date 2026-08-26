# modules/sectors/telecom.py
"""
Telecom — Sector Module
"""

SECTOR_CONFIG: dict = {
    "slug": "telecom",
    "display_name": "Telecom",

    "key_metrics": [
        {"id": "arpu",              "label": "ARPU",                     "unit": "₹",  "yf_key": None,            "higher_is_better": True},
        {"id": "subscriber_growth", "label": "Subscriber Growth (YoY)",  "unit": "%",  "yf_key": None,            "higher_is_better": True},
        {"id": "ebitda_margin",     "label": "EBITDA Margin",            "unit": "%",  "yf_key": "ebitdaMargins","higher_is_better": True},
        {"id": "net_debt_ebitda",   "label": "Net Debt/EBITDA",          "unit": "x",  "yf_key": None,            "higher_is_better": False},
        {"id": "data_usage_gb",     "label": "Avg Data Usage/Sub (GB)",  "unit": "GB", "yf_key": None,            "higher_is_better": True},
        {"id": "capex_to_sales",    "label": "Capex/Sales",              "unit": "%",  "yf_key": None,            "higher_is_better": False},
        {"id": "market_share",      "label": "Revenue Market Share",     "unit": "%",  "yf_key": None,            "higher_is_better": True},
    ],

    "scoring_rules": [
        {"metric": "arpu",              "op": ">", "threshold": 200.0, "points": 20, "max": 20},
        {"metric": "arpu",              "op": ">", "threshold": 150.0, "points": 12, "max": 20},
        {"metric": "ebitda_margin",     "op": ">", "threshold": 45.0,  "points": 20, "max": 20},
        {"metric": "ebitda_margin",     "op": ">", "threshold": 35.0,  "points": 12, "max": 20},
        {"metric": "subscriber_growth", "op": ">", "threshold": 5.0,   "points": 15, "max": 15},
        {"metric": "net_debt_ebitda",   "op": "<", "threshold": 2.5,   "points": 20, "max": 20},
        {"metric": "net_debt_ebitda",   "op": "<", "threshold": 4.0,   "points": 10, "max": 20},
        {"metric": "market_share",      "op": ">", "threshold": 30.0,  "points": 15, "max": 15},
    ],
    "score_max": 100,

    "risk_factors": [
        "Extreme capital intensity — 5G rollout requires sustained heavy capex",
        "High financial leverage from spectrum payments and network capex (AGR dues legacy risk)",
        "Tariff war risk if a competitor pursues aggressive market-share-grab pricing",
        "Regulatory levies (license fee, spectrum usage charge, AGR definition disputes)",
        "Technology obsolescence risk requiring continuous network upgrades (4G→5G→6G)",
        "Duopoly/oligopoly dynamics mean a single player's distress impacts sector pricing discipline",
    ],

    "moat_factors": [
        {"factor": "Spectrum Holdings",     "description": "Owned spectrum across bands is a scarce, license-controlled asset with high entry barriers"},
        {"factor": "Network Scale",         "description": "Tower and fiber density built over years cannot be replicated quickly by new entrants"},
        {"factor": "Subscriber Base",       "description": "Large installed base with switching friction (number portability hassle, bundled services)"},
        {"factor": "Spectrum + Capital Access", "description": "Only well-capitalised players can fund the next-gen network upgrade cycle"},
        {"factor": "Enterprise/B2B Ecosystem", "description": "Diversification into enterprise data, cloud, and IoT reduces consumer ARPU dependency"},
    ],

    "bull_case": [
        "Tariff hikes continuing as the industry consolidates to 2-3 viable players, improving ARPU",
        "5G monetisation through enterprise use cases (private networks, IoT, fixed wireless access)",
        "Data consumption per subscriber growing structurally, supporting premiumisation",
        "Operating leverage as capex intensity moderates post initial 5G rollout phase",
        "Industry discipline returning after years of destructive price competition",
    ],

    "bear_case": [
        "Renewed tariff war if a weaker player fights for survival via aggressive pricing",
        "5G capex burden without commensurate ARPU uplift in the near term",
        "Regulatory dues (AGR-related) creating balance sheet overhang for legacy operators",
        "Slower-than-expected enterprise 5G monetisation",
        "Continued market share loss for the weakest of the 2-3 incumbent operators",
    ],

    "red_flags": [
        {"condition": "net_debt_ebitda > 4",   "severity": "high",   "message": "Net Debt/EBITDA > 4x — balance sheet stress, equity dilution risk"},
        {"condition": "ebitda_margin < 30",    "severity": "medium", "message": "EBITDA margin < 30% — weak operating leverage vs peers"},
        {"condition": "subscriber_growth < 0", "severity": "high",   "message": "Subscriber base shrinking — losing share in a consolidating market"},
        {"condition": "arpu < 130",            "severity": "medium", "message": "ARPU below sustainable reinvestment levels for network capex"},
        {"condition": "capex_to_sales > 35",   "severity": "medium", "message": "Capex/Sales > 35% — heavy investment cycle pressuring free cash flow"},
    ],

    "valuation": {
        "primary":   ["EV/EBITDA"],
        "secondary": ["EV/Subscriber", "P/E Ratio"],
        "notes": (
            "Telecom is high-capex and often loss-making at the PAT level due to depreciation/interest — "
            "value primarily on EV/EBITDA (typically 6-10x for Indian telcos). "
            "EV/Subscriber is useful cross-check for relative valuation between operators. "
            "P/E is often not meaningful for leveraged players posting net losses."
        ),
        "bands": {
            "ev_ebitda": {"attractive": (0, 6), "fair": (6, 9), "expensive": (9, 999)},
        },
    },

    "llm_context": (
        "This is a TELECOM company. Focus on: ARPU trends, subscriber growth/market share, EBITDA margin, "
        "and Net Debt/EBITDA (critical given the sector's capital intensity). "
        "Do NOT rely on P/E — many telcos report net losses due to heavy depreciation/interest; use EV/EBITDA. "
        "Tariff hike cycles and industry consolidation (2-3 player market) are the central thesis drivers. "
        "Flag balance sheet stress (AGR dues, spectrum payment obligations) prominently."
    ),
}
