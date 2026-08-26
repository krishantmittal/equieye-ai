# modules/sectors/cement.py
"""
Cement / Building Materials — Sector Module
"""

SECTOR_CONFIG: dict = {
    "slug": "cement",
    "display_name": "Cement",

    "key_metrics": [
        {"id": "capacity_mtpa",     "label": "Installed Capacity",     "unit": "MTPA", "yf_key": None, "higher_is_better": True},
        {"id": "capacity_util",     "label": "Capacity Utilisation",   "unit": "%",    "yf_key": None, "higher_is_better": True},
        {"id": "realisation_per_tonne", "label": "Realisation / Tonne", "unit": "₹",   "yf_key": None, "higher_is_better": True},
        {"id": "ebitda_per_tonne",  "label": "EBITDA / Tonne",         "unit": "₹",    "yf_key": None, "higher_is_better": True},
        {"id": "ebitda_margin",     "label": "EBITDA Margin",          "unit": "%",    "yf_key": "ebitdaMargins", "higher_is_better": True},
    ],

    "risk_factors": [
        "Highly cyclical — demand tied to construction, infrastructure, and housing activity",
        "Regional oversupply can trigger price wars, compressing realisations",
        "Input cost volatility (coal/petcoke for kiln fuel, freight) squeezing margins",
        "Capital intensive — capacity expansion requires large, long-payback capex",
        "Freight costs limit economic radius — regional demand-supply mismatches persist",
        "Regulatory/environmental compliance costs (emissions norms) rising over time",
    ],

    "moat_factors": [
        {"factor": "Regional Market Leadership", "description": "Dominant share in a region reduces freight-cost disadvantage versus distant competitors"},
        {"factor": "Cost Leadership",             "description": "Captive power/fuel linkages and scale lower per-tonne production cost"},
        {"factor": "Distribution Network",        "description": "Dense dealer network is expensive and slow for new entrants to replicate"},
        {"factor": "Brand",                       "description": "Retail (non-trade) cement buyers pay a premium for a trusted brand"},
        {"factor": "Logistics / Location",        "description": "Plants located near limestone reserves and demand centres lower transport cost"},
    ],

    "bull_case": [
        "Infrastructure and housing capex cycle driving volume growth",
        "Consolidation reducing regional oversupply and improving pricing discipline",
        "Cost efficiency gains from captive power, waste heat recovery, and green fuel substitution",
        "Premiumisation (branded, blended cement) improving realisation and margin mix",
        "Capacity expansion ahead of demand positioning for market share gains",
    ],

    "bear_case": [
        "Regional oversupply triggering aggressive price competition",
        "Fuel cost spikes (coal, petcoke) compressing EBITDA/tonne",
        "Weak monsoon or construction slowdown denting volume growth",
        "Large debt-funded capacity expansion straining the balance sheet",
        "Government infrastructure spending slowdown ahead of elections",
    ],

    "red_flags": [
        {"condition": "de_ratio > 1.0",     "severity": "high",   "message": "D/E > 1.0x — high leverage for a cyclical, capital-intensive business"},
        {"condition": "ebitda_margin < 15", "severity": "medium", "message": "EBITDA margin < 15% — weak profitability versus typical cement sector economics"},
    ],

    "valuation": {
        "primary":   ["EV/EBITDA", "EV per tonne of capacity"],
        "secondary": ["P/E"],
        "notes": (
            "Cement is best valued on EV/EBITDA and EV-per-tonne-of-capacity, since P/E can be distorted by "
            "the heavy depreciation of capital-intensive plants. Compare EV/tonne against the replacement "
            "cost of building new capacity to judge if the market is over- or under-pricing existing assets."
        ),
        "bands": {
            "ev_ebitda": {"attractive": (0, 9), "fair": (9, 14), "expensive": (14, 999)},
        },
    },

    "llm_context": (
        "This is a CEMENT / BUILDING MATERIALS company. Focus on: capacity utilisation, regional market "
        "share and pricing power, EBITDA per tonne, fuel cost exposure (coal/petcoke), and the balance "
        "between debt-funded capacity expansion and cash generation. Cement economics are intensely regional "
        "— a company can be dominant in one state and irrelevant in another, so avoid treating 'market "
        "leadership' as a single national figure."
    ),
}
