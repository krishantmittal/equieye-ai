# modules/sectors/port_infrastructure.py
"""
Port Infrastructure / Operators — Sector Module
================================================
For Adani Ports & SEZ and similar port/marine-terminal operators.

CRITICAL DISTINCTION FROM LOGISTICS: yfinance tags this "Marine Shipping"
or "Logistics" and the company's own description repeatedly uses the word
"logistics", which previously routed it into the freight-forwarder/courier
module (Blue Dart-style — asset-light, contract-renewal risk, working-
capital-driven). A port operator is structurally the opposite: it owns and
operates physical terminal capacity (berths, cranes, rail/road
connectivity) at specific locations under long-term concessions, closer in
spirit to airport_infra than to a courier or freight aggregator. Cargo
volume (EXIM trade, coastal shipping) is the demand driver, revenue comes
from cargo-handling and storage charges per tonne/container, and the
moat is locational scarcity plus capital intensity, not a route network or
fleet of couriers.
"""

SECTOR_CONFIG: dict = {
    "slug": "port_infra",
    "display_name": "Port Infrastructure",

    "key_metrics": [
        {"id": "cargo_volume_growth",  "label": "Cargo Volume Growth (YoY)",   "unit": "%", "yf_key": None, "higher_is_better": True},
        {"id": "revenue_growth",       "label": "Revenue Growth (YoY)",        "unit": "%", "yf_key": "revenueGrowth", "higher_is_better": True},
        {"id": "ebitda_margin",        "label": "EBITDA Margin",               "unit": "%", "yf_key": "ebitdaMargins", "higher_is_better": True},
        {"id": "market_share",         "label": "Share of India Port Cargo",   "unit": "%", "yf_key": None, "higher_is_better": True},
        {"id": "de_ratio",             "label": "Debt/Equity (concession-capex heavy)", "unit": "x", "yf_key": "debtToEquity", "higher_is_better": False},
        {"id": "fcf_margin",           "label": "Free Cash Flow Margin",       "unit": "%", "yf_key": None, "higher_is_better": True},
    ],

    "scoring_rules": [
        {"metric": "revenue_growth",  "op": ">", "threshold": 15.0, "points": 20, "max": 20},
        {"metric": "revenue_growth",  "op": ">", "threshold": 8.0,  "points": 12, "max": 20},
        {"metric": "ebitda_margin",   "op": ">", "threshold": 55.0, "points": 25, "max": 25},
        {"metric": "ebitda_margin",   "op": ">", "threshold": 40.0, "points": 15, "max": 25},
        {"metric": "de_ratio",        "op": "<", "threshold": 1.5,  "points": 20, "max": 20},
        {"metric": "de_ratio",        "op": "<", "threshold": 2.5,  "points": 10, "max": 20},
        {"metric": "fcf_margin",      "op": ">", "threshold": 20.0, "points": 15, "max": 15},
    ],
    "score_max": 100,

    "risk_factors": [
        "EXIM trade volumes are tied to macro trade cycles, global commodity demand, and shipping-line routing decisions largely outside the operator's control",
        "Concession/land-lease terms with the port authority or state government (tariff-setting, revenue-share, renewal conditions) carry regulatory and renegotiation risk",
        "High leverage from berth, dredging, and rail/road connectivity capex — a project-finance-style balance sheet",
        "Competition from other ports along the same coastline (or road/rail alternatives for certain cargo) can pressure realisations and volumes at a given terminal",
        "Concentration risk if group-related cargo (e.g. captive coal, group-company imports/exports) makes up a large share of volumes",
        "Weather/monsoon and geopolitical shipping-route disruptions (e.g. Red Sea rerouting) can distort short-term volumes without reflecting underlying demand",
    ],

    "moat_factors": [
        {"factor": "Locational Scarcity", "description": "A deep-draft, well-connected port at a strategic coastal location is a scarce, hard-to-replicate asset — new capacity requires years of dredging, land acquisition, and regulatory clearance"},
        {"factor": "Multi-Port Portfolio Diversification", "description": "Operating terminals across multiple coasts/states diversifies against a single port's regional trade-cycle or weather risk"},
        {"factor": "Hinterland Rail & Road Connectivity", "description": "Owned or contracted rail/road logistics linking the port to inland industrial clusters extends the moat beyond the berth itself and captures a larger share of the cargo's value chain"},
        {"factor": "Long-Term Cargo Contracts", "description": "Multi-year handling agreements with large shippers (including capital-goods and bulk-commodity majors) provide revenue visibility that a spot-market terminal lacks"},
    ],

    "bull_case": [
        "India's rising share of global trade and container/bulk cargo volumes support structural throughput growth",
        "Government push on port-led industrialisation (Sagarmala and similar programs) improving hinterland connectivity and cargo capture",
        "Operating leverage as new berths/terminals ramp toward designed capacity",
        "Diversification into logistics parks, rail, and industrial-corridor real estate monetising the surrounding land bank",
    ],

    "bear_case": [
        "A global trade slowdown or commodity-demand downturn reducing cargo volumes across the portfolio",
        "Adverse tariff or concession-renewal terms from a port authority or state government",
        "High leverage limiting flexibility if a demand shock coincides with an active capex cycle",
        "Loss of a large anchor customer's cargo (including group-related volumes) concentrating downside at a specific terminal",
    ],

    "red_flags": [
        {"condition": "de_ratio > 3",        "severity": "high",   "message": "D/E > 3x — high even for a concession-capex-heavy port operator; check debt maturity and refinancing risk"},
        {"condition": "revenue_growth < 0",  "severity": "high",   "message": "Negative revenue growth — falling cargo volumes or realisations"},
        {"condition": "ebitda_margin < 35",  "severity": "medium", "message": "EBITDA margin < 35% — thin for a port operator; margins here are typically well above general logistics/freight-forwarding businesses"},
    ],

    "valuation": {
        "primary":   ["EV/EBITDA", "DCF (concession-cash-flow based)"],
        "secondary": ["EV/Tonne handled", "P/E"],
        "notes": (
            "Port assets are long-duration, high-margin infrastructure with concession-style economics, so "
            "EV/EBITDA and DCF are more appropriate than benchmarking against asset-light logistics or "
            "freight-forwarding multiples, which reflect a fundamentally different (working-capital-driven, "
            "lower-margin) business model."
        ),
    },

    "llm_context": (
        "This is a PORT / MARINE-TERMINAL INFRASTRUCTURE operator (e.g. Adani Ports & SEZ) — NOT a freight "
        "forwarder or courier, even though yfinance tags it 'Marine Shipping' or 'Logistics' and its own "
        "description uses the word 'logistics' frequently. It owns and operates physical port/terminal "
        "capacity under long-term concessions at specific coastal locations, earning cargo-handling and "
        "storage revenue per tonne/container — much closer in structure to an airport operator (locational "
        "scarcity, concession capex, high EBITDA margins) than to a Blue Dart-style asset-light courier or "
        "freight aggregator. Do NOT apply working-capital-driven, low-margin freight-forwarder framing "
        "here. LEVERAGE: D/E is structurally elevated by berth/dredging/connectivity capex, not lease "
        "accounting or working-capital swings — frame it against the capex/expansion cycle stage."
    ),
}
