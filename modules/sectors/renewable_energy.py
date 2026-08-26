# modules/sectors/renewable_energy.py
"""
Renewable Energy — Sector Module
"""

SECTOR_CONFIG: dict = {
    "slug": "renewable_energy",
    "display_name": "Renewable Energy",

    "key_metrics": [
        {"id": "installed_gw",      "label": "Installed Capacity (GW)",  "unit": "GW", "yf_key": None,            "higher_is_better": True},
        {"id": "pipeline_gw",       "label": "Capacity Pipeline (GW)",   "unit": "GW", "yf_key": None,            "higher_is_better": True},
        {"id": "plf",               "label": "Plant Load Factor",         "unit": "%",  "yf_key": None,            "higher_is_better": True},
        {"id": "debt_ebitda",       "label": "Debt/EBITDA",               "unit": "x",  "yf_key": None,            "higher_is_better": False},
        {"id": "interest_coverage", "label": "Interest Coverage",         "unit": "x",  "yf_key": None,            "higher_is_better": True},
        {"id": "ppa_revenue_pct",   "label": "PPA-backed Revenue (%)",    "unit": "%",  "yf_key": None,            "higher_is_better": True},
        {"id": "ocf",               "label": "Operating Cash Flow",       "unit": "₹Cr","yf_key": "operatingCashflow","higher_is_better": True},
        {"id": "de_ratio",          "label": "Debt/Equity",               "unit": "x",  "yf_key": "debtToEquity",  "higher_is_better": False},
        {"id": "ebitda_margin",     "label": "EBITDA Margin",             "unit": "%",  "yf_key": "ebitdaMargins", "higher_is_better": True},
    ],

    "scoring_rules": [
        {"metric": "ebitda_margin",    "op": ">", "threshold": 60.0, "points": 15, "max": 15},
        {"metric": "ebitda_margin",    "op": ">", "threshold": 45.0, "points": 8,  "max": 15},
        {"metric": "interest_coverage","op": ">", "threshold": 3.0,  "points": 20, "max": 20},
        {"metric": "interest_coverage","op": ">", "threshold": 1.5,  "points": 10, "max": 20},
        {"metric": "de_ratio",         "op": "<", "threshold": 2.0,  "points": 20, "max": 20},
        {"metric": "de_ratio",         "op": "<", "threshold": 3.0,  "points": 10, "max": 20},
        {"metric": "ppa_revenue_pct",  "op": ">", "threshold": 80.0, "points": 15, "max": 15},
        {"metric": "ppa_revenue_pct",  "op": ">", "threshold": 60.0, "points": 8,  "max": 15},
        {"metric": "plf",              "op": ">", "threshold": 28.0, "points": 10, "max": 10},  # Solar PLF >28% is excellent
        {"metric": "plf",              "op": ">", "threshold": 22.0, "points": 5,  "max": 10},
    ],
    "score_max": 100,

    "risk_factors": [
        "High financial leverage (Debt/EBITDA > 5x) creates refinancing risk",
        "Execution risk at scale — land acquisition, grid connectivity, regulatory approvals",
        "Curtailment risk: discoms refusing to off-take contracted power",
        "Currency risk on USD-denominated bonds used for project financing",
        "Weather/resource risk affecting actual vs. projected generation",
        "Rising interest rates compress IRR on new project bids",
        "Counterparty risk: weak discom balance sheets delaying payments",
    ],

    "moat_factors": [
        {"factor": "Scale & Land Bank",      "description": "Large operational portfolio provides cost of capital advantage and learning-curve benefits"},
        {"factor": "Execution Capability",   "description": "Track record of on-time, on-budget commissioning is rare and differentiating"},
        {"factor": "Long-term PPAs",         "description": "25-year PPAs with government offtakers provide near-utility revenue visibility"},
        {"factor": "Access to Capital",      "description": "Investment-grade credit rating unlocks cheaper project finance — huge advantage at scale"},
        {"factor": "Diversified Portfolio",  "description": "Mix of solar + wind + hydro reduces resource risk and improves generation predictability"},
    ],

    "bull_case": [
        "India's 500 GW renewable target by 2030 requires ₹25 lakh crore of investment — massive tailwind",
        "Falling solar/wind LCOE makes renewables the cheapest source of new power generation",
        "Green hydrogen opportunity: captive renewable generation + electrolyser strategy",
        "Corporate PPAs growing as ESG mandates push private sector to procure green power",
        "Re-rating potential as cash flows become more visible and leverage decreases",
    ],

    "bear_case": [
        "Persistently weak discom balance sheets leading to payment delays",
        "Grid infrastructure bottlenecks limiting evacuation of generated power",
        "Aggressive auction bidding with unsustainably low tariffs compressing IRR",
        "Refinancing risk if global interest rates remain elevated",
        "Land acquisition disputes delaying project commissioning",
    ],

    "red_flags": [
        {"condition": "de_ratio > 3",          "severity": "high",   "message": "D/E > 3x — leverage is dangerously high for a capital-intensive business"},
        {"condition": "interest_coverage < 1.5","severity": "high",   "message": "Interest coverage < 1.5x — debt service under stress"},
        {"condition": "debt_ebitda > 7",        "severity": "high",   "message": "Debt/EBITDA > 7x — unsustainable leverage ratio"},
        {"condition": "ppa_revenue_pct < 50",   "severity": "medium", "message": "< 50% PPA-backed revenue — merchant power exposure is high"},
        {"condition": "ocf < 0",                "severity": "high",   "message": "Negative operating cash flow — operations not self-funding"},
        {"condition": "plf < 18",               "severity": "medium", "message": "PLF < 18% — below-average generation efficiency"},
    ],

    "valuation": {
        "primary":   ["EV/EBITDA", "EV/MW Installed"],
        "secondary": ["P/E", "EV/Capacity Pipeline"],
        "notes": (
            "Renewables are infrastructure assets — value on EV/EBITDA (typically 12–18x for quality operators). "
            "EV/MW installed (₹ per MW) is useful for comparing acquisition vs. greenfield cost. "
            "P/E is distorted by high D&A on project assets — EBITDA-level metrics are more meaningful."
        ),
        "bands": {
            "ev_ebitda": {"attractive": (0, 12), "fair": (12, 18), "expensive": (18, 999)},
        },
    },

    "llm_context": (
        "This is a RENEWABLE ENERGY company. Focus on: installed GW, capacity pipeline, Plant Load Factor, "
        "Debt/EBITDA, interest coverage, % PPA-backed revenue, and operating cash flow. "
        "Do NOT apply generic P/E or revenue-growth framing — renewables are infrastructure, valued on EV/EBITDA. "
        "Key risk: leverage + discom payment delays. "
        "Key moat: PPAs + scale + execution track record."
    ),
}
