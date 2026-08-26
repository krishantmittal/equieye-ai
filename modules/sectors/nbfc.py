# modules/sectors/nbfc.py
"""
NBFC (Non-Banking Financial Company) — Sector Module
"""

SECTOR_CONFIG: dict = {
    "slug": "nbfc",
    "display_name": "NBFC",

    "key_metrics": [
        {"id": "aum_growth",        "label": "AUM Growth (YoY)",        "unit": "%", "yf_key": None,             "higher_is_better": True},
        {"id": "nim",               "label": "Net Interest Margin",     "unit": "%", "yf_key": None,             "higher_is_better": True},
        {"id": "gross_npa",         "label": "Gross Stage 3 (GNPA)",    "unit": "%", "yf_key": None,             "higher_is_better": False},
        {"id": "car",               "label": "Capital Adequacy Ratio",  "unit": "%", "yf_key": None,             "higher_is_better": True},
        {"id": "cost_of_funds",     "label": "Cost of Funds",           "unit": "%", "yf_key": None,             "higher_is_better": False},
        {"id": "roa",               "label": "Return on Assets",        "unit": "%", "yf_key": "returnOnAssets","higher_is_better": True},
        {"id": "roe",               "label": "Return on Equity",        "unit": "%", "yf_key": "returnOnEquity","higher_is_better": True},
        {"id": "borrowing_mix_bank","label": "Bank Borrowing Mix",      "unit": "%", "yf_key": None,             "higher_is_better": False},
    ],

    "scoring_rules": [
        {"metric": "aum_growth",   "op": ">", "threshold": 20.0, "points": 20, "max": 20},
        {"metric": "aum_growth",   "op": ">", "threshold": 12.0, "points": 12, "max": 20},
        {"metric": "roa",          "op": ">", "threshold": 3.0,  "points": 20, "max": 20},
        {"metric": "roa",          "op": ">", "threshold": 2.0,  "points": 12, "max": 20},
        {"metric": "roe",          "op": ">", "threshold": 18.0, "points": 15, "max": 15},
        {"metric": "roe",          "op": ">", "threshold": 12.0, "points": 8,  "max": 15},
        {"metric": "gross_npa",    "op": "<", "threshold": 2.0,  "points": 20, "max": 20},
        {"metric": "gross_npa",    "op": "<", "threshold": 3.5,  "points": 10, "max": 20},
        {"metric": "car",          "op": ">", "threshold": 20.0, "points": 15, "max": 15},
        {"metric": "car",          "op": ">", "threshold": 15.0, "points": 8,  "max": 15},
    ],
    "score_max": 100,

    "risk_factors": [
        "Asset-liability mismatch — NBFCs borrow short and lend long, creating liquidity risk",
        "Dependence on bank borrowings/CP market makes funding costlier in tight liquidity cycles",
        "Asset quality risk in unsecured retail/MFI lending segments rises sharply in downturns",
        "RBI's tightening prudential norms (scale-based regulation) raises compliance costs",
        "Credit rating downgrade can trigger a funding cost spiral",
        "Concentration risk in a single asset class (gold loans, vehicle finance, MFI)",
    ],

    "moat_factors": [
        {"factor": "Underwriting Expertise",  "description": "Deep niche underwriting (e.g., used vehicles, MSME) that banks find hard to replicate profitably"},
        {"factor": "Distribution Reach",      "description": "Last-mile reach into semi-urban/rural India where banks have limited branch presence"},
        {"factor": "Diversified Funding",     "description": "Access to multiple funding sources (banks, bonds, securitisation, ECBs) reduces cost of funds"},
        {"factor": "Credit Rating",           "description": "AAA/AA+ rated NBFCs access cheaper wholesale funding — a major competitive edge"},
        {"factor": "Phygital Model",          "description": "Combination of branch presence + digital underwriting improves turnaround and reach"},
    ],

    "bull_case": [
        "Credit-starved MSME and underbanked retail segments offer high-growth, high-yield lending opportunity",
        "Co-lending partnerships with banks provide low-cost capital while NBFC retains origination edge",
        "Falling cost of funds in a rate-cut cycle expands NIMs",
        "Digital underwriting and alternate data scoring improve risk-adjusted returns at scale",
        "AUM growth compounding faster than the banking system due to underserved niches",
    ],

    "bear_case": [
        "Liquidity crunch (like 2018 IL&FS or 2019 DHFL) triggers funding freeze for weaker NBFCs",
        "Asset quality deterioration in unsecured/MFI book during economic stress",
        "RBI tightening risk weights on NBFC lending, raising capital requirements",
        "Rising cost of funds compressing NIM faster than yield repricing",
        "Aggressive growth without commensurate risk management leading to credit losses",
    ],

    "red_flags": [
        {"condition": "gross_npa > 4",          "severity": "high",   "message": "GNPA > 4% — asset quality stress in the loan book"},
        {"condition": "car < 15",               "severity": "high",   "message": "CAR < 15% — capital buffer thin for a leveraged lending business"},
        {"condition": "borrowing_mix_bank > 70","severity": "medium", "message": "Bank borrowing > 70% of funding — concentrated funding source risk"},
        {"condition": "roa < 1.5",              "severity": "medium", "message": "ROA < 1.5% — weak profitability for a specialty lender"},
        {"condition": "aum_growth < 5",         "severity": "medium", "message": "AUM growth < 5% — growth engine has stalled"},
        {"condition": "cost_of_funds > 9",      "severity": "medium", "message": "Cost of funds > 9% — funding disadvantage vs banks compressing NIM"},
    ],

    "valuation": {
        "primary":   ["P/B Ratio", "ROE"],
        "secondary": ["P/E Ratio"],
        "notes": (
            "Like banks, NBFCs are valued on P/B anchored to ROE sustainability. "
            "Quality NBFCs with ROE > 18% and stable asset quality trade at 3-5x P/B; "
            "weaker/cyclical NBFCs trade closer to 1-2x P/B. "
            "Funding cost trajectory is a key swing factor for near-term earnings."
        ),
        "bands": {
            "price_to_book": {"attractive": (0, 3.0), "fair": (3.0, 6.0), "expensive": (6.0, 99)},
        },
    },

    "llm_context": (
        "This is an NBFC (Non-Banking Financial Company). Focus on: AUM growth, NIM, Gross Stage 3 (NPA), "
        "Capital Adequacy Ratio, cost of funds, ROA, and funding mix. "
        "Key risk is asset-liability mismatch and funding cost volatility — unlike banks, NBFCs cannot "
        "raise CASA deposits and rely on wholesale funding. "
        "Valuation should use P/B and ROE, similar to banks, not generic P/E."
    ),
}
