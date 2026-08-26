# modules/sectors/auto_ev.py
"""
Auto OEM & EV Manufacturers — Sector Module
"""

SECTOR_CONFIG: dict = {
    "slug": "auto_ev",
    "display_name": "Auto OEM & EV Manufacturers",

    "key_metrics": [
        {"id": "volume_growth",      "label": "Volume Growth (YoY)",     "unit": "%",  "yf_key": None,              "higher_is_better": True},
        {"id": "market_share",       "label": "Market Share",            "unit": "%",  "yf_key": None,              "higher_is_better": True},
        {"id": "capacity_util",      "label": "Capacity Utilisation",    "unit": "%",  "yf_key": None,              "higher_is_better": True},
        {"id": "ebitda_margin",      "label": "EBITDA Margin",           "unit": "%",  "yf_key": "ebitdaMargins",   "higher_is_better": True},
        {"id": "revenue_growth",     "label": "Revenue Growth (YoY)",    "unit": "%",  "yf_key": "revenueGrowth",   "higher_is_better": True},
        {"id": "dealer_network",     "label": "Dealer Network Size",     "unit": "#",  "yf_key": None,              "higher_is_better": True},
        # EV-specific
        {"id": "ev_volume_share",    "label": "EV Volume Share",         "unit": "%",  "yf_key": None,              "higher_is_better": True},
        {"id": "battery_strategy",   "label": "Battery Localisation",    "unit": "text","yf_key": None,             "higher_is_better": True},
        {"id": "de_ratio",           "label": "Debt/Equity",             "unit": "x",  "yf_key": "debtToEquity",   "higher_is_better": False},
    ],

    "scoring_rules": [
        {"metric": "ebitda_margin",  "op": ">", "threshold": 15.0, "points": 20, "max": 20},
        {"metric": "ebitda_margin",  "op": ">", "threshold": 10.0, "points": 12, "max": 20},
        {"metric": "ebitda_margin",  "op": ">", "threshold": 6.0,  "points": 6,  "max": 20},
        {"metric": "volume_growth",  "op": ">", "threshold": 15.0, "points": 20, "max": 20},
        {"metric": "volume_growth",  "op": ">", "threshold": 8.0,  "points": 12, "max": 20},
        {"metric": "volume_growth",  "op": ">", "threshold": 0.0,  "points": 5,  "max": 20},
        {"metric": "de_ratio",       "op": "<", "threshold": 0.5,  "points": 15, "max": 15},
        {"metric": "de_ratio",       "op": "<", "threshold": 1.0,  "points": 8,  "max": 15},
        {"metric": "capacity_util",  "op": ">", "threshold": 80.0, "points": 10, "max": 10},
        {"metric": "capacity_util",  "op": ">", "threshold": 65.0, "points": 5,  "max": 10},
    ],
    "score_max": 100,

    "risk_factors": [
        "Volume cyclicality tied to consumer sentiment and interest rate cycle",
        "Input cost volatility: steel, aluminium, semiconductors, battery metals (lithium, cobalt)",
        "EV disruption risk: incumbents face disruption from EV-native players",
        "Dealer channel conflict as OEMs launch direct-to-consumer EV sales",
        "Regulatory risk: CAFE norms, emission standards, EV mandate timelines",
        "Foreign competition if import duties rationalised under FTAs",
        "Product recall risk and quality issues denting brand equity",
    ],

    "moat_factors": [
        {"factor": "Brand",               "description": "Heritage brands (Maruti, Tata, Bajaj) carry decades of consumer trust across segments"},
        {"factor": "Distribution Network","description": "Pan-India dealer network is capital-intensive and slow to replicate — critical for Tier 3+ reach"},
        {"factor": "Manufacturing Scale", "description": "High volume amortises fixed costs — low-cost manufacturer advantage at scale"},
        {"factor": "Service Network",     "description": "Service touch-points build loyalty and sticky revenue; hard to match for new entrants"},
        {"factor": "R&D & Platform",      "description": "Shared platforms (e.g., common architecture across models) compress per-unit development cost"},
    ],

    "bull_case": [
        "India's vehicle penetration is 30 per 1000 vs 800+ in developed markets — structural demand runway",
        "Rural income recovery driving first-time 2W buyers and entry-level car replacement",
        "EV transition creating a volume upcycle as new model launches refresh demand",
        "PLI scheme incentives accelerating localisation and margin improvement",
        "Premiumisation: customers upgrading from 2W to 4W and entry to mid-segment",
    ],

    "bear_case": [
        "Volume decline in a high-interest-rate environment (EMI sensitivity in mass market)",
        "Margin compression as EV mix rises (EVs still dilutive at nascent scale)",
        "Battery supply chain disruption causing production cuts",
        "Quality issues or product launches that disappoint → market share loss",
        "Aggressive Chinese EV entry if import barriers fall",
    ],

    "red_flags": [
        {"condition": "volume_growth < -5",    "severity": "high",   "message": "Volumes declining > 5% — demand destruction or market share loss"},
        {"condition": "ebitda_margin < 6",     "severity": "high",   "message": "EBITDA margin < 6% — auto profitability under severe stress"},
        {"condition": "de_ratio > 1.5",        "severity": "medium", "message": "D/E > 1.5x — leverage elevated for a cyclical business"},
        {"condition": "capacity_util < 60",    "severity": "medium", "message": "Capacity utilisation < 60% — fixed costs being under-absorbed"},
        {"condition": "market_share < 0",      "severity": "medium", "message": "Market share declining — competitive position weakening"},
        {"condition": "ebitda_margin < 3",     "severity": "high",   "message": "EBITDA margin < 3% — near break-even, any volume dip causes losses"},
    ],

    "valuation": {
        "primary":   ["P/E Ratio", "EV/EBITDA"],
        "secondary": ["P/Sales", "EV/Unit Volume"],
        "notes": (
            "Auto OEMs are cyclical — P/E at cycle peak overstates valuation risk. "
            "Use mid-cycle normalised EV/EBITDA (typically 8–12x for established OEMs). "
            "EV-native players are priced on growth + TAM (EV/Sales) until they reach scale EBITDA."
        ),
        "bands": {
            "pe_ratio":    {"attractive": (0, 18), "fair": (18, 32), "expensive": (32, 999)},
            "ev_ebitda":   {"attractive": (0, 8),  "fair": (8, 14),  "expensive": (14, 999)},
        },
    },

    "llm_context": (
        "This is an AUTO OEM or EV MANUFACTURER. Focus on: volume growth and market share trends, "
        "EBITDA margins, capacity utilisation, dealer network strength, and EV transition strategy. "
        "Distinguish between ICE legacy risk and EV optionality. "
        "For EV players: assess battery localisation, charging ecosystem, and path to positive EBITDA. "
        "Valuation: use P/E and EV/EBITDA for traditional OEMs; EV/Sales for pure-play EV startups."
    ),
}
