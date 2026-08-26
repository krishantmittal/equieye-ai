# modules/sectors/hospitality.py
"""
Hospitality / Hotels — Sector Module
=====================================
For Indian Hotels Company (Taj), EIH (Oberoi), Lemon Tree Hotels, Chalet
Hotels and similar hotel owner-operators.

Was previously falling through to "generic". Hotels are a capacity-
constrained, high-operating-leverage business where the two metrics that
actually explain profitability — Occupancy and Average Room Rate (ARR),
combined into RevPAR (Revenue Per Available Room) — have no equivalent in
a generic industrial framework. A generic D/E or margin-only lens misses
that a modest RevPAR improvement can drive outsized EBITDA growth (high
fixed cost base), and that owned-asset-heavy chains carry real-estate-like
leverage that a pure management-contract/brand-licensing hotel company
(an "asset-light" model, increasingly common in India) does not.
"""

SECTOR_CONFIG: dict = {
    "slug": "hospitality",
    "display_name": "Hospitality / Hotels",

    "key_metrics": [
        {"id": "revpar_growth",     "label": "RevPAR Growth (YoY)",       "unit": "%", "yf_key": None, "higher_is_better": True},
        {"id": "occupancy_rate",    "label": "Occupancy Rate",            "unit": "%", "yf_key": None, "higher_is_better": True},
        {"id": "arr_growth",        "label": "Average Room Rate Growth",  "unit": "%", "yf_key": None, "higher_is_better": True},
        {"id": "ebitda_margin",     "label": "EBITDA Margin",             "unit": "%", "yf_key": "ebitdaMargins", "higher_is_better": True},
        {"id": "revenue_growth",    "label": "Revenue Growth (YoY)",      "unit": "%", "yf_key": "revenueGrowth", "higher_is_better": True},
        {"id": "de_ratio",         "label": "Debt/Equity (owned-asset heavy)", "unit": "x", "yf_key": "debtToEquity", "higher_is_better": False},
    ],

    "scoring_rules": [
        {"metric": "revenue_growth", "op": ">", "threshold": 15.0, "points": 20, "max": 20},
        {"metric": "revenue_growth", "op": ">", "threshold": 8.0,  "points": 12, "max": 20},
        {"metric": "ebitda_margin",  "op": ">", "threshold": 30.0, "points": 25, "max": 25},
        {"metric": "ebitda_margin",  "op": ">", "threshold": 20.0, "points": 15, "max": 25},
        {"metric": "de_ratio",       "op": "<", "threshold": 1.0,  "points": 20, "max": 20},
        {"metric": "de_ratio",       "op": "<", "threshold": 2.0,  "points": 10, "max": 20},
        {"metric": "occupancy_rate", "op": ">", "threshold": 70.0, "points": 15, "max": 15},
    ],
    "score_max": 100,

    "risk_factors": [
        "High fixed-cost operating leverage means a demand shock (economic slowdown, geopolitical event, pandemic-style disruption) hits profitability disproportionately harder than revenue",
        "New room-supply additions (own or competitor) in a given market can pressure occupancy and ARR even if underlying travel demand is healthy",
        "Owned-asset-heavy balance sheets (real estate) carry structurally higher leverage and depreciation than an asset-light, management-contract-driven hotel company",
        "Business/MICE (meetings, incentives, conferences, exhibitions) travel demand is more cyclical than leisure travel, and corporate travel budgets are among the first to be cut in a slowdown",
        "Seasonality (festive season, wedding season, monsoon) creates meaningful quarter-to-quarter swings that shouldn't be mistaken for a trend",
    ],

    "moat_factors": [
        {"factor": "Iconic Property & Brand Portfolio", "description": "Flagship heritage/iconic properties (e.g. Taj Mahal Palace, Oberoi properties) in prime locations are effectively irreplaceable assets that create pricing power a new-build competitor cannot match"},
        {"factor": "Asset-Light Management Contract Growth", "description": "Increasingly, Indian hotel majors are growing room inventory via management/franchise contracts rather than owned capex — this improves ROE and reduces balance-sheet risk versus a pure owned-asset model"},
        {"factor": "Loyalty Programs & Corporate Relationships", "description": "Loyalty programs and long-standing corporate-account relationships create repeat-booking stickiness that a new entrant has to build from scratch"},
        {"factor": "Prime Location Scarcity", "description": "Well-located land in metro/leisure-destination markets is scarce and increasingly expensive to acquire, protecting the value of existing owned properties"},
    ],

    "bull_case": [
        "Structural growth in Indian leisure and business travel, with room supply growth historically lagging demand growth in several key markets, supporting RevPAR expansion",
        "Shift toward asset-light management-contract expansion improving ROE and reducing capex intensity for the incumbent's growth",
        "Premiumisation and rising ARR as domestic and inbound travellers trade up",
        "MICE and wedding-destination demand providing a growing, India-specific demand pool beyond pure business/leisure travel",
    ],

    "bear_case": [
        "An economic slowdown or demand shock disproportionately hitting profitability given the high fixed-cost operating leverage",
        "New supply additions in key markets (Mumbai, Delhi, Goa etc.) pressuring occupancy and ARR",
        "A geopolitical or public-health disruption to travel (the sector's most extreme historical risk)",
        "High leverage at owned-asset-heavy chains limiting flexibility during a downturn",
    ],

    "red_flags": [
        {"condition": "occupancy_rate < 55", "severity": "high",   "message": "Occupancy < 55% — weak for the sector; check whether this reflects a demand shock, new competing supply, or a seasonal quarter"},
        {"condition": "ebitda_margin < 15",  "severity": "high",   "message": "EBITDA margin < 15% — thin given the sector's normal high-operating-leverage profile; check RevPAR trend"},
        {"condition": "de_ratio > 2.5",      "severity": "medium", "message": "D/E > 2.5x — high even for an owned-asset-heavy hotel chain; check debt maturity and interest cover"},
    ],

    "valuation": {
        "primary":   ["EV/EBITDA", "P/E"],
        "secondary": ["EV/Room", "P/B"],
        "notes": (
            "Hotel companies are usually valued on EV/EBITDA given the mix of owned real estate and "
            "operating business, with EV/Room a useful cross-check on how the market prices existing "
            "capacity versus replacement cost. Earnings are cyclical, so look at multiples across a full "
            "travel-demand cycle rather than a single peak or trough year."
        ),
    },

    "llm_context": (
        "This is a HOSPITALITY / HOTEL company (e.g. Indian Hotels Company/Taj, EIH/Oberoi, Lemon Tree "
        "Hotels) — a capacity-constrained, high-operating-leverage business. The key operating metrics are "
        "Occupancy, Average Room Rate (ARR), and RevPAR (Revenue Per Available Room) — a modest RevPAR "
        "improvement can drive outsized EBITDA growth because most operating costs are fixed. Distinguish "
        "between an owned-asset-heavy model (real-estate-like leverage, higher depreciation) and an "
        "asset-light management/franchise-contract growth model (better ROE, lower balance-sheet risk) — "
        "many Indian hotel majors are shifting toward the latter for new room additions even while retaining "
        "flagship owned properties. Don't apply a flat industrial D/E benchmark without checking which "
        "model dominates the company's growth."
    ),
}
