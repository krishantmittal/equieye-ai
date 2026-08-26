# modules/sectors/power_generation.py
"""
Power Generation — Sector Module
==================================
Split out of power_utilities.py. A generator (NTPC, Adani Power, JSW Energy)
lives and dies by fuel cost/availability, plant load factor, and PPA
(power purchase agreement) coverage — none of which apply to a pure
transmission or distribution company. This module keeps the generation-
specific concepts that power_utilities.py used to apply indiscriminately to
every power company regardless of which part of the value chain it's in.
"""

SECTOR_CONFIG: dict = {
    "slug": "power_generation",
    "display_name": "Power Generation",

    "key_metrics": [
        {"id": "plf",                "label": "Plant Load Factor",         "unit": "%", "yf_key": None,             "higher_is_better": True},
        {"id": "ppa_coverage_pct",   "label": "PPA-Tied Capacity",         "unit": "%", "yf_key": None,             "higher_is_better": True},
        {"id": "fuel_cost_per_unit", "label": "Fuel Cost/Unit Generated",  "unit": "₹", "yf_key": None,             "higher_is_better": False},
        {"id": "renewable_capacity_pct", "label": "Renewable Capacity Mix","unit": "%", "yf_key": None,             "higher_is_better": True},
        {"id": "debt_equity",        "label": "Debt/Equity",               "unit": "x", "yf_key": "debtToEquity",  "higher_is_better": False},
        {"id": "receivable_days",    "label": "Receivable Days (Discoms)", "unit": "days", "yf_key": None,          "higher_is_better": False},
        {"id": "roe",                "label": "Return on Equity",          "unit": "%", "yf_key": "returnOnEquity","higher_is_better": True},
    ],

    "scoring_rules": [
        {"metric": "plf",              "op": ">", "threshold": 75.0, "points": 20, "max": 20},
        {"metric": "plf",              "op": ">", "threshold": 60.0, "points": 10, "max": 20},
        {"metric": "ppa_coverage_pct", "op": ">", "threshold": 80.0, "points": 20, "max": 20},
        {"metric": "ppa_coverage_pct", "op": ">", "threshold": 50.0, "points": 10, "max": 20},
        {"metric": "debt_equity",      "op": "<", "threshold": 1.5,  "points": 20, "max": 20},
        {"metric": "debt_equity",      "op": "<", "threshold": 2.5,  "points": 10, "max": 20},
        {"metric": "receivable_days",  "op": "<", "threshold": 90.0, "points": 20, "max": 20},
        {"metric": "roe",              "op": ">", "threshold": 12.0, "points": 20, "max": 20},
    ],
    "score_max": 100,

    "risk_factors": [
        "Fuel availability/cost risk — coal linkage security, import dependency, and spot fuel-price spikes "
        "directly compress margins on the uncontracted/merchant portion of capacity",
        "Discom payment delays — receivables from state distribution utilities can balloon and strain "
        "working capital",
        "PPA renewal and merchant-market exposure — capacity not tied to a long-term PPA is exposed to "
        "volatile short-term power prices",
        "Stranded asset risk on thermal capacity as renewable mandates and coal-phase-down policy accelerate",
        "Environmental/emission-norm tightening requiring capex (FGD installation, etc.) on existing thermal "
        "fleet",
        "Regulatory risk: tariff orders and fuel-cost pass-through mechanisms can lag actual cost inflation",
    ],

    "moat_factors": [
        {"factor": "Long-Term PPAs",              "description": "25-year power purchase agreements with discoms provide multi-decade revenue visibility and de-risk the volume/price question that a merchant generator faces"},
        {"factor": "Fuel Linkage & Cost Position", "description": "Secured coal-linkage or captive-mine access gives a durable cost advantage over generators reliant on spot/imported fuel"},
        {"factor": "Scale & Fleet Diversification","description": "A diversified thermal+hydro+renewable generation mix smooths earnings across fuel-cost and demand cycles better than a single-fuel plant"},
        {"factor": "Execution Track Record",       "description": "Reliable large-scale plant execution and O&M track record commands regulatory/government trust for new capacity allocation"},
        {"factor": "Regulated Return (Where Applicable)", "description": "For capacity under a cost-plus regulated tariff, return on equity is contractually assured rather than merchant-price-dependent"},
    ],

    "bull_case": [
        "India's power demand growing at a structural pace (industrialisation, electrification, rising per-"
        "capita consumption) supporting utilisation and new capacity addition",
        "PPA-backed capacity offers earnings visibility comparable to a regulated-return business",
        "Renewable capacity addition (own build-out or JV) captures growth demand while diversifying away from "
        "pure thermal exposure",
        "Improving plant load factor and operational efficiency directly expanding margins on largely "
        "fixed-cost generation assets",
        "Fuel-cost pass-through mechanisms (where available) provide partial insulation from coal-price "
        "volatility",
    ],

    "bear_case": [
        "Coal supply disruption or cost spikes squeezing margins on uncontracted/merchant capacity",
        "Discom receivables ballooning and straining working capital and cash flow",
        "Stranded thermal asset risk accelerating as renewable mandates and coal-phase-down policy tighten",
        "Renewable energy displacing thermal dispatch (merit-order effect) and compressing PLF on older, "
        "less-efficient plants",
        "Environmental/emission compliance capex (FGD, etc.) required on ageing thermal fleet without a "
        "commensurate tariff increase",
        "PPA non-renewal risk pushing more capacity into the volatile merchant market",
    ],

    "red_flags": [
        {"condition": "plf < 55",             "severity": "high",   "message": "PLF < 55% — significant underutilisation of generation capacity"},
        {"condition": "ppa_coverage_pct < 40", "severity": "high",   "message": "PPA coverage < 40% — heavy exposure to volatile merchant power prices"},
        {"condition": "receivable_days > 150", "severity": "high",   "message": "Receivable days > 150 — severe discom payment-delay strain"},
        {"condition": "debt_equity > 2.5",     "severity": "medium", "message": "D/E > 2.5x — high leverage for a capital-intensive generation business"},
    ],

    "valuation": {
        "primary":   ["P/E", "EV/EBITDA"],
        "secondary": ["P/B Ratio", "Dividend Yield"],
        "notes": (
            "Generators with a high share of long-term PPA-backed, regulated-return capacity (e.g. NTPC) "
            "trade closer to a utility/infrastructure multiple (P/B, dividend yield); generators with more "
            "merchant/uncontracted capacity behave more like a cyclical commodity business and should be "
            "judged more on EV/EBITDA through a fuel-price cycle than on a single-year P/E."
        ),
    },

    "llm_context": (
        "This is a POWER GENERATION company (e.g. NTPC, Adani Power, JSW Energy) — distinct from a "
        "TRANSMISSION company (Power Grid, Adani Energy Solutions' transmission arm) and a DISTRIBUTION/"
        "discom company (Torrent Power, CESC). This company actually generates and sells power — fuel cost, "
        "fuel availability (coal linkage vs. import dependency), plant load factor, and PPA (power purchase "
        "agreement) coverage are all real and central here, unlike for a transmission-only company. "
        "Focus on: PPA-tied vs. merchant capacity mix, fuel linkage security and cost position, plant load "
        "factor and fleet diversification (thermal/hydro/renewable), discom receivable risk, and stranded-"
        "asset risk on ageing thermal capacity as the energy transition accelerates. "
        "The dominant BEAR theme specific to generation is fuel cost/availability risk and renewable "
        "cannibalisation of thermal dispatch (merit-order effect reducing PLF) — this is materially different "
        "from a transmission company's bear case (competitive-bid margin compression, discom payment delays "
        "with zero fuel exposure) or a distribution company's bear case (AT&C losses, tariff true-up delays)."
    ),
}
