# modules/sectors/chemicals.py
"""
Specialty / Basic Chemicals — Sector Module
"""

SECTOR_CONFIG: dict = {
    "slug": "chemicals",
    "display_name": "Chemicals",

    "key_metrics": [
        {"id": "capacity_util",     "label": "Capacity Utilisation",   "unit": "%", "yf_key": None, "higher_is_better": True},
        {"id": "export_mix",        "label": "Export Revenue Mix",     "unit": "%", "yf_key": None, "higher_is_better": True},
        {"id": "specialty_mix",     "label": "Specialty vs Commodity Mix", "unit": "%", "yf_key": None, "higher_is_better": True},
        {"id": "ebitda_margin",     "label": "EBITDA Margin",          "unit": "%", "yf_key": "ebitdaMargins", "higher_is_better": True},
        {"id": "r_and_d_intensity", "label": "R&D Spend / Revenue",    "unit": "%", "yf_key": None, "higher_is_better": True},
    ],

    "risk_factors": [
        "Commodity chemical pricing is highly cyclical and globally linked (crude/naphtha derivatives)",
        "China dumping / oversupply risk for basic and intermediate chemicals",
        "Regulatory and environmental compliance costs (pollution control, effluent norms)",
        "Customer/product concentration risk for single-molecule specialty players",
        "Currency and freight cost volatility for export-heavy chemical companies",
        "Plant safety/accident risk — chemical manufacturing carries inherent operational hazard",
    ],

    "moat_factors": [
        {"factor": "Specialty / Niche Molecules", "description": "Complex, low-competition molecules command better pricing than commodity chemicals"},
        {"factor": "Backward Integration",         "description": "Captive raw material production insulates margins from input cost swings"},
        {"factor": "Regulatory Approvals",         "description": "Registrations/approvals (especially agrochemical, pharma intermediates) are a real barrier to entry"},
        {"factor": "Customer Relationships",       "description": "Long-term supply contracts with global majors are sticky once qualified"},
        {"factor": "R&D / Process Innovation",     "description": "Process innovation lowers cost or improves yield versus commodity competitors"},
    ],

    "bull_case": [
        "China+1 sourcing shift benefiting Indian specialty/agro chemical exporters",
        "New capacity commissioning driving volume growth",
        "Product mix shift toward higher-margin specialty chemicals",
        "Global supply chain diversification favouring reliable non-China suppliers",
        "PLI (production-linked incentive) scheme benefits for domestic chemical manufacturing",
    ],

    "bear_case": [
        "Chinese oversupply/dumping compressing global chemical prices",
        "Crude/naphtha price volatility squeezing input costs",
        "Global demand slowdown reducing export order volumes",
        "Regulatory action (environmental violations) risking plant shutdowns",
        "New capacity additions industry-wide leading to oversupply and pricing pressure",
    ],

    "red_flags": [
        {"condition": "de_ratio > 1.0",     "severity": "high",   "message": "D/E > 1.0x — high leverage for a cyclical, commodity-price-exposed business"},
        {"condition": "ebitda_margin < 12", "severity": "medium", "message": "EBITDA margin < 12% — margin profile closer to commodity than specialty chemicals"},
    ],

    "valuation": {
        "primary":   ["EV/EBITDA", "P/E"],
        "secondary": ["Price/Sales"],
        "notes": (
            "Specialty chemical companies with a differentiated, high-margin product mix deserve a premium "
            "multiple versus commodity chemical producers whose earnings move with global cyclical pricing. "
            "EV/EBITDA is the standard cross-cycle comparison metric for this sector."
        ),
        "bands": {
            "ev_ebitda": {"attractive": (0, 10), "fair": (10, 16), "expensive": (16, 999)},
            # P/E fallback for when enterpriseToEbitda isn't available from the
            # data source. Commodity/cyclical chemical producers structurally
            # trade at lower multiples than the broader market — using the
            # generic "Basic Materials" band (12-28) was too lenient and let
            # a P/E like 9.5x score as maxed-out "Very Cheap" even though it's
            # fairly ordinary for this sector, not exceptionally cheap.
            "pe_ratio": {"attractive": (0, 8), "fair": (8, 14), "expensive": (14, 999)},
        },
    },

    "llm_context": (
        "This is a CHEMICALS company (specialty or commodity/basic chemicals). Distinguish clearly between "
        "specialty chemical businesses (differentiated molecules, better margins, stickier customers) and "
        "commodity chemical businesses (globally-priced, cyclical, thin margins) — do not treat them the "
        "same. Focus on product mix, export exposure, capacity utilisation, and China competitive dynamics."
    ),
}
