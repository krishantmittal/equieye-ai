# modules/sectors/consumer_durables.py
"""
Consumer Durables / Electronics — Sector Module
"""

SECTOR_CONFIG: dict = {
    "slug": "consumer_durables",
    "display_name": "Consumer Durables",

    "key_metrics": [
        {"id": "distribution_reach", "label": "Retail Distribution Reach", "unit": "outlets", "yf_key": None, "higher_is_better": True},
        {"id": "premiumisation_mix", "label": "Premium Product Mix",       "unit": "%", "yf_key": None, "higher_is_better": True},
        {"id": "inventory_days",     "label": "Inventory Days",            "unit": "days", "yf_key": None, "higher_is_better": False},
        {"id": "ebitda_margin",      "label": "EBITDA Margin",             "unit": "%", "yf_key": "ebitdaMargins", "higher_is_better": True},
        {"id": "revenue_growth",     "label": "Revenue Growth",            "unit": "%", "yf_key": None, "higher_is_better": True},
    ],

    "risk_factors": [
        "Discretionary spending exposure — demand highly sensitive to consumer sentiment/income cycles",
        "Seasonal demand concentration (summer for ACs/coolers, festive season for most categories)",
        "Input cost volatility (copper, steel, plastics) affecting margins",
        "Intense competition from both organised brands and Chinese/unbranded imports",
        "Rising online/quick-commerce channel disrupting traditional retail distribution economics",
        "Working capital intensity from dealer inventory financing and seasonal stocking",
    ],

    "moat_factors": [
        {"factor": "Brand",                 "description": "Trusted brand commands pricing power and repeat purchase in big-ticket categories"},
        {"factor": "Distribution Reach",    "description": "Deep retail/service network is expensive and slow for new entrants to replicate"},
        {"factor": "After-Sales Service",   "description": "Service network quality drives brand loyalty for durable goods with long usage life"},
        {"factor": "Product Innovation",    "description": "Regular new launches defend share against low-cost/import competition"},
        {"factor": "Manufacturing Scale",   "description": "Scale lowers unit costs and supports competitive pricing against smaller players"},
    ],

    "bull_case": [
        "Rising per-capita income driving premiumisation and category penetration",
        "Low penetration versus developed markets implying long growth runway",
        "Government PLI incentives supporting domestic manufacturing scale-up",
        "Summer/festive demand cycles providing predictable seasonal tailwinds",
        "Expanding rural distribution reach opening new demand pockets",
    ],

    "bear_case": [
        "Weak discretionary spending during economic slowdowns hurting volumes",
        "Input cost inflation (commodities) compressing margins",
        "Intensifying competition from low-cost/import players fragmenting market share",
        "Unseasonal weather disrupting category-specific demand (e.g. weak summer hurting ACs)",
        "Channel disruption from quick-commerce reshaping traditional dealer economics",
    ],

    "red_flags": [
        {"condition": "de_ratio > 1.0",     "severity": "medium", "message": "D/E > 1.0x — elevated leverage for a discretionary-demand business"},
        {"condition": "ebitda_margin < 8",  "severity": "medium", "message": "EBITDA margin < 8% — thin margins for a branded consumer durables business"},
    ],

    "valuation": {
        "primary":   ["P/E"],
        "secondary": ["EV/EBITDA"],
        "notes": (
            "Consumer durables companies are typically valued on P/E, with a premium for strong brands and "
            "wide distribution reach relative to smaller, regional, or private-label competitors."
        ),
        "bands": {
            "pe_ratio": {"attractive": (0, 25), "fair": (25, 45), "expensive": (45, 999)},
        },
    },

    "llm_context": (
        "This is a CONSUMER DURABLES / ELECTRONICS company. Focus on: brand strength, distribution/service "
        "network reach, seasonality of demand, premiumisation trend, and exposure to input cost and import "
        "competition. Distinguish discretionary big-ticket categories (ACs, refrigerators) from smaller "
        "appliances, since demand elasticity and seasonality differ significantly between them."
    ),
}
