# modules/sectors/qsr_restaurants.py
"""
Quick Service Restaurants (QSR) — Sector Module
================================================
For Jubilant FoodWorks (Domino's India franchisee), Devyani International
(KFC/Pizza Hut/Costa franchisee), Sapphire Foods and similar branded
restaurant-chain franchisees/operators.

Was previously falling through to "generic". QSR economics are driven by
same-store-sales growth (SSSG), store network expansion pace, and dine-in
vs delivery/aggregator channel mix — none of which map to a generic
industrial metric set. Most listed Indian QSR players are master
franchisees of global brands (Domino's, KFC, Pizza Hut) rather than
brand owners, which introduces royalty-payment obligations and brand-
renewal risk that a fully-owned-brand restaurant company wouldn't have.
"""

SECTOR_CONFIG: dict = {
    "slug": "qsr_restaurants",
    "display_name": "Quick Service Restaurants (QSR)",

    "key_metrics": [
        {"id": "same_store_sales_growth", "label": "Same-Store Sales Growth (SSSG)", "unit": "%", "yf_key": None, "higher_is_better": True},
        {"id": "store_count_growth",      "label": "Store Network Growth (YoY)",     "unit": "%", "yf_key": None, "higher_is_better": True},
        {"id": "revenue_growth",          "label": "Revenue Growth (YoY)",           "unit": "%", "yf_key": "revenueGrowth", "higher_is_better": True},
        {"id": "restaurant_ebitda_margin", "label": "Restaurant-Level EBITDA Margin", "unit": "%", "yf_key": "ebitdaMargins", "higher_is_better": True},
        {"id": "delivery_channel_mix",     "label": "Delivery/Aggregator Channel Mix", "unit": "%", "yf_key": None, "higher_is_better": None},
        {"id": "de_ratio",                 "label": "Debt/Equity (lease-heavy)",      "unit": "x", "yf_key": "debtToEquity", "higher_is_better": False},
    ],

    "scoring_rules": [
        {"metric": "revenue_growth",           "op": ">", "threshold": 15.0, "points": 20, "max": 20},
        {"metric": "revenue_growth",           "op": ">", "threshold": 8.0,  "points": 12, "max": 20},
        {"metric": "restaurant_ebitda_margin", "op": ">", "threshold": 20.0, "points": 25, "max": 25},
        {"metric": "restaurant_ebitda_margin", "op": ">", "threshold": 12.0, "points": 15, "max": 25},
        {"metric": "same_store_sales_growth",  "op": ">", "threshold": 8.0,  "points": 25, "max": 25},
        {"metric": "same_store_sales_growth",  "op": ">", "threshold": 3.0,  "points": 15, "max": 25},
        {"metric": "store_count_growth",       "op": ">", "threshold": 10.0, "points": 15, "max": 15},
    ],
    "score_max": 100,

    "risk_factors": [
        "Same-store-sales growth can turn negative even while total revenue grows from new store additions — the two must be read separately to judge true underlying health",
        "Food-input cost inflation (cheese, chicken, packaging) directly compresses restaurant-level margin, especially where menu-price hikes lag",
        "Heavy reliance on food-delivery aggregators (Swiggy/Zomato) for a large share of orders means commission structures set by a third party affect unit economics",
        "Ind AS 116 lease-capitalisation inflates reported D/E and depreciation for a store-network business, similar to airlines — reported leverage looks structurally higher than the underlying cash lease obligation",
        "Most listed players are master franchisees of a global brand, not the brand owner — royalty payments, menu/format mandates, and territory/franchise-renewal terms are set by the brand owner and are outside the franchisee's control",
        "New store cannibalisation risk in dense urban markets as network expansion continues",
    ],

    "moat_factors": [
        {"factor": "Exclusive Master-Franchise Rights", "description": "A long-term exclusive master-franchise agreement for a globally recognised brand (Domino's, KFC, Pizza Hut) in a defined territory is a scarce, hard-to-win right that blocks a domestic competitor from bringing in the same brand"},
        {"factor": "Store Network Density & Supply Chain", "description": "A dense store network supported by a built-out commissary/supply-chain infrastructure lowers delivery times and per-store logistics cost versus a smaller competitor trying to scale"},
        {"factor": "Global Brand Recognition", "description": "The underlying global brand's marketing and product-development investment (done at a global level) benefits the local franchisee without the franchisee bearing that R&D/brand-building cost directly"},
        {"factor": "Aggregator + Owned-App Omnichannel Reach", "description": "Presence across dine-in, owned app/website ordering, and third-party aggregators maximises addressable order volume versus a single-channel competitor"},
    ],

    "bull_case": [
        "Structural growth in India's out-of-home/branded QSR consumption as urbanisation and dual-income households increase",
        "New store network expansion into tier-2/3 cities extending the addressable market",
        "Recovering same-store-sales growth as menu innovation and value offerings win back price-sensitive consumers",
        "Operating leverage on restaurant-level fixed costs as SSSG turns positive",
    ],

    "bear_case": [
        "Persistently weak or negative same-store-sales growth signalling demand softness that new-store openings can mask in headline revenue",
        "Food-input cost inflation that cannot be fully passed through via menu-price hikes without hurting volumes",
        "Rising aggregator commission rates or a shift in commission structure squeezing unit economics",
        "Master-franchise agreement renewal risk or unfavourable renegotiation with the global brand owner",
    ],

    "red_flags": [
        {"condition": "same_store_sales_growth < 0", "severity": "high",   "message": "Negative same-store-sales growth — underlying per-store demand is shrinking even if total revenue is still growing from new stores"},
        {"condition": "restaurant_ebitda_margin < 8", "severity": "high", "message": "Restaurant-level EBITDA margin < 8% — thin; check for unabsorbed input-cost inflation or aggressive discounting"},
        {"condition": "revenue_growth < 0",           "severity": "medium", "message": "Negative total revenue growth — check whether store closures, weak SSSG, or both are the driver"},
    ],

    "valuation": {
        "primary":   ["EV/EBITDA", "P/E"],
        "secondary": ["EV/Store", "P/B"],
        "notes": (
            "QSR names often trade on growth-story multiples (EV/EBITDA, sometimes even EV/Store during "
            "rapid expansion phases) rather than a mature P/E, reflecting the market's focus on store-count "
            "runway and eventual same-store-sales maturation — but a sustained SSSG slowdown is usually the "
            "first signal the growth story is decelerating, well before it shows up in a trailing multiple."
        ),
    },

    "llm_context": (
        "This is a QUICK SERVICE RESTAURANT (QSR) company (e.g. Jubilant FoodWorks/Domino's India, Devyani "
        "International/KFC-Pizza Hut, Sapphire Foods) — most listed Indian QSR players are MASTER "
        "FRANCHISEES of a global brand, not the brand owner themselves, which matters for royalty "
        "obligations and franchise-renewal risk. The key operating metric is Same-Store-Sales Growth "
        "(SSSG) — always read this separately from total revenue growth, since new store additions can "
        "mask deteriorating per-store demand in the headline number. LEVERAGE: like airlines, Ind AS 116 "
        "lease capitalisation structurally inflates reported D/E for a store-network business — don't apply "
        "a flat industrial D/E benchmark without accounting for this. Aggregator (Swiggy/Zomato) commission "
        "structures and food-input cost inflation are the two biggest margin swing factors."
    ),
}
