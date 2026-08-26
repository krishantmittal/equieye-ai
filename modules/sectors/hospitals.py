# modules/sectors/hospitals.py
"""
Hospitals & Healthcare Delivery — Sector Module
==================================================
Not previously a distinct sector at all — hospital operators (Apollo
Hospitals, Fortis Healthcare, Max Healthcare, Narayana Health, Aster
DM, Global Health/Medanta) were falling through to the generic catch-
all sector entirely (no pharma/drug/biotech keyword match). This is a
capital-intensive, long-gestation real-estate-and-services business —
bed capacity, specialist doctor relationships, and occupancy economics
drive the model, not manufacturing, R&D, or drug-regulatory risk.
Structurally the most distinct of all the healthcare sub-sectors from
core pharma.
"""

SECTOR_CONFIG: dict = {
    "slug": "hospitals",
    "display_name": "Hospitals & Healthcare Delivery",

    "key_metrics": [
        {"id": "revenue_growth",     "label": "Revenue Growth (YoY)",       "unit": "%",  "yf_key": "revenueGrowth",   "higher_is_better": True},
        {"id": "ebitda_margin",      "label": "EBITDA Margin",              "unit": "%",  "yf_key": "ebitdaMargins",   "higher_is_better": True},
        {"id": "occupancy_rate",     "label": "Bed Occupancy Rate",         "unit": "%",  "yf_key": None,              "higher_is_better": True},
        {"id": "arpob",              "label": "ARPOB (Revenue/Occupied Bed/Day)", "unit": "₹","yf_key": None,         "higher_is_better": True},
        {"id": "mature_bed_pct",     "label": "Mature (Non-Ramping) Bed Share", "unit": "%", "yf_key": None,          "higher_is_better": True},
        {"id": "de_ratio",           "label": "Debt/Equity",                "unit": "x",  "yf_key": "debtToEquity",   "higher_is_better": False},
        {"id": "roe",                "label": "Return on Equity",           "unit": "%",  "yf_key": "returnOnEquity", "higher_is_better": True},
    ],

    "scoring_rules": [
        {"metric": "ebitda_margin",   "op": ">", "threshold": 22.0, "points": 20, "max": 20},
        {"metric": "ebitda_margin",   "op": ">", "threshold": 15.0, "points": 12, "max": 20},
        {"metric": "occupancy_rate",  "op": ">", "threshold": 70.0, "points": 20, "max": 20},
        {"metric": "occupancy_rate",  "op": ">", "threshold": 55.0, "points": 12, "max": 20},
        {"metric": "revenue_growth",  "op": ">", "threshold": 12.0, "points": 15, "max": 15},
        {"metric": "de_ratio",        "op": "<", "threshold": 0.7,  "points": 15, "max": 15},
        {"metric": "roe",             "op": ">", "threshold": 15.0, "points": 10, "max": 10},
    ],
    "score_max": 100,

    "risk_factors": [
        "New hospital capex is capital-intensive with a long gestation period (often 5-7 years) before a facility matures to peak occupancy",
        "Regulatory price caps on specific procedures/devices (e.g. NPPA caps on stents, knee implants) directly compress high-margin procedure revenue",
        "Insurance/TPA reimbursement delays and rate negotiations affect realized pricing and working capital",
        "Specialist doctor attrition or a key-doctor departure can materially impact a specific department's revenue and reputation",
        "Occupancy cyclicality — a new capacity addition (own or competitor's) in the same micro-market can pressure near-term occupancy",
        "Regulatory/compliance risk (clinical establishment norms, biomedical waste, fire safety) can disrupt operations at a facility",
    ],

    "moat_factors": [
        {"factor": "Bed Capacity in High-Demand Metros", "description": "Land and regulatory approval for hospital capacity in dense urban markets is scarce and slow to replicate — an incumbent's existing footprint is a genuine barrier to entry"},
        {"factor": "Specialist Doctor Network",           "description": "Reputation-driven relationships with leading specialists (often built over years) are difficult for a new hospital to poach or replicate quickly"},
        {"factor": "Brand Trust for Complex Procedures",  "description": "Patients default to a trusted brand for high-stakes, complex procedures (cardiac, oncology, transplants) — trust that compounds with clinical outcomes track record"},
        {"factor": "Insurance Network Empanelment",       "description": "Empanelment with major insurers/TPAs at favorable rates is a relationship built over years, gating new-entrant access to insured patient volume"},
        {"factor": "Scale Economics in Diagnostics/Pharmacy", "description": "In-house diagnostics and pharmacy at scale improve margins and patient convenience versus a standalone facility"},
    ],

    "bull_case": [
        "Under-penetrated healthcare infrastructure in India (low beds per 1000 population) — structural multi-year demand runway",
        "Occupancy ramp-up at recently-added (immature) capacity driving margin expansion as beds mature without proportionate new capex",
        "Rising complex/high-acuity procedure mix (oncology, transplants, robotic surgery) improving ARPOB and margins",
        "Health insurance penetration growth expanding the addressable, ability-to-pay patient base",
        "Medical tourism and international patient volume adding a higher-margin revenue stream",
    ],

    "bear_case": [
        "New capacity (own or competitor's) in the same micro-market taking years to reach mature occupancy, pressuring near-term margins",
        "Regulatory price caps on high-margin procedures or devices directly compressing profitability",
        "Key specialist doctor(s) departing to a competitor, impacting a specific high-value department",
        "Insurance/TPA reimbursement rate pressure or payment delays affecting realized pricing and cash flow",
        "Capex overrun or slower-than-planned ramp on a new hospital project delaying expected returns",
    ],

    "red_flags": [
        {"condition": "occupancy_rate < 50",   "severity": "high",   "message": "Occupancy rate < 50% — capacity is significantly under-utilised, a major margin drag"},
        {"condition": "ebitda_margin < 12",    "severity": "high",   "message": "EBITDA margin < 12% — weak for a hospital business at any reasonable scale/occupancy"},
        {"condition": "de_ratio > 1.2",        "severity": "medium", "message": "D/E > 1.2x — high leverage for a business with long-gestation capex and occupancy-cycle risk"},
        {"condition": "revenue_growth < 5",    "severity": "medium", "message": "Revenue growth < 5% — below sector growth rate; occupancy or ARPOB may be stagnating"},
    ],

    "valuation": {
        "primary":   ["EV/EBITDA", "P/E Ratio"],
        "secondary": ["EV/Bed", "P/FCF"],
        "notes": (
            "Hospitals are valued partly on current earnings and partly on embedded optionality in immature "
            "(recently-added, not-yet-peak-occupancy) bed capacity — a hospital chain with a large share of "
            "young, ramping beds can justify a higher multiple than trailing EBITDA alone suggests, provided "
            "the ramp is genuinely on track. EV/Bed is a useful cross-check against pure earnings multiples "
            "for capacity still maturing."
        ),
        "bands": {
            "pe_ratio":  {"attractive": (0, 30), "fair": (30, 50), "expensive": (50, 999)},
            "ev_ebitda": {"attractive": (0, 16), "fair": (16, 26), "expensive": (26, 999)},
        },
    },

    "llm_context": (
        "This is a Hospital / Healthcare Delivery operator running hospital facilities for inpatient and "
        "outpatient care. It's a capital-intensive, long-gestation real-estate-and-services business, NOT a "
        "pharma manufacturer — no manufacturing, R&D pipeline, FDA/USFDA exposure, or API/formulation risk; "
        "don't apply pharma manufacturing framing (ANDA pipeline, FDA import alerts, API supply chain). "
        "Key demand drivers: under-penetrated healthcare infrastructure (low beds per capita), occupancy "
        "ramp-up at immature capacity, rising complex/high-acuity procedure mix, insurance penetration "
        "growth. Key risks: long capex-to-maturity gestation, regulatory price caps on procedures/devices, "
        "specialist doctor attrition, insurance/TPA reimbursement pressure. "
        "Distinguish mature (stabilized-occupancy) beds from recently-added, still-ramping capacity when "
        "assessing margins — a chain adding new beds shows temporarily depressed consolidated margins even "
        "if the mature business is healthy. "
        "D/E can run moderately higher here than in asset-light healthcare sub-sectors given hospital "
        "construction's capital intensity — assess leverage against the capex cycle stage, not a flat "
        "near-zero-debt expectation."
    ),
}
