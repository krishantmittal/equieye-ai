# modules/sectors/it_services.py
"""
IT Services & SaaS — Sector Module
"""

SECTOR_CONFIG: dict = {
    "slug": "it_services",
    "display_name": "IT Services & SaaS",

    "key_metrics": [
        {"id": "revenue_growth",    "label": "Revenue Growth (YoY)",   "unit": "%",  "yf_key": "revenueGrowth",  "higher_is_better": True},
        {"id": "usd_rev_growth",    "label": "USD Revenue Growth",     "unit": "%",  "yf_key": None,             "higher_is_better": True},
        {"id": "ebitda_margin",     "label": "EBITDA Margin",          "unit": "%",  "yf_key": "ebitdaMargins",  "higher_is_better": True},
        {"id": "attrition_rate",    "label": "Attrition Rate (TTM)",   "unit": "%",  "yf_key": None,             "higher_is_better": False},
        {"id": "utilisation_rate",  "label": "Utilisation Rate",       "unit": "%",  "yf_key": None,             "higher_is_better": True},
        {"id": "deal_wins_tcv",     "label": "Deal Win TCV",           "unit": "$B", "yf_key": None,             "higher_is_better": True},
        {"id": "client_concentration","label": "Top-10 Client Revenue","unit": "%",  "yf_key": None,             "higher_is_better": False},
        {"id": "roe",               "label": "Return on Equity",       "unit": "%",  "yf_key": "returnOnEquity", "higher_is_better": True},
        {"id": "fcf_conversion",    "label": "FCF Conversion",         "unit": "%",  "yf_key": None,             "higher_is_better": True},
    ],

    "scoring_rules": [
        {"metric": "revenue_growth",   "op": ">", "threshold": 15.0, "points": 20, "max": 20},
        {"metric": "revenue_growth",   "op": ">", "threshold": 8.0,  "points": 12, "max": 20},
        {"metric": "revenue_growth",   "op": ">", "threshold": 3.0,  "points": 5,  "max": 20},
        {"metric": "ebitda_margin",    "op": ">", "threshold": 25.0, "points": 20, "max": 20},
        {"metric": "ebitda_margin",    "op": ">", "threshold": 18.0, "points": 12, "max": 20},
        {"metric": "ebitda_margin",    "op": ">", "threshold": 12.0, "points": 6,  "max": 20},
        {"metric": "attrition_rate",   "op": "<", "threshold": 12.0, "points": 20, "max": 20},
        {"metric": "attrition_rate",   "op": "<", "threshold": 18.0, "points": 10, "max": 20},
        {"metric": "utilisation_rate", "op": ">", "threshold": 82.0, "points": 10, "max": 10},
        {"metric": "utilisation_rate", "op": ">", "threshold": 75.0, "points": 5,  "max": 10},
        {"metric": "roe",              "op": ">", "threshold": 25.0, "points": 10, "max": 10},
        {"metric": "roe",              "op": ">", "threshold": 18.0, "points": 6,  "max": 10},
    ],
    "score_max": 100,

    "risk_factors": [
        "Demand slowdown from US/Europe enterprise IT budget cuts (BFSI, telecom are key verticals)",
        "Margin headwinds from wage inflation, visa costs, and rupee appreciation",
        "High attrition increasing recruitment and training costs",
        "AI / GenAI disrupting traditional T&M billing models — threat to headcount-driven revenue",
        "Client concentration risk: loss of a top-5 client is a material earnings risk",
        "Pricing pressure as clients commoditise legacy services",
        "Deal ramp delays as enterprise decision cycles lengthen in uncertainty",
    ],

    "moat_factors": [
        {"factor": "Client Relationships",       "description": "Multi-decade relationships with Fortune 500 clients create high switching costs and reference value"},
        {"factor": "Global Delivery Model",      "description": "Offshore cost arbitrage + onshore delivery — hard to replicate for non-Indian competitors"},
        {"factor": "Talent Pool",                "description": "India's engineering talent depth at scale is a structural cost advantage"},
        {"factor": "Domain Expertise",           "description": "Sector-specific IP in BFSI, healthcare, and manufacturing commands premium pricing"},
        {"factor": "Brand & Certifications",     "description": "CMM Level 5, ISO, and sector compliance certifications are procurement pre-qualifiers"},
    ],

    "bull_case": [
        "Cloud migration, AI adoption, and digital transformation are secular multi-year spend drivers",
        "GenAI enablement: IT majors building AI practices generate higher-margin consulting revenue",
        "Pricing power recovery as talent supply normalises post-pandemic hiring frenzy",
        "Large deal momentum: mega-deals > $500M TCV have long revenue tails",
        "Currency depreciation tailwind if rupee weakens vs USD",
    ],

    "bear_case": [
        "US/EU recession leading to discretionary IT spend cuts",
        "AI replacing coding, testing, and documentation — reducing billable headcount",
        "Attrition spike on macro recovery — rehiring at higher wages compresses margins",
        "Visa restrictions tightening onsite delivery capability",
        "Market share loss to nimble product-engineering boutiques",
    ],

    "red_flags": [
        {"condition": "attrition_rate > 20",   "severity": "high",   "message": "Attrition > 20% — talent flight creates delivery risk and cost pressure"},
        {"condition": "revenue_growth < 2",    "severity": "high",   "message": "Revenue growth < 2% — near-stagnation, demand headwinds severe"},
        {"condition": "ebitda_margin < 12",    "severity": "high",   "message": "EBITDA margin < 12% — margin compression below sustainable levels"},
        {"condition": "client_concentration > 30", "severity": "medium", "message": "Top-10 clients > 30% revenue — dangerous concentration risk"},
        {"condition": "utilisation_rate < 70", "severity": "medium", "message": "Utilisation < 70% — bench cost being absorbed, dragging margins"},
        {"condition": "usd_rev_growth < 0",    "severity": "high",   "message": "Negative USD revenue growth — real demand contraction underway"},
    ],

    "valuation": {
        "primary":   ["P/E Ratio", "EV/EBITDA"],
        "secondary": ["EV/Sales", "P/FCF"],
        "notes": (
            "IT services trade on P/E (premium for cash-generative, asset-light model). "
            "Large-caps (TCS, Infosys) historically trade at 22–30x P/E. "
            "Mid-caps with faster growth deserve a premium; stagnating companies de-rate to 14–18x. "
            "SaaS businesses use EV/ARR or EV/Sales if pre-profit."
        ),
        "bands": {
            "pe_ratio":  {"attractive": (0, 22), "fair": (22, 38), "expensive": (38, 999)},
            "ev_ebitda": {"attractive": (0, 14), "fair": (14, 22), "expensive": (22, 999)},
        },
    },

    "llm_context": (
        "This is an IT SERVICES or SaaS company. Focus on: USD revenue growth, EBITDA margin, "
        "attrition rate, utilisation, deal wins, and client concentration. "
        "Do NOT apply D/E or NPA analysis — IT is asset-light with near-zero debt. "
        "Key question: is the company gaining or losing market share in its verticals? "
        "Assess GenAI strategy and its impact on future billing models."
    ),
}
