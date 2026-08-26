# modules/sectors/logistics.py
"""
Logistics / Freight / Supply Chain — Sector Module
"""

SECTOR_CONFIG: dict = {
    "slug": "logistics",
    "display_name": "Logistics",

    "key_metrics": [
        {"id": "network_reach",     "label": "Network Reach (cities/routes)", "unit": "count", "yf_key": None, "higher_is_better": True},
        {"id": "asset_turnover",    "label": "Asset Turnover",          "unit": "x",  "yf_key": None, "higher_is_better": True},
        {"id": "fuel_cost_pass_through", "label": "Fuel Cost Pass-Through", "unit": "%", "yf_key": None, "higher_is_better": True},
        {"id": "ebitda_margin",     "label": "EBITDA Margin",           "unit": "%",  "yf_key": "ebitdaMargins", "higher_is_better": True},
        {"id": "revenue_growth",    "label": "Revenue Growth",          "unit": "%",  "yf_key": None, "higher_is_better": True},
    ],

    "risk_factors": [
        "Fuel price volatility directly impacts cost structure (diesel for surface transport)",
        "Asset-heavy models (own fleet) carry high capex and maintenance burden",
        "E-commerce/quick-commerce growth is a double-edged sword — volume driver but margin-thin",
        "Intense price competition on commoditised freight lanes",
        "Regulatory/infrastructure dependency (highways, ports, rail capacity)",
        "Working capital strain from extended receivable cycles with large corporate clients",
    ],

    "moat_factors": [
        {"factor": "Network Density",      "description": "Dense pickup/delivery network is capital-intensive and slow for new entrants to replicate"},
        {"factor": "Technology / Tracking", "description": "Real-time tracking and route optimisation improve efficiency and customer stickiness"},
        {"factor": "Asset-Light Model",     "description": "Asset-light (contracted fleet) models scale faster with lower capital intensity"},
        {"factor": "Customer Contracts",    "description": "Long-term contracts with large e-commerce/enterprise clients provide revenue visibility"},
        {"factor": "Multi-Modal Capability", "description": "Ability to combine road/rail/air/warehousing wins larger, stickier enterprise contracts"},
    ],

    "bull_case": [
        "E-commerce and quick-commerce growth structurally expanding parcel volumes",
        "Formalisation of logistics (GST, e-way bill) favouring organised players over unorganised competition",
        "Network expansion into tier-2/3 cities capturing underserved demand",
        "Operating leverage as fixed network costs are spread over growing volumes",
        "Multi-modal / warehousing expansion increasing wallet share per customer",
    ],

    "bear_case": [
        "Fuel cost spikes compressing thin freight margins",
        "Intensifying price competition from unorganised players and new entrants",
        "Client concentration risk if a large e-commerce customer shifts volumes in-house",
        "Working capital strain from delayed payments by large corporate clients",
        "Economic slowdown reducing overall freight and parcel volumes",
    ],

    "red_flags": [
        {"condition": "de_ratio > 1.2",     "severity": "high",   "message": "D/E > 1.2x — high leverage for an asset-heavy, thin-margin logistics business"},
        {"condition": "ebitda_margin < 8",  "severity": "medium", "message": "EBITDA margin < 8% — thin margins typical of commoditised freight, limited cushion"},
    ],

    "valuation": {
        "primary":   ["EV/EBITDA", "P/E"],
        "secondary": ["Price/Sales"],
        "notes": (
            "Asset-heavy logistics companies are best compared on EV/EBITDA given depreciation-heavy P&Ls; "
            "asset-light, high-growth logistics/delivery platforms are often valued on Price/Sales during "
            "their growth phase before margins normalise."
        ),
        "bands": {
            "ev_ebitda": {"attractive": (0, 10), "fair": (10, 16), "expensive": (16, 999)},
        },
    },

    "llm_context": (
        "This is a LOGISTICS / FREIGHT / SUPPLY CHAIN company. Focus on: network density and reach, "
        "asset-light vs asset-heavy business model, fuel cost exposure, client concentration (especially "
        "e-commerce clients), and margin trajectory as volumes scale. Distinguish traditional freight/courier "
        "businesses from newer e-commerce-logistics platforms, since their margin structures and growth "
        "profiles are quite different."
    ),
}
