# modules/sectors/biotech.py
"""
Biotech / Biosimilars — Sector Module
========================================
Split out from the monolithic pharma.py (see engineering_rd.py for the
precedent). Biotech/biosimilar companies (Biocon, Bharat Biotech, and
biosimilar-focused pipelines) develop and manufacture biologics — a
fundamentally harder-to-replicate manufacturing process than small-
molecule generics, with correspondingly higher capex, longer
development timelines, and larger binary regulatory/clinical risk.
Distinct from specialty pharma (typically small-molecule, later-stage)
and from generic formulators (small-molecule, manufacturing-cost-
driven, near-zero clinical risk on already-approved products).
"""

SECTOR_CONFIG: dict = {
    "slug": "biotech",
    "display_name": "Biotech / Biosimilars",

    "key_metrics": [
        {"id": "revenue_growth",        "label": "Revenue Growth (YoY)",       "unit": "%",  "yf_key": "revenueGrowth",   "higher_is_better": True},
        {"id": "ebitda_margin",         "label": "EBITDA Margin",              "unit": "%",  "yf_key": "ebitdaMargins",   "higher_is_better": True},
        {"id": "rnd_pct_revenue",       "label": "R&D as % of Revenue",        "unit": "%",  "yf_key": None,              "higher_is_better": True},
        {"id": "biosimilar_approvals",  "label": "Approved Biosimilars (#)",   "unit": "#",  "yf_key": None,              "higher_is_better": True},
        {"id": "us_eu_revenue_pct",     "label": "US/EU Revenue (%)",          "unit": "%",  "yf_key": None,              "higher_is_better": True},
        {"id": "de_ratio",              "label": "Debt/Equity",                "unit": "x",  "yf_key": "debtToEquity",   "higher_is_better": False},
        {"id": "roe",                   "label": "Return on Equity",           "unit": "%",  "yf_key": "returnOnEquity", "higher_is_better": True},
    ],

    "scoring_rules": [
        {"metric": "ebitda_margin",   "op": ">", "threshold": 25.0, "points": 20, "max": 20},
        {"metric": "ebitda_margin",   "op": ">", "threshold": 15.0, "points": 10, "max": 20},
        {"metric": "revenue_growth",  "op": ">", "threshold": 18.0, "points": 20, "max": 20},
        {"metric": "revenue_growth",  "op": ">", "threshold": 10.0, "points": 12, "max": 20},
        {"metric": "rnd_pct_revenue", "op": ">", "threshold": 15.0, "points": 15, "max": 15},
        {"metric": "rnd_pct_revenue", "op": ">", "threshold": 8.0,  "points": 8,  "max": 15},
        {"metric": "de_ratio",        "op": "<", "threshold": 0.4,  "points": 15, "max": 15},
        {"metric": "roe",             "op": ">", "threshold": 10.0, "points": 10, "max": 10},
    ],
    "score_max": 100,

    "risk_factors": [
        "Binary clinical/regulatory trial outcomes — biologics development carries longer timelines and higher failure rates than small-molecule generics",
        "High R&D and manufacturing capex with a long payback period before a biosimilar reaches commercial scale",
        "Biosimilar pricing competition intensifying as more players enter approved molecules",
        "Manufacturing complexity risk — biologics production is far more sensitive to process deviation than small-molecule synthesis, raising quality/regulatory risk",
        "Currency and geopolitical risk — much biosimilar revenue is EU/US-denominated and subject to region-specific regulatory/reimbursement regimes",
        "Interchangeability and payer-substitution risk — biosimilar adoption depends on payer/physician willingness to substitute, not just regulatory approval",
    ],

    "moat_factors": [
        {"factor": "Manufacturing Complexity",   "description": "Biologics production (cell-line development, process validation, quality control) is a multi-year, capital-intensive barrier that small-molecule competitors cannot easily cross into"},
        {"factor": "Regulatory Approval Track Record", "description": "A history of successful biosimilar approvals in regulated markets (US, EU) lowers the bar and de-risks the next pipeline asset"},
        {"factor": "Global Market Access",       "description": "Established distribution/commercialization partnerships in the US and EU are difficult for a new entrant to replicate quickly"},
        {"factor": "Pipeline Breadth",           "description": "A diversified biosimilar pipeline across multiple molecules reduces single-asset binary risk relative to a one- or two-product biotech"},
        {"factor": "Cost Leadership in Biologics", "description": "Scale manufacturing economics in a historically high-cost-to-produce category is a durable advantage once achieved"},
    ],

    "bull_case": [
        "Biosimilar market expansion as more original biologics lose exclusivity, opening new addressable markets",
        "US/EU biosimilar adoption acceleration as payers push substitution to control healthcare costs",
        "New biosimilar approvals adding to the commercial portfolio and diversifying single-asset risk",
        "Manufacturing capacity scale-up lowering unit costs and improving margins as volume ramps",
        "Partnership/licensing deals with global pharma majors validating pipeline and providing commercialization reach",
    ],

    "bear_case": [
        "Clinical trial failure or regulatory rejection (CRL) on a key pipeline biosimilar",
        "Manufacturing/quality deviation triggering a regulatory action at a biologics facility",
        "Biosimilar price erosion intensifying faster than expected as more competitors enter a molecule",
        "Slower-than-expected payer/physician adoption of an approved biosimilar versus the originator biologic",
        "Capex overrun or delayed commercial ramp on new manufacturing capacity pressuring near-term returns",
    ],

    "red_flags": [
        {"condition": "rnd_pct_revenue < 6",   "severity": "medium", "message": "R&D < 6% of revenue — thin for a biotech/biosimilar pipeline business"},
        {"condition": "ebitda_margin < 10",    "severity": "high",   "message": "EBITDA margin < 10% — weak for a scaled biosimilar business; may indicate early-stage commercial ramp or pricing pressure"},
        {"condition": "revenue_growth < 5",    "severity": "medium", "message": "Revenue growth < 5% — pipeline may not be converting into new commercial revenue"},
        {"condition": "de_ratio > 0.8",        "severity": "medium", "message": "D/E > 0.8x — elevated leverage for a business with binary clinical/regulatory and manufacturing-complexity risk"},
    ],

    "valuation": {
        "primary":   ["EV/EBITDA", "EV/Sales"],
        "secondary": ["P/E Ratio (once profitable)", "Pipeline-adjusted sum-of-the-parts"],
        "notes": (
            "Biotech/biosimilar names often trade on EV/Sales or pipeline-adjusted multiples rather than P/E, "
            "since near-term earnings can be depressed by R&D and manufacturing-capacity investment relative "
            "to long-term commercial potential. A profitable, diversified biosimilar portfolio deserves a "
            "premium to a single-asset, pre-commercial biotech — the risk profiles are not comparable despite "
            "sharing the sector label."
        ),
        "bands": {
            "pe_ratio":  {"attractive": (0, 25), "fair": (25, 45), "expensive": (45, 999)},
            "ev_ebitda": {"attractive": (0, 16), "fair": (16, 28), "expensive": (28, 999)},
        },
    },

    "llm_context": (
        "This is a Biotech / Biosimilars company — it develops and manufactures biologics (complex, large-"
        "molecule drugs), a fundamentally harder-to-replicate manufacturing process than small-molecule "
        "generics, with higher capex, longer development timelines, and larger binary regulatory/clinical "
        "risk. Distinct from specialty pharma (typically small-molecule, later-stage/commercial) and from "
        "generic formulators (small-molecule, manufacturing-cost-driven, near-zero clinical risk on already-"
        "approved products). "
        "Key demand drivers: biosimilar market expansion as originator biologics lose exclusivity, US/EU "
        "payer-driven substitution, new approvals diversifying the pipeline. "
        "Key risks: clinical/regulatory binary outcomes, manufacturing/quality deviation risk (far more "
        "sensitive than small-molecule synthesis), biosimilar price erosion, slow payer/physician adoption. "
        "Distinguish between an established, profitable, diversified biosimilar portfolio and a single-asset, "
        "pre-commercial biotech — very different risk profiles despite the shared sector label. "
        "Do NOT apply D/E analysis the same way as industrials — should be low-leverage."
    ),
}
