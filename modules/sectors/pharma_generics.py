# modules/sectors/pharma_generics.py
"""
Generic Formulators — Sector Module
=====================================
Split out from the monolithic pharma.py (see engineering_rd.py for the
precedent). Generic formulators (Sun Pharma, Cipla, Dr. Reddy's, Lupin,
Aurobindo, Zydus) sell branded and generic finished-dose products
directly to patients/pharmacies/payers through their own sales and
distribution infrastructure — a fundamentally different business from
an API manufacturer (sells intermediate ingredient to formulators) or a
CDMO (manufactures a client's molecule under contract). This is also
the default/fallback pharma bucket: a pharma company that doesn't
clearly match API, CDMO, biotech, specialty, diagnostics, or hospitals
routes here, since generic formulation is the most common Indian pharma
business model.
"""

SECTOR_CONFIG: dict = {
    "slug": "pharma_generics",
    "display_name": "Generic Formulators",

    "key_metrics": [
        {"id": "revenue_growth",   "label": "Revenue Growth (YoY)",   "unit": "%",  "yf_key": "revenueGrowth",   "higher_is_better": True},
        {"id": "ebitda_margin",    "label": "EBITDA Margin",          "unit": "%",  "yf_key": "ebitdaMargins",   "higher_is_better": True},
        {"id": "rnd_pct_revenue",  "label": "R&D as % of Revenue",    "unit": "%",  "yf_key": None,              "higher_is_better": True},
        {"id": "us_revenue_pct",   "label": "US Revenue (%)",         "unit": "%",  "yf_key": None,              "higher_is_better": True},
        {"id": "anda_pipeline",    "label": "ANDA Pipeline (#)",      "unit": "#",  "yf_key": None,              "higher_is_better": True},
        {"id": "usfda_status",     "label": "US FDA Compliance",      "unit": "text","yf_key": None,             "higher_is_better": True},
        {"id": "de_ratio",         "label": "Debt/Equity",            "unit": "x",  "yf_key": "debtToEquity",   "higher_is_better": False},
        {"id": "roe",              "label": "Return on Equity",       "unit": "%",  "yf_key": "returnOnEquity", "higher_is_better": True},
    ],

    "scoring_rules": [
        {"metric": "ebitda_margin",   "op": ">", "threshold": 26.0, "points": 20, "max": 20},
        {"metric": "ebitda_margin",   "op": ">", "threshold": 18.0, "points": 12, "max": 20},
        {"metric": "ebitda_margin",   "op": ">", "threshold": 12.0, "points": 6,  "max": 20},
        {"metric": "revenue_growth",  "op": ">", "threshold": 12.0, "points": 20, "max": 20},
        {"metric": "revenue_growth",  "op": ">", "threshold": 6.0,  "points": 12, "max": 20},
        {"metric": "rnd_pct_revenue", "op": ">", "threshold": 7.0,  "points": 15, "max": 15},
        {"metric": "rnd_pct_revenue", "op": ">", "threshold": 4.0,  "points": 8,  "max": 15},
        {"metric": "de_ratio",        "op": "<", "threshold": 0.3,  "points": 15, "max": 15},
        {"metric": "de_ratio",        "op": "<", "threshold": 0.7,  "points": 8,  "max": 15},
        {"metric": "roe",             "op": ">", "threshold": 18.0, "points": 10, "max": 10},
    ],
    "score_max": 100,

    "risk_factors": [
        "US FDA import alerts, Form 483 observations, or consent decrees can halt exports from a facility",
        "Price erosion in the US generics market as new ANDA approvals intensify competition on base products",
        "Patent litigation (Para IV challenges) risk on first-to-file opportunities",
        "NPPA price controls limiting domestic branded-formulation pricing",
        "US channel consolidation (PBM/wholesaler concentration) increases buyer pricing power",
        "Currency risk: USD/INR movement impacts US-export margins",
    ],

    "moat_factors": [
        {"factor": "US ANDA Portfolio",      "description": "Approved ANDAs with first-to-file exclusivity periods create temporary monopoly-like profits before competition floods in"},
        {"factor": "Domestic Distribution & Brand", "description": "A large medical-representative field force and brand recall in chronic therapies (diabetes, cardiac) create pricing power competitors can't easily replicate"},
        {"factor": "Complex Generics Pipeline", "description": "Differentiated products (injectables, inhalers, peptides) command better pricing and face far less competition than oral solids"},
        {"factor": "Manufacturing Scale",     "description": "WHO/FDA-approved facilities at scale create cost leadership on base generics"},
        {"factor": "Regulatory Track Record", "description": "A clean USFDA inspection history across facilities lowers approval friction for the ANDA pipeline"},
    ],

    "bull_case": [
        "US generics pricing stabilisation plus niche/complex product launches drive US revenue recovery",
        "India domestic formulations: chronic therapy penetration (diabetes, cardiac, respiratory) at a low base",
        "Complex generics (peptides, inhalers, injectables) — limited competition, materially better margins than oral solids",
        "Biosimilar pipeline optionality — long development timeline but a large market once approved",
        "Para IV first-to-file wins creating temporary exclusivity windows on high-value molecules",
    ],

    "bear_case": [
        "US FDA warning letter triggering a plant shutdown and direct revenue loss",
        "Price erosion acceleration in US base generics as competition floods a molecule",
        "R&D pipeline setbacks (CRLs, trial failures) without offsetting new approvals",
        "Domestic price-control tightening on essential/chronic-therapy medicines",
        "US channel consolidation squeezing realized pricing across the base ANDA portfolio",
    ],

    "red_flags": [
        {"condition": "ebitda_margin < 12",  "severity": "high",   "message": "EBITDA margin < 12% — well below sector norms; structural pricing or mix issues likely"},
        {"condition": "rnd_pct_revenue < 3", "severity": "medium", "message": "R&D < 3% of revenue — ANDA pipeline may not sustain growth beyond the existing base"},
        {"condition": "de_ratio > 1.0",      "severity": "medium", "message": "D/E > 1x — high leverage for a business exposed to FDA binary/regulatory risk"},
        {"condition": "revenue_growth < 5",  "severity": "medium", "message": "Revenue growth < 5% — below sector growth rate, market share at risk"},
        {"condition": "us_revenue_pct > 60", "severity": "medium", "message": "US revenue > 60% of total — high concentration; FDA compliance risk is elevated"},
    ],

    "valuation": {
        "primary":   ["P/E Ratio", "EV/EBITDA"],
        "secondary": ["EV/Sales", "P/FCF"],
        "notes": (
            "Generic formulators trade on P/E adjusted for ANDA pipeline value and US-market pricing outlook. "
            "Indian pharma mid-caps trade 18-28x P/E; large-caps with strong domestic branded franchises "
            "22-32x. Complex-generics-heavy players deserve a premium to commodity-oral-solid-heavy peers. "
            "Binary risk of a US FDA facility action justifies a discount for single-facility dependency."
        ),
        "bands": {
            "pe_ratio":  {"attractive": (0, 20), "fair": (20, 32), "expensive": (32, 999)},
            "ev_ebitda": {"attractive": (0, 12), "fair": (12, 20), "expensive": (20, 999)},
        },
    },

    "llm_context": (
        "This is a Generic Formulator — it manufactures and sells branded and generic finished-dose "
        "pharmaceutical products directly to patients/pharmacies/payers through its own sales and "
        "distribution infrastructure. Distinct from an API manufacturer (sells the ingredient itself to "
        "formulators like this one, not finished products) and from a CDMO (manufactures a client's molecule "
        "under contract rather than selling its own branded/generic portfolio). "
        "Key demand drivers: US ANDA pipeline and complex-generics mix, domestic chronic-therapy franchise "
        "growth, Para IV first-to-file opportunities. "
        "Key risks: US FDA facility action (import alert, warning letter), US base-generics price erosion, "
        "domestic NPPA price controls, channel consolidation. "
        "Assess whether growth is driven by commodity generics (low value, price-competitive) or complex/"
        "specialty generics (high value, limited competition) — this distinction matters more than the "
        "headline growth number. Do NOT apply D/E analysis the same way as industrials — pharma should be "
        "nearly debt-free."
    ),
}
