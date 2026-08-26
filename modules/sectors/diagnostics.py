# modules/sectors/diagnostics.py
"""
Diagnostics & Pathology — Sector Module
==========================================
Not previously a distinct sector at all — diagnostics/pathology
companies (Dr. Lal PathLabs, Metropolis Healthcare, Thyrocare, Vijaya
Diagnostic, Krsnaa Diagnostics) were falling through to the generic
catch-all sector entirely (no pharma/drug/biotech keyword match), so
they got zero sector-specific moat/risk/bull/bear content. This is a
lab-services and collection-network business — brand trust, test menu
breadth, and hub-and-spoke network density drive the economics, not
manufacturing, R&D pipelines, or FDA regulatory risk. Structurally
distinct from every pharma sub-sector, not merely a variant of one.
"""

SECTOR_CONFIG: dict = {
    "slug": "diagnostics",
    "display_name": "Diagnostics & Pathology",

    "key_metrics": [
        {"id": "revenue_growth",       "label": "Revenue Growth (YoY)",       "unit": "%",  "yf_key": "revenueGrowth",   "higher_is_better": True},
        {"id": "ebitda_margin",        "label": "EBITDA Margin",              "unit": "%",  "yf_key": "ebitdaMargins",   "higher_is_better": True},
        {"id": "test_volume_growth",   "label": "Test Volume Growth",         "unit": "%",  "yf_key": None,              "higher_is_better": True},
        {"id": "non_covid_growth",     "label": "Non-COVID Revenue Growth",   "unit": "%",  "yf_key": None,              "higher_is_better": True},
        {"id": "network_centers",      "label": "Collection Centers (#)",     "unit": "#",  "yf_key": None,              "higher_is_better": True},
        {"id": "de_ratio",             "label": "Debt/Equity",                "unit": "x",  "yf_key": "debtToEquity",   "higher_is_better": False},
        {"id": "roe",                  "label": "Return on Equity",           "unit": "%",  "yf_key": "returnOnEquity", "higher_is_better": True},
    ],

    "scoring_rules": [
        {"metric": "ebitda_margin",     "op": ">", "threshold": 26.0, "points": 20, "max": 20},
        {"metric": "ebitda_margin",     "op": ">", "threshold": 18.0, "points": 12, "max": 20},
        {"metric": "non_covid_growth",  "op": ">", "threshold": 15.0, "points": 20, "max": 20},
        {"metric": "non_covid_growth",  "op": ">", "threshold": 8.0,  "points": 12, "max": 20},
        {"metric": "test_volume_growth","op": ">", "threshold": 12.0, "points": 15, "max": 15},
        {"metric": "de_ratio",          "op": "<", "threshold": 0.3,  "points": 15, "max": 15},
        {"metric": "roe",               "op": ">", "threshold": 20.0, "points": 10, "max": 10},
    ],
    "score_max": 100,

    "risk_factors": [
        "COVID-linked high base effect — many diagnostics companies had inflated 2020-22 revenue from COVID testing that doesn't repeat",
        "Price competition from aggregator/online platforms and hyperlocal lab-testing apps compressing realized pricing",
        "Franchisee/collection-center quality-control risk — brand reputation depends on consistent service across a network the company doesn't fully own",
        "Reimbursement/insurance-panel dependency for a growing share of test volumes",
        "Regulatory risk on test pricing or mandatory price caps in certain states",
        "New capacity (labs, collection centers) requires time to ramp utilisation — near-term margin drag on expansion",
    ],

    "moat_factors": [
        {"factor": "Brand Trust",              "description": "Patients and physicians default to a trusted brand for diagnostic accuracy — a genuine trust moat that's slow to build and slow to erode, but also slow for a new entrant to overcome"},
        {"factor": "Collection Network Density", "description": "A dense hub-and-spoke network of collection centers/phlebotomists creates convenience and turnaround-time advantages that are capital- and time-intensive for a competitor to replicate"},
        {"factor": "Test Menu Breadth",         "description": "A wide, specialized test menu (including complex/reference tests) captures higher-value referrals that a narrow-menu competitor can't service"},
        {"factor": "Lab Accreditation",         "description": "NABL/CAP accreditation and consistent quality track record are prerequisites for physician and hospital referral relationships"},
        {"factor": "Operating Leverage at Scale", "description": "Centralized reference labs spread fixed costs (equipment, specialists) across growing volume, improving margins as scale increases"},
    ],

    "bull_case": [
        "Organized-sector penetration of India's still-fragmented diagnostics market — structural share gain from unorganized local labs",
        "Preventive-health and wellness-package adoption growing test volumes per patient beyond illness-driven testing",
        "Specialized/high-value test mix shift (genomics, oncology panels) improving realization per sample",
        "Network expansion into underserved tier-2/tier-3 cities extending the addressable market",
        "B2B/hospital and corporate wellness partnerships adding a steadier, less price-competitive volume stream",
    ],

    "bear_case": [
        "COVID-testing high base unwinding, making YoY growth comparisons look weaker than underlying core-business trends",
        "Aggregator/online platforms undercutting on price for commoditized routine tests",
        "Franchisee quality lapse damaging brand trust across the broader network, not just the affected center",
        "Reimbursement panel pricing pressure from insurers/TPAs as their bargaining leverage grows",
        "New lab/network capex ramping slower than planned, pressuring near-term margins",
    ],

    "red_flags": [
        {"condition": "non_covid_growth < 5",    "severity": "high",   "message": "Non-COVID revenue growth < 5% — core testing business growth may be weaker than headline numbers suggest"},
        {"condition": "ebitda_margin < 15",      "severity": "medium", "message": "EBITDA margin < 15% — weak for an asset-light diagnostics business at scale"},
        {"condition": "test_volume_growth < 5",  "severity": "medium", "message": "Test volume growth < 5% — revenue growth may be pricing-driven rather than volume-driven, a less durable growth source"},
        {"condition": "de_ratio > 0.6",          "severity": "medium", "message": "D/E > 0.6x — elevated leverage for a typically asset-light, cash-generative business model"},
    ],

    "valuation": {
        "primary":   ["P/E Ratio", "EV/EBITDA"],
        "secondary": ["EV/Sales", "P/FCF"],
        "notes": (
            "Diagnostics companies trade at a premium to pharma manufacturing peers, reflecting an asset-"
            "light, high-margin, high-ROE business model — but the COVID-era testing boom inflated both "
            "earnings and multiples industry-wide, so valuation should be assessed against normalized, "
            "non-COVID core-business growth rather than headline post-2020 figures."
        ),
        "bands": {
            "pe_ratio":  {"attractive": (0, 30), "fair": (30, 50), "expensive": (50, 999)},
            "ev_ebitda": {"attractive": (0, 18), "fair": (18, 28), "expensive": (28, 999)},
        },
    },

    "llm_context": (
        "This is a Diagnostics & Pathology company — it operates diagnostic laboratories and a collection-"
        "center network, providing lab testing services to patients and physicians. This is a lab-services "
        "and network-density business, NOT a pharma manufacturer — it has no manufacturing, no R&D drug "
        "pipeline, no FDA/USFDA regulatory exposure, and no API/formulation risk. Do not apply pharma "
        "manufacturing framing (ANDA pipeline, FDA import alerts, API supply chain) to this company. "
        "Key demand drivers: organized-sector penetration of a still-fragmented market, preventive-health/"
        "wellness test adoption, specialized/high-value test mix shift, network expansion into underserved "
        "cities. "
        "Key risks: COVID-testing high base effect distorting YoY comparisons, aggregator/online price "
        "competition, franchisee quality-control risk, reimbursement panel pricing pressure. "
        "Distinguish core (non-COVID) testing growth from pandemic-era volume when assessing the growth "
        "trend — headline YoY numbers spanning 2020-2022 can be misleading either direction. "
        "Do NOT apply D/E analysis the same way as capital-intensive industrials — this is typically an "
        "asset-light, high-ROE, low-leverage business."
    ),
}
