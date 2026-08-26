# modules/sectors/coal_mining.py
"""
Coal Mining — Sector Module
============================
Split out from metals_mining.py, where "coal india" was previously a
hardcoded keyword match. A dedicated coal producer (reserves-and-royalty
economics, government-mandated linkage pricing, a single-commodity thermal-
demand outlook, PSU dividend policy) is a fundamentally different business
from a diversified metals/mining company (steel/aluminium/zinc/copper —
commodity-price-taking, multi-commodity, no linkage-pricing mechanism), so
the two shouldn't share moat/bull/bear language. This module's user base is
effectively Coal India Ltd and its listed subsidiaries (Mahanadi Coalfields,
etc.) plus Singareni Collieries — India's only significant listed pure-play
coal producers.
"""

SECTOR_CONFIG: dict = {
    "slug": "coal_mining",
    "display_name": "Coal Mining",

    "key_metrics": [
        {"id": "e_auction_premium",  "label": "E-Auction Premium over FSA", "unit": "%", "yf_key": None,             "higher_is_better": True},
        {"id": "offtake_growth",     "label": "Coal Offtake Growth (YoY)",  "unit": "%", "yf_key": None,             "higher_is_better": True},
        {"id": "fsa_volume_share",   "label": "FSA/Linkage Volume Share",   "unit": "%", "yf_key": None,             "higher_is_better": True},
        {"id": "cost_of_production", "label": "Cost of Production/Tonne",   "unit": "₹", "yf_key": None,             "higher_is_better": False},
        {"id": "realisation_per_tonne", "label": "Realisation/Tonne",       "unit": "₹", "yf_key": None,             "higher_is_better": True},
        {"id": "ebitda_margin",      "label": "EBITDA Margin",              "unit": "%", "yf_key": "ebitdaMargins", "higher_is_better": True},
        {"id": "dividend_yield",     "label": "Dividend Yield",             "unit": "%", "yf_key": "dividendYield", "higher_is_better": True},
        {"id": "roce",               "label": "Return on Capital Employed", "unit": "%", "yf_key": "returnOnEquity","higher_is_better": True},
    ],

    "scoring_rules": [
        {"metric": "ebitda_margin",     "op": ">", "threshold": 30.0, "points": 20, "max": 20},
        {"metric": "ebitda_margin",     "op": ">", "threshold": 20.0, "points": 12, "max": 20},
        {"metric": "dividend_yield",    "op": ">", "threshold": 5.0,  "points": 15, "max": 15},
        {"metric": "dividend_yield",    "op": ">", "threshold": 3.0,  "points": 8,  "max": 15},
        {"metric": "offtake_growth",    "op": ">", "threshold": 5.0,  "points": 15, "max": 15},
        {"metric": "offtake_growth",    "op": ">", "threshold": 0.0,  "points": 8,  "max": 15},
        {"metric": "roce",              "op": ">", "threshold": 25.0, "points": 20, "max": 20},
        {"metric": "roce",              "op": ">", "threshold": 15.0, "points": 10, "max": 20},
        {"metric": "e_auction_premium", "op": ">", "threshold": 30.0, "points": 10, "max": 10},
    ],
    "score_max": 100,

    "risk_factors": [
        "Long-term thermal demand risk from the renewable/decarbonization transition — this is a structural, "
        "multi-decade headwind unique to a fossil-fuel pure-play, not a normal cyclical risk",
        "Government-mandated FSA/linkage pricing caps realisation on the majority of volumes — this is not a "
        "free-market price-taker business the way a diversified miner is",
        "Evacuation-infrastructure bottleneck — rail siding/first-mile connectivity constrains how much mined "
        "coal can actually be dispatched, independent of demand or mining capacity",
        "Environmental clearance and mining-lease renewal risk (forest land diversion, R&R/land acquisition "
        "disputes) on new and existing blocks",
        "Large unionised workforce — wage settlements and industrial action risk",
        "Monsoon-driven production and evacuation disruption in open-cast mining",
        "Single-commodity, majority-domestic-customer concentration (Indian power sector) — a policy shift in "
        "coal-based power dispatch has an outsized impact versus a diversified commodity mix",
    ],

    "moat_factors": [
        {"factor": "Reserve Base & Mining Rights",  "description": "Government-allotted coal blocks and reserves at this scale are effectively impossible for a new entrant to replicate — this is a structural, not competitive, barrier"},
        {"factor": "Dominant Market Share",         "description": "Commands the large majority of domestic coal production — a quasi-monopoly position in India's primary power-generation fuel"},
        {"factor": "Cost Leadership",                "description": "Predominantly open-cast mining gives materially lower extraction cost per tonne than underground mining used by many global peers"},
        {"factor": "Captive Offtake via FSA",        "description": "Long-term Fuel Supply Agreements with power utilities lock in volume commitments, reducing demand-side uncertainty versus a spot-market commodity seller"},
        {"factor": "Rail Evacuation Infrastructure", "description": "Established rail sidings/MGR links to major power plants are a real, hard-to-replicate logistics barrier for a new entrant"},
        {"factor": "Regulatory & Licensing Barrier", "description": "New coal block allocation and environmental clearance is a multi-year, politically sensitive process that structurally limits new supply"},
    ],

    "bull_case": [
        "India's rising electricity demand and continued base-load reliance on coal-fired capacity keeping "
        "offtake volumes strong through the medium term",
        "E-auction (market-priced) volume mix improving realisation versus government-capped FSA pricing",
        "High free cash flow generation supporting a sustained high dividend payout — a core part of the "
        "investment case for a PSU cash-cow, distinct from a growth thesis",
        "Import-substitution push (reducing thermal/coking coal imports) directing incremental demand to "
        "domestic production",
        "Operating leverage from largely fixed-cost mining infrastructure as volumes grow",
        "Diversification into coal gasification and allied businesses as a long-horizon hedge on core demand",
    ],

    "bear_case": [
        "Renewable energy transition structurally eroding long-term thermal coal demand — the single biggest "
        "risk to the multi-decade investment case, not a cyclical one",
        "Global and domestic decarbonization/ESG pressure constraining capital access and investor appetite "
        "for a fossil-fuel pure-play, regardless of near-term fundamentals",
        "Government price control on FSA-linked volumes caps realisation upside even when market/e-auction "
        "prices are strong — profitability is not fully in management's control",
        "Evacuation and rail-infrastructure constraints capping how fast offtake can actually grow even if "
        "demand and mined output are available",
        "Labour/union disruption risk given the scale of the unionised workforce",
        "Environmental clearance and land-acquisition delays slowing new mine development",
        "Monsoon-season production and logistics disruption is a recurring, not one-off, drag",
    ],

    "red_flags": [
        {"condition": "offtake_growth < 0",   "severity": "high",   "message": "Coal offtake volume declining — demand or evacuation-capacity issue, not just a pricing issue"},
        {"condition": "ebitda_margin < 15",   "severity": "high",   "message": "EBITDA margin < 15% — unusually weak for a cost-leadership coal producer"},
        {"condition": "dividend_yield < 2",   "severity": "medium", "message": "Dividend yield below 2% — notably low for a PSU coal cash-generator; check for a payout-policy change"},
        {"condition": "roce < 12",            "severity": "medium", "message": "ROCE < 12% — weak capital efficiency for a business with this degree of pricing/volume support"},
    ],

    "valuation": {
        "primary":   ["P/E", "Dividend Yield"],
        "secondary": ["EV/EBITDA"],
        "notes": (
            "Coal India-type companies are typically valued on trailing/forward P/E and dividend yield rather "
            "than growth multiples — this is a mature, high-payout PSU cash generator, not a growth story. "
            "A low headline P/E here usually reflects the market pricing in long-term thermal-demand decline "
            "risk, not necessarily undervaluation — weigh valuation against the ESG/transition risk, not just "
            "against sector peers. EV/EBITDA is a useful cross-check but secondary to the dividend-yield lens "
            "most investors actually use for this stock."
        ),
    },

    "llm_context": (
        "This is a COAL MINING company (e.g. Coal India, Mahanadi Coalfields, Singareni Collieries) — "
        "distinct from a diversified METALS & MINING company (steel/aluminium/zinc/copper: Tata Steel, "
        "Vedanta, Hindalco, JSW Steel). Don't use diversified-commodity or multi-metal moat language; this "
        "is a single-commodity (thermal coal) business, and that concentration is itself the defining "
        "structural fact, not something to call diversified. "
        "Focus on: reserve base and mining rights, dominant/near-monopoly domestic market share, PSU/"
        "government ownership, FSA (linkage) offtake vs. e-auction (market-priced) volume mix, open-cast "
        "cost per tonne, rail evacuation infrastructure, and — critical for the bull case — high dividend "
        "yield and cash generation (not growth) as the primary reason to hold. "
        "The dominant BEAR theme isn't commodity-price cyclicality as with a diversified miner — it's the "
        "structural, multi-decade risk that the renewable transition and ESG/decarbonisation pressure erode "
        "long-term thermal coal demand, compounded by government-mandated linkage pricing capping "
        "realisation upside. Ground outlook in India's near-term power demand growth and coal's continued "
        "base-load role, not global steel/aluminium cycle framing (China oversupply, EV/GDP-linked demand), "
        "which belongs to metals_mining, not here. "
        "MOAT comes from reserve/licensing scarcity, dominant market share, and evacuation-infrastructure "
        "lock-in — not pricing power (FSA price control limits that) or commodity diversification (there is "
        "none)."
    ),
}
