# modules/sectors/textiles_apparel.py
"""
Textiles & Apparel Manufacturing — Sector Module
=================================================
For Page Industries (Jockey licensee), Vardhman Textiles, Raymond and
similar branded-apparel or yarn/fabric manufacturers.

Was previously falling through to "generic". This sector spans a wide
spectrum from commodity yarn/fabric manufacturing (cotton-price exposed,
export-driven, thin-margin) to branded innerwear/apparel manufacturing
(licensed-brand royalty economics, much higher margin and pricing power)
— a single generic industrial lens misses both the cotton-price/export-
cycle exposure common to the whole sector AND the very different margin
profile a licensed brand (e.g. Jockey in India) commands versus a pure
commodity fabric/yarn maker.
"""

SECTOR_CONFIG: dict = {
    "slug": "textiles_apparel",
    "display_name": "Textiles & Apparel Manufacturing",

    "key_metrics": [
        {"id": "revenue_growth",   "label": "Revenue Growth (YoY)",       "unit": "%", "yf_key": "revenueGrowth", "higher_is_better": True},
        {"id": "export_revenue_share", "label": "Export Revenue Share",   "unit": "%", "yf_key": None, "higher_is_better": True},
        {"id": "ebitda_margin",    "label": "EBITDA Margin",              "unit": "%", "yf_key": "ebitdaMargins", "higher_is_better": True},
        {"id": "roe",              "label": "Return on Equity",           "unit": "%", "yf_key": "returnOnEquity", "higher_is_better": True},
        {"id": "inventory_days",   "label": "Inventory Days",             "unit": "days", "yf_key": None, "higher_is_better": False},
        {"id": "de_ratio",         "label": "Debt/Equity",                "unit": "x", "yf_key": "debtToEquity", "higher_is_better": False},
    ],

    "scoring_rules": [
        {"metric": "revenue_growth", "op": ">", "threshold": 12.0, "points": 20, "max": 20},
        {"metric": "revenue_growth", "op": ">", "threshold": 5.0,  "points": 12, "max": 20},
        {"metric": "ebitda_margin",  "op": ">", "threshold": 18.0, "points": 25, "max": 25},
        {"metric": "ebitda_margin",  "op": ">", "threshold": 10.0, "points": 15, "max": 25},
        {"metric": "roe",            "op": ">", "threshold": 20.0, "points": 25, "max": 25},
        {"metric": "roe",            "op": ">", "threshold": 12.0, "points": 15, "max": 25},
        {"metric": "de_ratio",       "op": "<", "threshold": 0.7,  "points": 15, "max": 15},
    ],
    "score_max": 100,

    "risk_factors": [
        "Cotton and other raw-material (fibre, yarn) price volatility directly affects input costs and margin, especially for commodity yarn/fabric manufacturers",
        "Export-oriented players face demand-cycle and currency risk tied to key export markets (US/EU apparel demand, freight costs)",
        "Fashion/seasonal inventory risk — unsold seasonal stock can force margin-eroding discounting, more acute for branded-apparel players than pure yarn/fabric makers",
        "Labour-cost inflation and competition from other low-cost textile-manufacturing geographies (Bangladesh, Vietnam) pressure India's cost competitiveness in commodity segments",
        "Licensed-brand businesses (e.g. a brand-licensee model) carry royalty/licence-renewal terms and brand-owner relationship risk not present in a fully-owned-brand or pure-manufacturing business",
    ],

    "moat_factors": [
        {"factor": "Licensed Brand Exclusivity", "description": "An exclusive, long-term licence to manufacture and distribute a globally recognised brand (e.g. Jockey, certain international labels) in India provides brand-level pricing power that a pure contract manufacturer lacks"},
        {"factor": "Distribution & Retail Network", "description": "A wide-format retail/EBO (exclusive brand outlet) and modern-trade distribution network built over years is a real barrier for a new apparel brand entering the market"},
        {"factor": "Vertical Integration", "description": "Backward integration from yarn/fabric into finished garments reduces margin volatility from raw-material price swings and improves quality control versus a pure trading/cut-and-sew player"},
        {"factor": "Scale in Export Manufacturing", "description": "Large-scale yarn/fabric exporters with long-standing global buyer relationships have cost and reliability advantages difficult for smaller players to match"},
    ],

    "bull_case": [
        "Premiumisation and branded-apparel category growth in India as discretionary spending rises",
        "China-plus-one and global supply-chain diversification trends benefiting Indian textile exporters",
        "Government PLI (production-linked incentive) schemes for textiles supporting capacity expansion and cost competitiveness",
        "Retail network expansion (EBOs, e-commerce) improving direct-to-consumer economics for branded players",
    ],

    "bear_case": [
        "A cotton/input-price spike compressing margins faster than pricing can be passed through, especially for commodity yarn/fabric makers",
        "A slowdown in key export markets (US/EU) reducing demand for India's textile exports",
        "Unsold seasonal branded-apparel inventory forcing margin-eroding discounting",
        "Rising competition from lower-cost manufacturing geographies eroding India's cost advantage in commodity segments",
    ],

    "red_flags": [
        {"condition": "ebitda_margin < 8",   "severity": "high",   "message": "EBITDA margin < 8% — thin even for the more commodity end of this sector; check for a raw-material cost spike or heavy discounting"},
        {"condition": "revenue_growth < 0",  "severity": "high",   "message": "Negative revenue growth — check whether this reflects export-market weakness, domestic demand softness, or brand/licence-related disruption"},
        {"condition": "de_ratio > 1.5",      "severity": "medium", "message": "D/E > 1.5x — elevated for this sector; check whether it funds working capital (inventory-heavy, less concerning) or capacity expansion"},
    ],

    "valuation": {
        "primary":   ["P/E", "EV/EBITDA"],
        "secondary": ["P/B", "EV/Sales"],
        "notes": (
            "Branded/licensed-apparel names (e.g. Page Industries) typically command a meaningful valuation "
            "premium over pure commodity yarn/fabric manufacturers (e.g. Vardhman Textiles) given the "
            "brand-royalty-like margin and pricing-power profile — don't benchmark the two sub-segments "
            "against the same multiple band."
        ),
    },

    "llm_context": (
        "This is a TEXTILES & APPAREL MANUFACTURING company (e.g. Page Industries/Jockey, Vardhman "
        "Textiles, Raymond). This sector spans a spectrum: commodity yarn/fabric/export manufacturing "
        "(cotton-price exposed, thinner margin, export-cycle-driven) at one end, and licensed-brand or "
        "owned-brand apparel manufacturing (much higher margin, brand-pricing-power-driven) at the other — "
        "identify which end of the spectrum the specific company sits on from its description before "
        "applying margin/valuation expectations, since a flat sector-wide benchmark would misjudge either "
        "extreme. For licensed-brand businesses (e.g. an exclusive brand licensee), note the royalty/"
        "licence-renewal relationship with the brand owner as a distinct risk factor not present in a fully "
        "owned-brand or pure-manufacturing business."
    ),
}
