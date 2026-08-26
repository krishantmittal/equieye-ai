# modules/sectors/oil_gas.py
"""
Oil & Gas (Upstream / Downstream / OMCs) — Sector Module
"""

SECTOR_CONFIG: dict = {
    "slug": "oil_gas",
    "display_name": "Oil & Gas",

    "key_metrics": [
        {"id": "gross_refining_margin", "label": "Gross Refining Margin (GRM)", "unit": "$/bbl", "yf_key": None, "higher_is_better": True},
        {"id": "reserves_replacement",  "label": "Reserves Replacement Ratio",  "unit": "x",      "yf_key": None, "higher_is_better": True},
        {"id": "capacity_util",         "label": "Refinery Capacity Utilisation", "unit": "%",    "yf_key": None, "higher_is_better": True},
        {"id": "ebitda_margin",         "label": "EBITDA Margin",               "unit": "%",      "yf_key": "ebitdaMargins", "higher_is_better": True},
        {"id": "net_debt_to_ebitda",    "label": "Net Debt / EBITDA",           "unit": "x",      "yf_key": None, "higher_is_better": False},
    ],

    "risk_factors": [
        "Crude oil price volatility directly impacts upstream realisations and downstream input costs",
        "Government price/subsidy policy risk for OMCs (fuel pricing, LPG subsidy burden)",
        "Currency risk — crude is priced/imported in USD, INR depreciation raises costs",
        "Capital intensive — refining/exploration capex has very long payback periods",
        "Energy transition risk — long-term demand uncertainty as EVs and renewables scale",
        "Geopolitical risk affecting crude supply and pricing (OPEC decisions, regional conflicts)",
    ],

    "moat_factors": [
        {"factor": "Refining Complexity",  "description": "Complex refineries can process cheaper, heavier crude grades at better margins"},
        {"factor": "Retail Network",        "description": "Extensive fuel retail network (for OMCs) is a major barrier to new entrants"},
        {"factor": "Reserves Quality",      "description": "Low-cost, long-life reserves support durable upstream profitability through cycles"},
        {"factor": "Integration",           "description": "Upstream-downstream integration smooths earnings across the commodity cycle"},
        {"factor": "Scale",                 "description": "Scale lowers per-unit operating costs versus smaller regional players"},
    ],

    "bull_case": [
        "Rising refining margins (GRMs) on strong product demand-supply dynamics",
        "New discoveries or reserve additions extending upstream production life",
        "Government fuel pricing reforms improving OMC marketing margins",
        "Petrochemical/downstream diversification adding higher-margin revenue streams",
        "Capacity expansion capturing growing domestic fuel/petrochemical demand",
    ],

    "bear_case": [
        "Crude price spikes compressing refining and marketing margins",
        "Government price controls limiting pass-through of higher input costs (OMCs)",
        "Weak refining margins during oversupply in regional product markets",
        "Currency depreciation raising the cost of USD-denominated crude imports",
        "Long-term demand risk from accelerating energy transition to EVs/renewables",
    ],

    "red_flags": [
        {"condition": "de_ratio > 1.2",         "severity": "high",   "message": "D/E > 1.2x — high leverage for a highly cyclical, capital-intensive business"},
        {"condition": "net_debt_to_ebitda > 3",  "severity": "high",   "message": "Net Debt/EBITDA > 3x — elevated leverage relative to cash-generating capacity"},
    ],

    "valuation": {
        "primary":   ["EV/EBITDA"],
        "secondary": ["P/E", "P/B"],
        "notes": (
            "Oil & gas companies are best valued on EV/EBITDA due to heavy depreciation and cyclical "
            "earnings — P/E can be misleading at cycle peaks/troughs. Cross-check against P/B for "
            "asset-heavy upstream players."
        ),
        "bands": {
            "ev_ebitda": {"attractive": (0, 6), "fair": (6, 10), "expensive": (10, 999)},
        },
    },

    "llm_context": (
        "This is an OIL & GAS company (upstream exploration, downstream refining, or an oil marketing "
        "company/OMC). Distinguish clearly between these sub-segments since their economics differ "
        "substantially: upstream is driven by reserves and crude price realisation, refining by GRMs and "
        "capacity utilisation, and OMCs by government fuel-pricing policy and marketing margins. Flag "
        "government price-control risk explicitly for any OMC."
    ),
}
