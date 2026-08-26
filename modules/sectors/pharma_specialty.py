# modules/sectors/pharma_specialty.py
"""
Specialty Pharma — Sector Module
===================================
Split out from the monolithic pharma.py (see engineering_rd.py for the
precedent). Specialty pharma companies develop and sell proprietary or
complex branded products — often protected by patents, formulation
complexity, or regulatory exclusivity — rather than competing purely on
generic-manufacturing cost and scale. The moat is product/IP
differentiation and prescriber relationships; the risk profile is
dominated by clinical/regulatory pipeline binary events and patent
cliffs, not commodity price erosion.
"""

SECTOR_CONFIG: dict = {
    "slug": "pharma_specialty",
    "display_name": "Specialty Pharma",

    "key_metrics": [
        {"id": "revenue_growth",   "label": "Revenue Growth (YoY)",     "unit": "%",  "yf_key": "revenueGrowth",   "higher_is_better": True},
        {"id": "ebitda_margin",    "label": "EBITDA Margin",            "unit": "%",  "yf_key": "ebitdaMargins",   "higher_is_better": True},
        {"id": "rnd_pct_revenue",  "label": "R&D as % of Revenue",      "unit": "%",  "yf_key": None,              "higher_is_better": True},
        {"id": "pipeline_stage_count", "label": "Late-Stage Pipeline (#)", "unit": "#","yf_key": None,             "higher_is_better": True},
        {"id": "patent_cliff_exposure", "label": "Revenue Facing Patent Expiry (3yr)", "unit": "%", "yf_key": None, "higher_is_better": False},
        {"id": "de_ratio",         "label": "Debt/Equity",              "unit": "x",  "yf_key": "debtToEquity",   "higher_is_better": False},
        {"id": "roe",              "label": "Return on Equity",         "unit": "%",  "yf_key": "returnOnEquity", "higher_is_better": True},
    ],

    "scoring_rules": [
        {"metric": "ebitda_margin",   "op": ">", "threshold": 28.0, "points": 20, "max": 20},
        {"metric": "ebitda_margin",   "op": ">", "threshold": 20.0, "points": 12, "max": 20},
        {"metric": "revenue_growth",  "op": ">", "threshold": 15.0, "points": 20, "max": 20},
        {"metric": "revenue_growth",  "op": ">", "threshold": 8.0,  "points": 12, "max": 20},
        {"metric": "rnd_pct_revenue", "op": ">", "threshold": 12.0, "points": 15, "max": 15},
        {"metric": "rnd_pct_revenue", "op": ">", "threshold": 7.0,  "points": 8,  "max": 15},
        {"metric": "patent_cliff_exposure", "op": "<", "threshold": 15.0, "points": 15, "max": 15},
        {"metric": "de_ratio",        "op": "<", "threshold": 0.3,  "points": 10, "max": 10},
        {"metric": "roe",             "op": ">", "threshold": 15.0, "points": 10, "max": 10},
    ],
    "score_max": 100,

    "risk_factors": [
        "Clinical trial failure or a Complete Response Letter (CRL) can erase years of R&D investment on a single asset",
        "Patent cliff risk: loss of exclusivity on a key product opens the door to generic competition and rapid price erosion",
        "Payer/reimbursement pressure — formulary placement and price negotiations with insurers directly affect realized pricing",
        "High R&D capex with binary (not gradual) payoff — a single trial failure can materially impair the investment case",
        "Regulatory approval timeline risk — delays push out revenue and extend the cash-burn runway",
        "Physician/prescriber adoption risk for a newly launched product, independent of clinical efficacy",
    ],

    "moat_factors": [
        {"factor": "Patent-Protected Products",  "description": "Composition-of-matter or formulation patents create a genuine, legally-enforced monopoly period — the strongest moat type in pharma"},
        {"factor": "Formulation/Delivery Complexity", "description": "Complex delivery mechanisms (long-acting injectables, novel drug-delivery systems) are difficult and slow for generic competitors to replicate even after patent expiry"},
        {"factor": "Prescriber Relationships",   "description": "Physician trust and clinical-data familiarity built over years of specialty sales-force engagement create switching friction independent of price"},
        {"factor": "Regulatory Exclusivity",     "description": "Orphan drug status, new chemical entity exclusivity, or other regulatory protections extend the moat beyond the patent term itself"},
        {"factor": "Clinical Data Depth",        "description": "A larger post-marketing clinical evidence base than a newly-launched competitor reinforces prescriber confidence and payer formulary position"},
    ],

    "bull_case": [
        "Late-stage pipeline asset approaching approval — a binary catalyst with large addressable-market upside",
        "New product launch ramping ahead of expectations on physician adoption and formulary wins",
        "Regulatory exclusivity (orphan drug, breakthrough therapy) extending the effective patent runway",
        "Label expansion into new indications for an already-approved product, extending its revenue life",
        "Out-licensing or partnership deal validating pipeline value and providing non-dilutive capital",
    ],

    "bear_case": [
        "Late-stage clinical trial failure or a CRL on the lead pipeline asset",
        "Patent cliff on a key product with no adequately-scaled replacement in the pipeline",
        "Payer pushback or unfavorable formulary placement limiting realized pricing on a newly launched product",
        "Slower-than-expected physician adoption of a new launch versus pre-launch expectations",
        "A competitor's earlier or better-differentiated launch in the same indication eroding addressable market",
    ],

    "red_flags": [
        {"condition": "rnd_pct_revenue < 5",           "severity": "medium", "message": "R&D < 5% of revenue — thin for a specialty pipeline business; growth may depend entirely on existing products"},
        {"condition": "patent_cliff_exposure > 30",    "severity": "high",   "message": "Patent cliff exposure > 30% of revenue over 3 years — material revenue at risk without an offsetting pipeline"},
        {"condition": "ebitda_margin < 15",            "severity": "medium", "message": "EBITDA margin < 15% — weak for specialty pharma; may indicate early-stage commercial ramp or pricing pressure"},
        {"condition": "de_ratio > 0.8",                "severity": "medium", "message": "D/E > 0.8x — elevated leverage for a business with binary clinical/regulatory risk"},
    ],

    "valuation": {
        "primary":   ["EV/EBITDA", "P/E Ratio"],
        "secondary": ["EV/Sales", "PEG-style pipeline-adjusted multiples"],
        "notes": (
            "Specialty pharma trades at a premium to generic formulators when the pipeline is genuinely "
            "differentiated (patent-protected, novel delivery, regulatory exclusivity) — but that premium "
            "should compress sharply as key products approach patent expiry without a scaled replacement. "
            "A single-asset-dependent specialty name deserves a much larger risk discount than a diversified "
            "portfolio."
        ),
        "bands": {
            "pe_ratio":  {"attractive": (0, 22), "fair": (22, 35), "expensive": (35, 999)},
            "ev_ebitda": {"attractive": (0, 14), "fair": (14, 22), "expensive": (22, 999)},
        },
    },

    "llm_context": (
        "This is a Specialty Pharma company — it develops and sells proprietary or complex branded products "
        "protected by patents, formulation complexity, or regulatory exclusivity, rather than competing "
        "primarily on generic-manufacturing cost and scale. Distinct from a generic formulator (competes on "
        "ANDA pipeline breadth and distribution, not product-level patent protection) and from biotech "
        "(specialty pharma is typically small-molecule and later-stage/commercial, while biotech skews "
        "biologics and earlier-stage). "
        "Key demand drivers: pipeline catalysts approaching approval, new launch ramps, label expansions, "
        "regulatory exclusivity. "
        "Key risks: clinical trial failure or CRL on a key asset, patent cliff without an offsetting pipeline, "
        "payer/reimbursement pressure, slower-than-expected launch adoption. "
        "Treat pipeline concentration explicitly — a company dependent on one or two key assets carries "
        "materially more binary risk than a diversified specialty portfolio, even at similar current margins. "
        "Do NOT apply D/E analysis the same way as industrials — should be low-leverage."
    ),
}
