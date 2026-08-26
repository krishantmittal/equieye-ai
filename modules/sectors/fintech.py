# modules/sectors/fintech.py
"""
Fintech / Consumer Internet — Sector Module
"""

SECTOR_CONFIG: dict = {
    "slug": "fintech",
    "display_name": "Fintech & Consumer Internet",

    "key_metrics": [
        {"id": "tpv_growth",       "label": "TPV Growth (YoY)",        "unit": "%",  "yf_key": None, "higher_is_better": True},
        {"id": "user_growth",      "label": "Active User Growth",      "unit": "%",  "yf_key": None, "higher_is_better": True},
        {"id": "take_rate",        "label": "Take Rate",               "unit": "%",  "yf_key": None, "higher_is_better": True},
        {"id": "contribution_margin","label": "Contribution Margin",   "unit": "%",  "yf_key": None, "higher_is_better": True},
        {"id": "ebitda_margin",    "label": "EBITDA Margin",           "unit": "%",  "yf_key": "ebitdaMargins", "higher_is_better": True},
        {"id": "fcf",              "label": "Free Cash Flow",          "unit": "₹Cr","yf_key": "freeCashflow",  "higher_is_better": True},
        {"id": "revenue_growth",   "label": "Revenue Growth (YoY)",    "unit": "%",  "yf_key": "revenueGrowth", "higher_is_better": True},
        {"id": "cac",              "label": "Customer Acquisition Cost","unit": "₹", "yf_key": None, "higher_is_better": False},
    ],

    "scoring_rules": [
        {"metric": "revenue_growth","op": ">",  "threshold": 30.0, "points": 20, "max": 20},
        {"metric": "revenue_growth","op": ">",  "threshold": 20.0, "points": 12, "max": 20},
        {"metric": "revenue_growth","op": ">",  "threshold": 10.0, "points": 6,  "max": 20},
        {"metric": "ebitda_margin", "op": ">",  "threshold": 15.0, "points": 20, "max": 20},
        {"metric": "ebitda_margin", "op": ">",  "threshold": 0.0,  "points": 10, "max": 20},
        {"metric": "ebitda_margin", "op": ">",  "threshold": -10.0,"points": 5,  "max": 20},
        {"metric": "take_rate",     "op": ">",  "threshold": 1.5,  "points": 15, "max": 15},
        {"metric": "take_rate",     "op": ">",  "threshold": 0.8,  "points": 8,  "max": 15},
        {"metric": "fcf",           "op": ">",  "threshold": 0,    "points": 15, "max": 15},
    ],
    "score_max": 100,

    "risk_factors": [
        "Regulatory risk: RBI/SEBI tightening on payments, lending, or wallet limits",
        "Take rate compression as competition intensifies and merchant bargaining power grows",
        "Unit economics not proven at scale — contribution margin turning positive is key milestone",
        "Platform risk: Google/Apple/Meta entering adjacent segments",
        "UPI-zero-MDR policy risk permanently limiting payment monetisation",
        "Fraud and cybersecurity risk at scale",
    ],

    "moat_factors": [
        {"factor": "Network Effects",    "description": "More merchants attract more users; more users attract more merchants — compounding flywheel"},
        {"factor": "User Ecosystem",     "description": "Super-app stickiness: if payments, lending, and insurance are on one platform, switching is costly"},
        {"factor": "Switching Costs",    "description": "Merchant integrations (POS, reconciliation, APIs) have high technical switching costs"},
        {"factor": "Merchant Stickiness","description": "Settlement timing, working capital loans, and analytics create lock-in for merchants"},
        {"factor": "Brand & Trust",      "description": "Consumer trust in handling money is a slow-to-build, hard-to-replicate asset"},
    ],

    "bull_case": [
        "India's digital payment volume is growing at 40%+ CAGR — fintech is still in early innings",
        "Financial inclusion wave: 500M+ underbanked users entering formal financial system",
        "Cross-sell of credit, insurance, and wealth to existing payment user base",
        "Take-rate expansion as value-added services (credit on UPI, FASTag, ONDC) layer on top of payments",
        "Profitable unit economics within 2-3 years as fixed-cost leverage kicks in",
    ],

    "bear_case": [
        "Slowing TPV growth as market matures and competition from Jio Financial intensifies",
        "Regulatory caps making payments a loss-leader with no path to monetisation",
        "Rising CAC as user acquisition in metro markets saturates",
        "Persistent losses burning through cash reserves before profitability",
        "BNPL/micro-lending portfolio turning bad in a credit tightening cycle",
    ],

    "red_flags": [
        {"condition": "revenue_growth < 10",   "severity": "high",   "message": "Revenue growth < 10% — growth story losing momentum"},
        {"condition": "ebitda_margin < -20",   "severity": "high",   "message": "EBITDA margin < -20% — cash burn rate is unsustainable"},
        {"condition": "take_rate < 0.5",       "severity": "high",   "message": "Take rate < 0.5% — monetisation structurally weak"},
        {"condition": "tpv_growth < 15",       "severity": "medium", "message": "TPV growth slowing — platform engagement at risk"},
        {"condition": "fcf < 0",               "severity": "medium", "message": "Negative FCF — still burning cash; watch cash runway"},
    ],

    "valuation": {
        "primary":   ["EV/Sales", "Price/Sales"],
        "secondary": ["EV/Gross Profit", "Price/GMV"],
        "notes": (
            "P/E is not applicable for loss-making fintechs. "
            "Use EV/Sales (forward) for revenue-stage companies. "
            "Market often prices on TAM × addressable take-rate rather than current earnings. "
            "Path to EBITDA positivity is the key re-rating catalyst."
        ),
        "bands": {
            "price_to_sales": {"attractive": (0, 4), "fair": (4, 10), "expensive": (10, 999)},
        },
    },

    "llm_context": (
        "This is a FINTECH / CONSUMER INTERNET company. Focus on: TPV growth, "
        "take rate, contribution margin, path to EBITDA profitability, and cash runway. "
        "Do NOT apply P/E or P/B valuation — use EV/Sales and P/S. "
        "Key question: is this a platform with network effects, or a commodity payments processor? "
        "Assess whether unit economics improve at scale or deteriorate with competition."
    ),
}
