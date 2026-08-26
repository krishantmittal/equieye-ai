# modules/sectors/insurance.py
"""
Insurance — Sector Module
"""

SECTOR_CONFIG: dict = {
    "slug": "insurance",
    "display_name": "Insurance",

    "key_metrics": [
        {"id": "gwp_growth",        "label": "Gross Written Premium Growth", "unit": "%", "yf_key": None, "higher_is_better": True},
        {"id": "vnb_margin",        "label": "VNB Margin (Life)",            "unit": "%", "yf_key": None, "higher_is_better": True},
        {"id": "combined_ratio",    "label": "Combined Ratio (General)",     "unit": "%", "yf_key": None, "higher_is_better": False},
        {"id": "persistency_13m",   "label": "13th Month Persistency",       "unit": "%", "yf_key": None, "higher_is_better": True},
        {"id": "solvency_ratio",    "label": "Solvency Ratio",               "unit": "x", "yf_key": None, "higher_is_better": True},
        {"id": "claims_ratio",      "label": "Claims Ratio",                 "unit": "%", "yf_key": None, "higher_is_better": False},
        {"id": "embedded_value_growth", "label": "Embedded Value Growth",    "unit": "%", "yf_key": None, "higher_is_better": True},
        {"id": "roe",               "label": "Return on Equity",             "unit": "%", "yf_key": "returnOnEquity", "higher_is_better": True},
    ],

    "scoring_rules": [
        {"metric": "gwp_growth",      "op": ">", "threshold": 15.0, "points": 20, "max": 20},
        {"metric": "gwp_growth",      "op": ">", "threshold": 8.0,  "points": 12, "max": 20},
        {"metric": "vnb_margin",      "op": ">", "threshold": 25.0, "points": 20, "max": 20},
        {"metric": "vnb_margin",      "op": ">", "threshold": 15.0, "points": 12, "max": 20},
        {"metric": "persistency_13m", "op": ">", "threshold": 85.0, "points": 15, "max": 15},
        {"metric": "persistency_13m", "op": ">", "threshold": 75.0, "points": 8,  "max": 15},
        {"metric": "solvency_ratio",  "op": ">", "threshold": 2.0,  "points": 15, "max": 15},
        {"metric": "solvency_ratio",  "op": ">", "threshold": 1.5,  "points": 8,  "max": 15},
        {"metric": "combined_ratio",  "op": "<", "threshold": 100.0,"points": 15, "max": 15},
        {"metric": "combined_ratio",  "op": "<", "threshold": 105.0,"points": 8,  "max": 15},
        {"metric": "roe",             "op": ">", "threshold": 15.0, "points": 15, "max": 15},
    ],
    "score_max": 100,

    "risk_factors": [
        "Persistency deterioration (policy lapses) destroys embedded value built up over years",
        "Regulatory changes on commission structures or surrender value norms compress margins",
        "Combined ratio > 100% for general insurers means underwriting losses",
        "Bancassurance channel dependency risk if distribution partnership terms change",
        "Catastrophic event risk (floods, cyclones) for general/health insurers",
        "Interest rate risk on investment book backing long-duration life liabilities",
    ],

    "moat_factors": [
        {"factor": "Distribution Network",  "description": "Multi-channel distribution (agency, bancassurance, digital) is costly and slow to build"},
        {"factor": "Brand Trust",           "description": "Insurance is a trust-driven purchase — established brands have a durable edge"},
        {"factor": "Underwriting Discipline","description": "Actuarial expertise and risk-based pricing protect long-term profitability"},
        {"factor": "Product Mix",           "description": "Higher share of protection/non-par products improves margin quality (VNB)"},
        {"factor": "Embedded Value Base",   "description": "A large in-force book compounds value even with modest new business growth"},
    ],

    "bull_case": [
        "India's insurance penetration (~4% of GDP) is well below global average — long runway",
        "Rising financial literacy and protection-gap awareness post-pandemic",
        "Shift towards higher-margin protection and non-par products improving VNB margin",
        "Bancassurance and digital distribution lowering customer acquisition cost over time",
        "Regulatory push (IRDAI 'Insurance for All by 2047') as a structural tailwind",
    ],

    "bear_case": [
        "Persistency decline due to mis-selling fallout or economic stress on policyholders",
        "Regulatory tightening on commissions/surrender charges compressing new business margins",
        "Intensifying competition compressing pricing in motor/health general insurance",
        "Combined ratio deterioration from catastrophic claims (floods, pandemics)",
        "Bancassurance partner renegotiating terms or switching insurer partners",
    ],

    "red_flags": [
        {"condition": "persistency_13m < 70",  "severity": "high",   "message": "13th month persistency < 70% — high policy lapse rate destroying value"},
        {"condition": "solvency_ratio < 1.5",  "severity": "high",   "message": "Solvency ratio < 1.5x — close to regulatory minimum, capital risk"},
        {"condition": "combined_ratio > 105",  "severity": "high",   "message": "Combined ratio > 105% — sustained underwriting losses"},
        {"condition": "vnb_margin < 10",       "severity": "medium", "message": "VNB margin < 10% — new business profitability is weak"},
        {"condition": "gwp_growth < 5",        "severity": "medium", "message": "GWP growth < 5% — premium growth lagging sector"},
    ],

    "valuation": {
        "primary":   ["P/EV (Price to Embedded Value)", "VNB Multiple"],
        "secondary": ["P/B"],
        "notes": (
            "Life insurers are valued on P/EV (typically 2-4x for quality franchises) — embedded value "
            "captures the discounted value of the in-force book plus net worth. "
            "General insurers are valued more like P/B with combined ratio as the key profitability lens. "
            "P/E is less meaningful due to actuarial reserve accounting distorting reported profit."
        ),
        "bands": {
            "p_ev": {"attractive": (0, 2.0), "fair": (2.0, 3.5), "expensive": (3.5, 99)},
            # P/EV is the textbook-correct metric per the notes above, but
            # yfinance never actually supplies embedded value data, so that
            # band was silently dead — every insurer fell back to the same
            # generic hardcoded P/B formula used for banks, ignoring that
            # insurers structurally trade at much higher P/B than banks
            # (life insurers especially, since embedded value sits well
            # above accounting book value). Adding an explicit P/B band so
            # the fallback the app actually uses is sector-calibrated.
            # NOTE: these thresholds are a reasonable approximation based on
            # typical listed Indian insurer multiples, not sourced from a
            # verified dataset — sanity-check against real comps if this
            # scoring needs to be precise.
            "price_to_book": {"attractive": (0, 4.0), "fair": (4.0, 8.0), "expensive": (8.0, 99)},
        },
    },

    "llm_context": (
        "This is an INSURANCE company. For LIFE insurers focus on: VNB margin, persistency, embedded value growth, "
        "product mix (protection vs savings). For GENERAL/HEALTH insurers focus on: combined ratio, claims ratio, "
        "GWP growth. Always check solvency ratio for capital adequacy. "
        "Do NOT apply standard P/E valuation — use P/EV for life insurers, P/B + combined ratio for general insurers. "
        "Persistency and combined ratio are the most important quality signals."
    ),
}
