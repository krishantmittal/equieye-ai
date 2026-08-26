# modules/sectors/pharma.py
"""
Pharmaceuticals & Biotech — Sector Module
"""

SECTOR_CONFIG: dict = {
    "slug": "pharma",
    "display_name": "Pharmaceuticals & Biotech",

    "key_metrics": [
        {"id": "revenue_growth",    "label": "Revenue Growth (YoY)",   "unit": "%",  "yf_key": "revenueGrowth",   "higher_is_better": True},
        {"id": "ebitda_margin",     "label": "EBITDA Margin",          "unit": "%",  "yf_key": "ebitdaMargins",   "higher_is_better": True},
        {"id": "rnd_pct_revenue",   "label": "R&D as % of Revenue",    "unit": "%",  "yf_key": None,              "higher_is_better": True},
        {"id": "us_revenue_pct",    "label": "US Revenue (%)",         "unit": "%",  "yf_key": None,              "higher_is_better": True},
        {"id": "anda_pipeline",     "label": "ANDA Pipeline (#)",      "unit": "#",  "yf_key": None,              "higher_is_better": True},
        {"id": "usfda_status",      "label": "US FDA Compliance",      "unit": "text","yf_key": None,             "higher_is_better": True},
        {"id": "de_ratio",          "label": "Debt/Equity",            "unit": "x",  "yf_key": "debtToEquity",   "higher_is_better": False},
        {"id": "roe",               "label": "Return on Equity",       "unit": "%",  "yf_key": "returnOnEquity", "higher_is_better": True},
    ],

    "scoring_rules": [
        {"metric": "ebitda_margin",   "op": ">", "threshold": 28.0, "points": 20, "max": 20},
        {"metric": "ebitda_margin",   "op": ">", "threshold": 20.0, "points": 12, "max": 20},
        {"metric": "ebitda_margin",   "op": ">", "threshold": 14.0, "points": 6,  "max": 20},
        {"metric": "revenue_growth",  "op": ">", "threshold": 15.0, "points": 20, "max": 20},
        {"metric": "revenue_growth",  "op": ">", "threshold": 8.0,  "points": 12, "max": 20},
        {"metric": "rnd_pct_revenue", "op": ">", "threshold": 8.0,  "points": 15, "max": 15},
        {"metric": "rnd_pct_revenue", "op": ">", "threshold": 5.0,  "points": 8,  "max": 15},
        {"metric": "de_ratio",        "op": "<", "threshold": 0.3,  "points": 15, "max": 15},
        {"metric": "de_ratio",        "op": "<", "threshold": 0.7,  "points": 8,  "max": 15},
        {"metric": "roe",             "op": ">", "threshold": 20.0, "points": 10, "max": 10},
    ],
    "score_max": 100,

    "risk_factors": [
        "US FDA import alerts, Form 483 observations, or consent decrees can halt exports",
        "Price erosion in US generics market as new ANDA approvals intensify competition",
        "Patent expiry cliff risk for innovator-focused companies",
        "NPPA price controls limiting domestic formulations pricing",
        "API supply chain concentration in China creates geopolitical risk",
        "Currency risk: USD/INR movement impacts US-export margins",
        "Clinical trial failure risk for novel drug candidates",
    ],

    "moat_factors": [
        {"factor": "US ANDA Portfolio",     "description": "Approved ANDAs with first-to-file exclusivity periods create temporary monopoly profits"},
        {"factor": "Manufacturing Scale",   "description": "WHO/FDA-approved facilities with scale create cost leadership in generics"},
        {"factor": "R&D Pipeline",          "description": "Differentiated complex generics (injectables, inhalers) command better pricing and fewer competitors"},
        {"factor": "Branded Domestic Moat","description": "Strong domestic MR force and brand recall in chronic therapies create pricing power"},
        {"factor": "Backward Integration", "description": "In-house API manufacturing insulates from supply disruption and improves margins"},
    ],

    "bull_case": [
        "US generics pricing stabilisation + niche product launches drive US revenue recovery",
        "India domestic formulations: chronic therapy penetration (diabetes, cardiac) at low base",
        "Complex generics (peptides, inhalers, injectables) — limited competition, better margins",
        "CDMO/contract manufacturing boom as global pharma diversifies away from China",
        "Biosimilar pipeline: long development but massive market once approved",
    ],

    "bear_case": [
        "US FDA warning letter triggering plant shutdown and revenue loss",
        "Price erosion acceleration in US base generics as competition floods market",
        "R&D pipeline setbacks increasing without offsetting new approvals",
        "Domestic price controls tightening on essential medicines",
        "Geo-political supply chain disruption cutting API availability",
    ],

    "red_flags": [
        {"condition": "ebitda_margin < 12",  "severity": "high",   "message": "EBITDA margin < 12% — well below pharma norms, structural issues likely"},
        {"condition": "rnd_pct_revenue < 3", "severity": "medium", "message": "R&D < 3% of revenue — pipeline may not sustain growth beyond base products"},
        {"condition": "de_ratio > 1.0",      "severity": "medium", "message": "D/E > 1x — high leverage for a business with regulatory binary risks"},
        {"condition": "revenue_growth < 5",  "severity": "medium", "message": "Revenue growth < 5% — below sector growth rate, market share at risk"},
        {"condition": "us_revenue_pct > 60", "severity": "medium", "message": "US revenue > 60% — high concentration; FDA compliance risk is elevated"},
    ],

    "valuation": {
        "primary":   ["P/E Ratio", "EV/EBITDA"],
        "secondary": ["EV/Sales", "P/FCF"],
        "notes": (
            "Pharma trades on P/E adjusted for R&D pipeline value. "
            "Indian pharma mid-caps trade at 18–28x P/E; large-caps 22–32x. "
            "FDA-compliant, niche-generics players deserve premium to commodity API manufacturers. "
            "Binary risk of US FDA action justifies a discount for single-facility dependency."
        ),
        "bands": {
            "pe_ratio":  {"attractive": (0, 20), "fair": (20, 40), "expensive": (40, 999)},
            "ev_ebitda": {"attractive": (0, 12), "fair": (12, 20), "expensive": (20, 999)},
        },
    },

    "llm_context": (
        "This is a PHARMACEUTICAL company. Focus on: US FDA compliance status, ANDA/product pipeline, "
        "R&D spend as % of revenue, US vs domestic revenue mix, EBITDA margins, and debt levels. "
        "Key binary risk: US FDA import alerts or warning letters. "
        "Assess whether the growth is driven by commodity generics (low value) or "
        "complex/specialty generics (high value, limited competition). "
        "Do NOT apply D/E analysis the same way as industrials — pharma should be nearly debt-free."
    ),
}
