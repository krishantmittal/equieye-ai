# modules/sectors/pharma_api.py
"""
API / Bulk Drug Manufacturers — Sector Module
================================================
Split out from the monolithic pharma.py (see engineering_rd.py for the
precedent). API/bulk-drug manufacturers (Divi's Laboratories, Laurus
Labs, Granules India, Aarti Drugs, Neuland Laboratories) sell the active
pharmaceutical ingredient itself — a cost-leadership, scale, and
regulatory-filing (DMF) business — to formulators, not branded/generic
finished-dose products to patients or payers. Distinct moat, distinct
customer base (other pharma companies, not patients/pharmacies),
distinct risk profile (China API price competition, single-molecule
customer concentration) from a generic formulator like Sun Pharma or a
CDMO like Syngene.
"""

SECTOR_CONFIG: dict = {
    "slug": "pharma_api",
    "display_name": "API / Bulk Drug Manufacturers",

    "key_metrics": [
        {"id": "revenue_growth",     "label": "Revenue Growth (YoY)",     "unit": "%",  "yf_key": "revenueGrowth",   "higher_is_better": True},
        {"id": "ebitda_margin",      "label": "EBITDA Margin",            "unit": "%",  "yf_key": "ebitdaMargins",   "higher_is_better": True},
        {"id": "customer_concentration", "label": "Top-3 Customer Revenue Share", "unit": "%", "yf_key": None,      "higher_is_better": False},
        {"id": "dmf_filings",        "label": "Active DMF/CEP Filings (#)","unit": "#",  "yf_key": None,             "higher_is_better": True},
        {"id": "backward_integration_pct", "label": "Backward-Integrated Revenue", "unit": "%", "yf_key": None,     "higher_is_better": True},
        {"id": "de_ratio",           "label": "Debt/Equity",              "unit": "x",  "yf_key": "debtToEquity",   "higher_is_better": False},
        {"id": "roe",                "label": "Return on Equity",         "unit": "%",  "yf_key": "returnOnEquity", "higher_is_better": True},
    ],

    "scoring_rules": [
        {"metric": "ebitda_margin",   "op": ">", "threshold": 24.0, "points": 20, "max": 20},
        {"metric": "ebitda_margin",   "op": ">", "threshold": 18.0, "points": 12, "max": 20},
        {"metric": "ebitda_margin",   "op": ">", "threshold": 12.0, "points": 6,  "max": 20},
        {"metric": "revenue_growth",  "op": ">", "threshold": 15.0, "points": 20, "max": 20},
        {"metric": "revenue_growth",  "op": ">", "threshold": 8.0,  "points": 12, "max": 20},
        {"metric": "customer_concentration", "op": "<", "threshold": 25.0, "points": 15, "max": 20},
        {"metric": "de_ratio",        "op": "<", "threshold": 0.4,  "points": 15, "max": 15},
        {"metric": "de_ratio",        "op": "<", "threshold": 0.8,  "points": 8,  "max": 15},
        {"metric": "roe",             "op": ">", "threshold": 18.0, "points": 10, "max": 10},
    ],
    "score_max": 100,

    "risk_factors": [
        "China API price competition — Chinese manufacturers can undercut on commodity/high-volume molecules",
        "Single-molecule or single-customer concentration: loss of a top formulator client is a material earnings risk",
        "Environmental/pollution norms tightening (effluent treatment, CPCB action) can force capacity shutdowns",
        "PLI scheme dependency — India's API-localization push is a tailwind but also a policy-continuity risk",
        "US FDA/EU GMP inspection risk at bulk-drug facilities — an import alert halts export revenue directly",
        "Commoditization risk on off-patent, high-volume molecules where many producers compete purely on cost",
        "Currency: majority-export (USD/EUR) revenue against an INR cost base",
    ],

    "moat_factors": [
        {"factor": "Regulatory Filing Portfolio",  "description": "Active DMF/CEP filings across multiple regulated markets (US, EU, Japan) are a multi-year, capital-intensive barrier new entrants must replicate molecule-by-molecule"},
        {"factor": "Manufacturing Scale & Cost Leadership", "description": "Large-scale, backward-integrated plants achieve per-unit cost advantages smaller API makers can't match"},
        {"factor": "Complex Molecule Expertise",   "description": "High-potency APIs, peptides, and complex synthesis chemistry command better pricing and face far less competition than commodity APIs"},
        {"factor": "Backward Integration",         "description": "In-house key-starting-material and intermediate production insulates margins from upstream (often China-sourced) input price swings"},
        {"factor": "Regulatory Track Record",      "description": "A clean USFDA/EU-GMP inspection history at existing facilities lowers the bar for approving new capacity/molecules"},
    ],

    "bull_case": [
        "China+1 API sourcing shift as global formulators diversify supply chains away from Chinese dependency",
        "PLI-scheme-driven capacity expansion into critical starting materials and high-value APIs",
        "Complex/high-potency API mix shift (peptides, oncology APIs) — structurally better margins than commodity APIs",
        "New molecule DMF filings opening access to new regulated-market customers and revenue streams",
        "Custom synthesis/CDMO crossover — API scale players increasingly winning contract manufacturing deals too",
    ],

    "bear_case": [
        "Chinese API price undercutting on commodity, high-volume molecules compresses margins industry-wide",
        "Loss of a top-3 customer (a major formulator switching supplier) is a direct, hard-to-replace revenue hit",
        "Environmental/pollution-control action forcing a plant shutdown or capacity curtailment",
        "USFDA import alert or warning letter at a key facility halting regulated-market exports",
        "Capex-heavy new capacity ramping slower than planned, pressuring near-term return ratios",
    ],

    "red_flags": [
        {"condition": "ebitda_margin < 12",       "severity": "high",   "message": "EBITDA margin < 12% — weak for an API business; suggests commoditized molecule mix or pricing pressure"},
        {"condition": "customer_concentration > 40", "severity": "high", "message": "Top-3 customers > 40% of revenue — a single customer loss is a material earnings risk"},
        {"condition": "revenue_growth < 3",       "severity": "medium", "message": "Revenue growth < 3% — DMF pipeline may not be converting into new regulated-market business"},
        {"condition": "de_ratio > 1.0",           "severity": "medium", "message": "D/E > 1x — high leverage for a business with China-competition and single-customer binary risks"},
    ],

    "valuation": {
        "primary":   ["P/E Ratio", "EV/EBITDA"],
        "secondary": ["EV/Sales", "P/FCF"],
        "notes": (
            "API manufacturers trade at a discount to generic formulators and a larger discount to CDMOs, "
            "reflecting lower pricing power and higher commoditization risk on the bulk-molecule end of the "
            "business. Complex/high-potency API mix and backward integration justify a premium within the "
            "sub-sector. Indian API players typically trade 15-25x P/E; commodity-heavy names trade below that."
        ),
        "bands": {
            "pe_ratio":  {"attractive": (0, 15), "fair": (15, 28), "expensive": (28, 999)},
            "ev_ebitda": {"attractive": (0, 10), "fair": (10, 16), "expensive": (16, 999)},
        },
    },

    "llm_context": (
        "This is an API / Bulk Drug Manufacturer — it sells the active pharmaceutical ingredient itself to "
        "other pharma companies (formulators), not branded or generic finished-dose products to patients or "
        "payers. Distinct from a generic formulator (Sun Pharma, Cipla) which sells finished products through "
        "its own sales force, and from a CDMO (Syngene, Suven) which manufactures a specific client's molecule "
        "under contract rather than selling its own API portfolio. "
        "Key demand drivers: China+1 API sourcing diversification, PLI-scheme capacity expansion, complex/"
        "high-potency molecule mix shift. "
        "Key risks: Chinese price competition on commodity molecules, customer concentration (a handful of "
        "large formulators), environmental/pollution-control action, USFDA inspection risk at bulk-drug "
        "facilities. "
        "Assess whether growth and margin come from commodity, high-volume molecules (low value, price-"
        "competitive) or complex/high-potency APIs with DMF-filing barriers (high value, limited competition). "
        "D/E should stay low — this is typically a cash-generative, low-leverage business."
    ),
}
