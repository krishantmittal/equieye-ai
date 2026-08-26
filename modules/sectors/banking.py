# modules/sectors/banking.py
"""
Banking & Financial Services — Sector Module
"""

SECTOR_CONFIG: dict = {
    "slug": "banking",
    "display_name": "Banking & Financial Services",

    # ── A. Key Metrics ────────────────────────────────────────────────────────
    "key_metrics": [
        {"id": "casa_ratio",       "label": "CASA Ratio",              "unit": "%",  "yf_key": None, "higher_is_better": True},
        {"id": "gross_npa",        "label": "Gross NPA",               "unit": "%",  "yf_key": None, "higher_is_better": False},
        {"id": "net_npa",          "label": "Net NPA",                 "unit": "%",  "yf_key": None, "higher_is_better": False},
        {"id": "pcr",              "label": "Provision Coverage Ratio","unit": "%",  "yf_key": None, "higher_is_better": True},
        {"id": "cet1_ratio",       "label": "CET1 Ratio",              "unit": "%",  "yf_key": None, "higher_is_better": True},
        {"id": "nim",              "label": "Net Interest Margin",     "unit": "%",  "yf_key": None, "higher_is_better": True},
        {"id": "credit_growth",    "label": "Credit Growth (YoY)",     "unit": "%",  "yf_key": None, "higher_is_better": True},
        {"id": "cost_to_income",   "label": "Cost-to-Income Ratio",    "unit": "%",  "yf_key": None, "higher_is_better": False},
        {"id": "roa",              "label": "Return on Assets (ROA)",  "unit": "%",  "yf_key": "returnOnAssets", "higher_is_better": True},
        {"id": "roe",              "label": "Return on Equity (ROE)",  "unit": "%",  "yf_key": "returnOnEquity", "higher_is_better": True},
    ],

    # ── B. Scoring Logic ─────────────────────────────────────────────────────
    # Each rule: (metric_id, operator, threshold, points_if_true, max_points)
    "scoring_rules": [
        # ROA: > 1.5% = excellent, > 1% = good, > 0.5% = average
        {"metric": "roa",           "op": ">",  "threshold": 1.5,  "points": 10, "max": 10},
        {"metric": "roa",           "op": ">",  "threshold": 1.0,  "points": 7,  "max": 10},
        {"metric": "roa",           "op": ">",  "threshold": 0.5,  "points": 4,  "max": 10},
        # ROE: > 15% = excellent
        {"metric": "roe",           "op": ">",  "threshold": 15.0, "points": 10, "max": 10},
        {"metric": "roe",           "op": ">",  "threshold": 12.0, "points": 7,  "max": 10},
        {"metric": "roe",           "op": ">",  "threshold": 8.0,  "points": 4,  "max": 10},
        # Gross NPA: <2% excellent, <3% ok, <5% weak
        {"metric": "gross_npa",     "op": "<",  "threshold": 2.0,  "points": 15, "max": 15},
        {"metric": "gross_npa",     "op": "<",  "threshold": 3.0,  "points": 10, "max": 15},
        {"metric": "gross_npa",     "op": "<",  "threshold": 5.0,  "points": 5,  "max": 15},
        # CASA > 40% is strong franchise
        {"metric": "casa_ratio",    "op": ">",  "threshold": 45.0, "points": 10, "max": 10},
        {"metric": "casa_ratio",    "op": ">",  "threshold": 35.0, "points": 6,  "max": 10},
        # PCR > 80% = well-provisioned
        {"metric": "pcr",           "op": ">",  "threshold": 80.0, "points": 10, "max": 10},
        {"metric": "pcr",           "op": ">",  "threshold": 70.0, "points": 6,  "max": 10},
    ],
    "score_max": 100,

    # ── C. Risk Factors ───────────────────────────────────────────────────────
    "risk_factors": [
        "Credit cycle turning — rising NPAs compress profitability",
        "Regulatory tightening on capital adequacy (RBI Basel norms)",
        "Margin compression as deposit costs rise faster than lending rates",
        "Concentration risk in unsecured retail or a single sector",
        "Systemic liquidity events (sudden deposit withdrawal risk)",
        "Fintech disruption of CASA and payments float",
    ],

    # ── D. Moat Framework ─────────────────────────────────────────────────────
    "moat_factors": [
        {"factor": "CASA Franchise",         "description": "Low-cost sticky deposits create a durable funding cost advantage"},
        {"factor": "Branch & ATM Network",   "description": "Physical reach in Tier 2/3 cities builds long-term liability franchise"},
        {"factor": "Brand Trust",            "description": "Customer trust is the single most important moat for a deposit-taking institution"},
        {"factor": "Cross-sell Ecosystem",   "description": "Ability to cross-sell insurance, wealth, and cards drives non-interest income"},
        {"factor": "Retail Deposit Strength","description": "High retail deposit mix insulates from wholesale funding volatility"},
    ],

    # ── E. Bull Case Drivers ──────────────────────────────────────────────────
    "bull_case": [
        "India's credit penetration (credit/GDP) is among the lowest globally — long structural runway",
        "Formalisation of the economy drives incremental credit demand into organised banking",
        "Rising CASA + falling credit costs → sustained ROE expansion",
        "Successful digital banking moat building (mobile app, UPI, co-branded cards)",
        "Improving asset quality cycle after years of clean-up",
    ],

    # ── F. Bear Case Drivers ──────────────────────────────────────────────────
    "bear_case": [
        "Deteriorating asset quality in the unsecured/MSME book",
        "Margin compression as RBI tightens or deposit wars intensify",
        "CASA erosion as customers shift to mutual funds/UPI savings",
        "Regulatory caps on fees or cards/payments monetisation",
        "Macro slowdown reducing credit demand and raising delinquencies",
    ],

    # ── G. Red Flag Detection Rules ───────────────────────────────────────────
    "red_flags": [
        {"condition": "gross_npa > 5",   "severity": "high",   "message": "GNPA > 5% — asset quality under severe stress"},
        {"condition": "net_npa > 3",     "severity": "high",   "message": "Net NPA > 3% — provisioning may be insufficient"},
        {"condition": "pcr < 70",        "severity": "high",   "message": "PCR < 70% — bank is under-provisioned for bad loans"},
        {"condition": "casa_ratio < 30", "severity": "medium", "message": "CASA < 30% — high-cost liability franchise, NIM at risk"},
        {"condition": "roa < 0.5",       "severity": "medium", "message": "ROA < 0.5% — poor asset productivity"},
        {"condition": "roe < 8",         "severity": "medium", "message": "ROE < 8% — below cost of equity, value-destructive"},
        {"condition": "cost_to_income > 55", "severity": "low", "message": "Cost-to-Income > 55% — operational efficiency lagging peers"},
        {"condition": "cet1_ratio < 10", "severity": "high",  "message": "CET1 < 10% — capital adequacy risk, dilution possible"},
    ],

    # ── H. Valuation Framework ────────────────────────────────────────────────
    "valuation": {
        "primary":   ["P/B Ratio", "ROE"],
        "secondary": ["P/E Ratio"],
        "notes": (
            "Banks are best valued on P/B because book value anchors to net assets after provisioning. "
            "A bank with ROE > 15% deserves P/B > 2.5x. "
            "High-NPA banks often trade at steep P/B discounts — discount can persist if asset quality doesn't improve."
        ),
        "bands": {
            "price_to_book": {"attractive": (0, 2.0), "fair": (2.0, 4.0), "expensive": (4.0, 99)},
        },
    },

    # ── LLM prompt context injected into sector_analysis ─────────────────────
    "llm_context": (
        "This is a BANKING company. Focus your analysis on: CASA ratio, NIM, "
        "Gross/Net NPA, Provision Coverage, CET1 capital adequacy, ROA, ROE, "
        "and credit growth. "
        "Do NOT apply generic P/E or D/E analysis — banks are valued on P/B and ROE. "
        "Asset quality (NPAs) is the single most important risk factor. "
        "Classify the bank as: (a) asset-quality-led franchise, (b) liability-franchise-led, "
        "or (c) fee-income diversified."
    ),
}
