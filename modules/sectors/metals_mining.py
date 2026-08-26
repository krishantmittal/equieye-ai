# modules/sectors/metals_mining.py
"""
Metals & Mining — Sector Module
"""

SECTOR_CONFIG: dict = {
    "slug": "metals_mining",
    "display_name": "Metals & Mining",

    "key_metrics": [
        {"id": "ebitda_per_tonne",  "label": "EBITDA / Tonne",          "unit": "₹",  "yf_key": None,             "higher_is_better": True},
        {"id": "capacity_util",     "label": "Capacity Utilisation",    "unit": "%",  "yf_key": None,             "higher_is_better": True},
        {"id": "volume_growth",     "label": "Volume Growth (YoY)",     "unit": "%",  "yf_key": None,             "higher_is_better": True},
        {"id": "net_debt_ebitda",   "label": "Net Debt/EBITDA",         "unit": "x",  "yf_key": None,             "higher_is_better": False},
        {"id": "realisation_growth","label": "Price Realisation Growth","unit": "%",  "yf_key": None,             "higher_is_better": True},
        {"id": "cost_of_production","label": "Cost of Production/Tonne","unit": "₹", "yf_key": None,             "higher_is_better": False},
        {"id": "ebitda_margin",     "label": "EBITDA Margin",           "unit": "%",  "yf_key": "ebitdaMargins", "higher_is_better": True},
        {"id": "roce",              "label": "Return on Capital Employed","unit": "%","yf_key": "returnOnEquity","higher_is_better": True},
    ],

    "scoring_rules": [
        {"metric": "ebitda_margin",   "op": ">", "threshold": 25.0, "points": 20, "max": 20},
        {"metric": "ebitda_margin",   "op": ">", "threshold": 15.0, "points": 12, "max": 20},
        {"metric": "net_debt_ebitda", "op": "<", "threshold": 1.5,  "points": 20, "max": 20},
        {"metric": "net_debt_ebitda", "op": "<", "threshold": 3.0,  "points": 10, "max": 20},
        {"metric": "capacity_util",   "op": ">", "threshold": 85.0, "points": 15, "max": 15},
        {"metric": "capacity_util",   "op": ">", "threshold": 70.0, "points": 8,  "max": 15},
        {"metric": "roce",            "op": ">", "threshold": 18.0, "points": 20, "max": 20},
        {"metric": "roce",            "op": ">", "threshold": 12.0, "points": 10, "max": 20},
        {"metric": "volume_growth",   "op": ">", "threshold": 8.0,  "points": 10, "max": 10},
    ],
    "score_max": 100,

    "risk_factors": [
        "Commodity price cyclicality — steel/aluminium/copper prices swing with global demand-supply",
        "China demand/supply dynamics dominate global metal pricing (China overcapacity risk)",
        "High capital intensity with long-gestation capacity expansion projects",
        "Environmental/mining-license regulatory risk (forest clearance, mining lease renewals)",
        "Energy cost volatility — power/coal is a major input cost for primary metal production",
        "Leverage risk during commodity downcycles when EBITDA compresses sharply",
    ],

    "moat_factors": [
        {"factor": "Low-Cost Production",    "description": "Captive raw material (iron ore, bauxite, coal mines) gives a structural cost advantage"},
        {"factor": "Scale & Integration",    "description": "Backward integration from mine to finished product captures margin across the value chain"},
        {"factor": "Diversified Commodity Exposure", "description": "Spread across multiple commodities (e.g. aluminium, zinc-lead-silver, iron ore, oil & gas) reduces dependence on any single commodity's price cycle, unlike a single-metal pure-play"},
        {"factor": "Logistics & Location",   "description": "Proximity to ports/raw material sources reduces freight cost disadvantage"},
        {"factor": "Product Mix",            "description": "Value-added/specialty products (auto-grade steel, alloys) command premium over commodity grades"},
        {"factor": "Brownfield Expansion",   "description": "Expanding existing capacity is cheaper and faster than greenfield — an edge for incumbents"},
    ],

    "bull_case": [
        "Infrastructure and construction capex cycle in India driving structural steel/cement-adjacent demand",
        "China supply-side reforms or property slowdown reducing global oversupply",
        "Captive mine ownership providing margin insulation during raw material price spikes",
        "Value-added product mix shift (specialty alloys, auto-grade steel) improving realisation",
        "Global green steel transition creating premium pricing for low-carbon production",
    ],

    "bear_case": [
        "Global recession or China hard-landing crushing commodity prices",
        "Chinese export dumping at below-cost prices pressuring domestic realisations",
        "High leverage amplifying downside during a cyclical trough",
        "Rising energy/coking coal costs compressing margins independent of metal prices",
        "Regulatory delays in mining lease renewals disrupting raw material security",
    ],

    "red_flags": [
        {"condition": "net_debt_ebitda > 3",  "severity": "high",   "message": "Net Debt/EBITDA > 3x — dangerous leverage heading into a commodity downcycle"},
        {"condition": "ebitda_margin < 12",   "severity": "high",   "message": "EBITDA margin < 12% — weak margin even before a cyclical trough"},
        {"condition": "capacity_util < 65",   "severity": "medium", "message": "Capacity utilisation < 65% — fixed costs under-absorbed"},
        {"condition": "volume_growth < 0",    "severity": "medium", "message": "Volume decline — demand or competitiveness issue"},
        {"condition": "roce < 8",             "severity": "medium", "message": "ROCE < 8% — capital intensive business not earning above cost of capital"},
    ],

    "valuation": {
        "primary":   ["EV/EBITDA", "EV/Tonne"],
        "secondary": ["P/B Ratio"],
        "notes": (
            "Metals/mining is deeply cyclical — value through-the-cycle on normalised mid-cycle EV/EBITDA "
            "(typically 5-8x), not peak-cycle earnings. "
            "EV/Tonne of capacity is a useful cross-check for replacement-cost valuation. "
            "P/E is unreliable at cycle extremes (very low at peak earnings, very high/negative at trough)."
        ),
        "bands": {
            "ev_ebitda": {"attractive": (0, 5), "fair": (5, 8), "expensive": (8, 999)},
        },
    },

    "llm_context": (
        "This is a METALS & MINING company. Focus on: EBITDA/tonne, capacity utilisation, Net Debt/EBITDA, "
        "captive raw material integration, and where the company sits in the commodity price cycle. Don't "
        "value on peak-cycle P/E — use through-cycle EV/EBITDA. Leverage is the critical risk factor — flag "
        "Net Debt/EBITDA > 3x heading into a downcycle. China demand-supply dynamics dominate global metal "
        "pricing and are worth mentioning. "
        "MOAT — this is a commodity-price-taking business, not a pricing-power one: a strong trailing "
        "margin/ROE mostly reflects where the cycle currently sits, not a durable edge the way it would for "
        "a branded consumer or platform business (Asian Paints, Titan, HDFC Bank); assess the moat "
        "through-cycle, not off current-year fundamentals. Real, durable moat sources here are cost "
        "leadership (captive raw material, integration, scale, logistics) and, for a diversified "
        "multi-commodity producer, reduced single-commodity dependence versus a pure-play peer — call these "
        "out only when the company description supports them. Offset against: (1) genuine "
        "commodity-pricing risk — this business doesn't control what it sells for, so 'pricing power' "
        "framing is misleading, and (2) for a conglomerate with a listed parent, group-level "
        "governance/cash-upstreaming risk (e.g. dividends to a leveraged parent) is fair to flag only if "
        "grounded in something real about this specific company — never invent a governance concern."
    ),
}
