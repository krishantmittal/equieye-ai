# modules/sectors/tyre_manufacturing.py
"""
Tyre Manufacturing — Sector Module
===================================
For MRF, Apollo Tyres, CEAT and similar tyre manufacturers.

Previously landed in "auto_ev" (the auto OEM module) — a weak fit, not
technically broken but wrong in emphasis. Tyre makers are auto ancillary/
component manufacturers, not vehicle OEMs: they sell into both the OEM
channel (lower margin, negotiated with auto manufacturers) and the much
higher-margin replacement/aftermarket channel (where brand and dealer
network matter, similar to a branded consumer product), plus exports.
Natural rubber price is the dominant input-cost swing factor, which has
no equivalent in the auto_ev module (built around vehicle-demand cycles,
EV transition, and OEM-level metrics like ASP and EV mix).
"""

SECTOR_CONFIG: dict = {
    "slug": "tyre_manufacturing",
    "display_name": "Tyre Manufacturing",

    "key_metrics": [
        {"id": "replacement_channel_mix", "label": "Replacement (Aftermarket) Revenue Mix", "unit": "%", "yf_key": None, "higher_is_better": True},
        {"id": "revenue_growth",          "label": "Revenue Growth (YoY)",                  "unit": "%", "yf_key": "revenueGrowth", "higher_is_better": True},
        {"id": "ebitda_margin",           "label": "EBITDA Margin",                          "unit": "%", "yf_key": "ebitdaMargins", "higher_is_better": True},
        {"id": "export_revenue_share",    "label": "Export Revenue Share",                   "unit": "%", "yf_key": None, "higher_is_better": True},
        {"id": "roe",                     "label": "Return on Equity",                       "unit": "%", "yf_key": "returnOnEquity", "higher_is_better": True},
        {"id": "de_ratio",                "label": "Debt/Equity",                            "unit": "x", "yf_key": "debtToEquity", "higher_is_better": False},
    ],

    "scoring_rules": [
        {"metric": "revenue_growth", "op": ">", "threshold": 10.0, "points": 20, "max": 20},
        {"metric": "revenue_growth", "op": ">", "threshold": 4.0,  "points": 12, "max": 20},
        {"metric": "ebitda_margin",  "op": ">", "threshold": 16.0, "points": 25, "max": 25},
        {"metric": "ebitda_margin",  "op": ">", "threshold": 10.0, "points": 15, "max": 25},
        {"metric": "roe",            "op": ">", "threshold": 15.0, "points": 25, "max": 25},
        {"metric": "roe",            "op": ">", "threshold": 8.0,  "points": 15, "max": 25},
        {"metric": "de_ratio",       "op": "<", "threshold": 0.7,  "points": 15, "max": 15},
    ],
    "score_max": 100,

    "risk_factors": [
        "Natural rubber price volatility (a globally traded, weather- and geography-concentrated commodity) is the single largest input-cost swing factor, and pass-through to pricing lags",
        "OEM channel pricing is negotiated with a concentrated set of auto manufacturers who have real bargaining power, structurally lower-margin than the replacement channel",
        "Competitive intensity from Chinese and other low-cost-geography tyre imports pressures pricing in both domestic and export markets",
        "Capex-heavy capacity expansion (new plants) creates a multi-year gestation lag before incremental volume reaches full utilisation",
        "Export demand is exposed to global auto-demand cycles and, for truck/bus radial tyres, freight/logistics-sector health in destination markets",
    ],

    "moat_factors": [
        {"factor": "Brand Strength in Replacement Market", "description": "A trusted tyre brand (e.g. MRF's long-standing reputation) commands a price premium and preferred-choice status in the higher-margin replacement/aftermarket channel, where the end consumer (not just the OEM) makes the purchase decision"},
        {"factor": "Dealer & Distribution Network", "description": "A wide replacement-market dealer network built over decades is a real barrier to a new entrant trying to reach end consumers directly"},
        {"factor": "OEM Relationships & Fitment Approvals", "description": "Long-standing OEM fitment approvals (a tyre must be tested and approved for a specific vehicle model) create switching costs and a moat against a new supplier displacing an incumbent mid-cycle"},
        {"factor": "Manufacturing Scale & R&D", "description": "Scale in manufacturing and R&D (tread compound technology, radial tyre technology) supports both cost competitiveness and premium product positioning"},
    ],

    "bull_case": [
        "Rising vehicle parc (total vehicles on the road) in India driving structural replacement-tyre demand independent of new-vehicle sales cycles",
        "Premiumisation toward radial tyres (from bias-ply) in commercial vehicles improving realisation and margin",
        "Export growth as Indian manufacturers gain share in select international markets",
        "Softening natural rubber prices providing a margin tailwind if it occurs",
    ],

    "bear_case": [
        "A natural rubber price spike compressing margin faster than pricing can be passed through",
        "Intensifying import competition (particularly from China) pressuring domestic pricing",
        "A slowdown in commercial-vehicle sales or freight activity reducing OEM and replacement demand for truck/bus tyres",
        "Capacity additions across the industry outpacing demand growth, pressuring industry-wide utilisation and pricing",
    ],

    "red_flags": [
        {"condition": "ebitda_margin < 8",  "severity": "high",   "message": "EBITDA margin < 8% — thin for the sector; check for an unabsorbed natural-rubber cost spike"},
        {"condition": "revenue_growth < 0", "severity": "high",   "message": "Negative revenue growth — check whether this reflects OEM/export demand weakness or replacement-channel share loss"},
        {"condition": "de_ratio > 1.5",     "severity": "medium", "message": "D/E > 1.5x — elevated; check whether it funds an active capacity-expansion phase or reflects structural leverage"},
    ],

    "valuation": {
        "primary":   ["P/E", "EV/EBITDA"],
        "secondary": ["P/B", "EV/Sales"],
        "notes": (
            "Tyre manufacturers are typically valued on P/E or EV/EBITDA with meaningful earnings cyclicality "
            "tied to the natural-rubber cost cycle — a low trailing P/E during a high-rubber-price period can "
            "understate normalized earnings power, and vice versa, so normalise for the input-cost cycle "
            "before comparing multiples across time or peers."
        ),
    },

    "llm_context": (
        "This is a TYRE MANUFACTURING company (e.g. MRF, Apollo Tyres, CEAT) — an auto ANCILLARY/component "
        "manufacturer, not a vehicle OEM, even though it's adjacent to the auto sector. Do NOT apply auto_ev "
        "OEM-level framing (vehicle ASP, EV transition, model-cycle launches) here. The two channels that "
        "matter are OEM (lower margin, negotiated with a concentrated set of auto manufacturers) and "
        "replacement/aftermarket (higher margin, brand- and dealer-network-driven, more like a branded "
        "consumer product) — a rising replacement-channel mix is generally a margin positive. The dominant "
        "input-cost swing factor is natural rubber price, which has no equivalent in the auto OEM module."
    ),
}
