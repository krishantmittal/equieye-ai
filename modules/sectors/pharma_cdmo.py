# modules/sectors/pharma_cdmo.py
"""
CDMO / CRAMS — Sector Module
===============================
Split out from the monolithic pharma.py (see engineering_rd.py for the
precedent). CDMO/CRAMS players (Syngene International, Suven Pharma,
Cohance Lifesciences) manufacture a specific client's molecule under
contract — for the client's own drug development or commercial supply
chain — rather than selling their own branded/generic portfolio (a
formulator) or their own API catalogue (an API manufacturer). The moat
is contractual/relationship depth and regulatory track record, not
product ownership; the risk profile is dominated by client
concentration and the biotech funding cycle, not FDA action on the
company's own branded products.
"""

SECTOR_CONFIG: dict = {
    "slug": "pharma_cdmo",
    "display_name": "CDMO / CRAMS",

    "key_metrics": [
        {"id": "revenue_growth",       "label": "Revenue Growth (YoY)",      "unit": "%",  "yf_key": "revenueGrowth",   "higher_is_better": True},
        {"id": "ebitda_margin",        "label": "EBITDA Margin",             "unit": "%",  "yf_key": "ebitdaMargins",   "higher_is_better": True},
        {"id": "client_concentration", "label": "Top Client Revenue Share",  "unit": "%",  "yf_key": None,              "higher_is_better": False},
        {"id": "deal_wins_tcv",        "label": "New Deal Win TCV",          "unit": "$M", "yf_key": None,              "higher_is_better": True},
        {"id": "capacity_utilisation", "label": "Capacity Utilisation",      "unit": "%",  "yf_key": None,              "higher_is_better": True},
        {"id": "de_ratio",             "label": "Debt/Equity",               "unit": "x",  "yf_key": "debtToEquity",   "higher_is_better": False},
        {"id": "roe",                  "label": "Return on Equity",          "unit": "%",  "yf_key": "returnOnEquity", "higher_is_better": True},
    ],

    "scoring_rules": [
        {"metric": "ebitda_margin",   "op": ">", "threshold": 30.0, "points": 20, "max": 20},
        {"metric": "ebitda_margin",   "op": ">", "threshold": 22.0, "points": 12, "max": 20},
        {"metric": "ebitda_margin",   "op": ">", "threshold": 15.0, "points": 6,  "max": 20},
        {"metric": "revenue_growth",  "op": ">", "threshold": 18.0, "points": 20, "max": 20},
        {"metric": "revenue_growth",  "op": ">", "threshold": 10.0, "points": 12, "max": 20},
        {"metric": "client_concentration", "op": "<", "threshold": 20.0, "points": 15, "max": 20},
        {"metric": "de_ratio",        "op": "<", "threshold": 0.3,  "points": 15, "max": 15},
        {"metric": "roe",             "op": ">", "threshold": 15.0, "points": 10, "max": 10},
    ],
    "score_max": 100,

    "risk_factors": [
        "Client concentration: a mega-deal ending or a top client insourcing/switching supplier is a material earnings risk",
        "Biotech funding-cycle sensitivity — a VC/biotech funding downturn directly hits smaller biotech clients' order books",
        "One-time deal step-downs as a large custom-synthesis or commercial-supply contract phases out",
        "Capacity utilisation cyclicality — long lead times between capex and revenue ramp create earnings lumpiness",
        "USFDA/EU-GMP inspection risk at contract-manufacturing facilities — an adverse finding can halt a client's supply",
        "Client's own pipeline/regulatory risk passes through — a client's drug failing trials or losing approval cuts the CDMO's revenue too",
        "Currency: majority-export (USD) revenue against an INR cost base",
    ],

    "moat_factors": [
        {"factor": "Long-Term Client Relationships", "description": "Multi-year contract manufacturing/development deals, often spanning a drug's full lifecycle from development through commercial supply, create high switching costs once embedded"},
        {"factor": "Process & Technology IP",         "description": "Proprietary synthesis routes, platform technologies, and process-development expertise are difficult and slow for a client to replicate or re-source"},
        {"factor": "Regulatory Track Record",         "description": "A clean USFDA/EU-GMP inspection history at existing facilities is a prerequisite most clients audit before awarding new business — a strong track record compounds into more wins"},
        {"factor": "Integrated Service Offering",     "description": "End-to-end capability (development through commercial-scale manufacturing) lets a CDMO capture more of a client's outsourced spend than a single-stage player"},
        {"factor": "Design-Cycle Switching Costs",    "description": "Once a CDMO is qualified into a client's regulatory filing for a specific molecule, switching manufacturers requires re-validation and re-filing — a structurally high switching cost"},
    ],

    "bull_case": [
        "China+1 outsourcing shift as global biopharma diversifies contract manufacturing away from Chinese CDMOs",
        "Biotech funding recovery reactivating smaller clients' development pipelines and order books",
        "Large pharma increasingly outsourcing complex/specialty manufacturing rather than building in-house capacity",
        "New mega-deal wins with multi-year revenue visibility once a molecule reaches commercial-scale supply",
        "Platform technology (e.g. novel synthesis routes, biologics capability) attracting premium-priced, differentiated work",
    ],

    "bear_case": [
        "Loss of a top client or a mega-deal step-down as a commercial contract phases out or client insources",
        "Biotech funding-cycle downturn shrinking order books from smaller, cash-constrained clients",
        "New capacity ramping slower than planned, pressuring utilisation and near-term margins",
        "A client's own drug failing trials or losing regulatory approval directly cuts CDMO revenue tied to it",
        "USFDA/EU-GMP inspection finding at a key facility disrupting a client's supply and damaging the CDMO's track record",
    ],

    "red_flags": [
        {"condition": "client_concentration > 30", "severity": "high",   "message": "Top client > 30% of revenue — a single client loss or contract step-down is a material earnings risk"},
        {"condition": "ebitda_margin < 15",        "severity": "high",   "message": "EBITDA margin < 15% — weak for a CDMO business; suggests commoditized/low-value contract mix"},
        {"condition": "revenue_growth < 5",        "severity": "medium", "message": "Revenue growth < 5% — deal pipeline may be slowing or utilisation dropping"},
        {"condition": "capacity_utilisation < 60", "severity": "medium", "message": "Capacity utilisation < 60% — new capex may be ramping slower than planned"},
    ],

    "valuation": {
        "primary":   ["EV/EBITDA", "P/E Ratio"],
        "secondary": ["EV/Sales", "P/FCF"],
        "notes": (
            "CDMOs command a premium to both API manufacturers and generic formulators, reflecting recurring, "
            "relationship-locked revenue and typically higher margins — but the premium should be discounted "
            "for client concentration. A CDMO with one or two clients driving the bulk of revenue deserves a "
            "meaningfully lower multiple than a diversified one, regardless of current margin quality."
        ),
        "bands": {
            "pe_ratio":  {"attractive": (0, 25), "fair": (25, 40), "expensive": (40, 999)},
            "ev_ebitda": {"attractive": (0, 15), "fair": (15, 24), "expensive": (24, 999)},
        },
    },

    "llm_context": (
        "This is a CDMO / CRAMS (Contract Development and Manufacturing Organisation) — it manufactures a "
        "specific client's molecule under contract, for that client's own drug development or commercial "
        "supply chain, rather than selling its own branded/generic portfolio (a formulator) or its own API "
        "catalogue (an API manufacturer). "
        "Key demand drivers: China+1 outsourcing shift, biotech funding-cycle recovery, large pharma "
        "increasingly outsourcing complex manufacturing, platform-technology differentiation. "
        "Key risks: client concentration (a handful of large clients or even a single mega-deal), biotech "
        "funding-cycle sensitivity for smaller clients, capacity-utilisation cyclicality, and pass-through risk "
        "from a client's own pipeline/regulatory setbacks. "
        "Assess client concentration and deal-pipeline visibility as carefully as margin — a high-margin CDMO "
        "overly dependent on one client is riskier than a lower-margin, diversified one. "
        "Do NOT apply D/E or NPA analysis the same way as industrials — this is typically a nearly debt-free, "
        "cash-generative business."
    ),
}
