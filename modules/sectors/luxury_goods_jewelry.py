# modules/sectors/luxury_goods_jewelry.py
"""
Luxury Goods & Jewellery Retail — Sector Module
================================================
For Titan Company, Kalyan Jewellers, PC Jeweller, and similar branded
jewellery/watches/eyewear retailers.

Was previously falling through to "generic" — a normal-industrial default
that ignores this sector's two defining, unusual traits: (1) gold-price
pass-through economics mean revenue growth is often driven as much by
bullion price moves as by volume/store growth, so headline revenue growth
must be read alongside grams-of-gold-sold or same-store-sales growth where
available; and (2) working capital (inventory financing for high-value
gold/diamond stock) is a much bigger swing factor in balance-sheet health
than for a typical retailer.
"""

SECTOR_CONFIG: dict = {
    "slug": "luxury_goods_jewelry",
    "display_name": "Luxury Goods & Jewellery Retail",

    "key_metrics": [
        {"id": "same_store_sales_growth", "label": "Same-Store Sales Growth",  "unit": "%", "yf_key": None, "higher_is_better": True},
        {"id": "revenue_growth",          "label": "Revenue Growth (YoY)",     "unit": "%", "yf_key": "revenueGrowth", "higher_is_better": True},
        {"id": "ebitda_margin",           "label": "EBITDA Margin",            "unit": "%", "yf_key": "ebitdaMargins", "higher_is_better": True},
        {"id": "store_count_growth",      "label": "Store Network Growth",     "unit": "%", "yf_key": None, "higher_is_better": True},
        {"id": "roe",                     "label": "Return on Equity",         "unit": "%", "yf_key": "returnOnEquity", "higher_is_better": True},
        {"id": "inventory_days",          "label": "Inventory Days (gold-heavy working capital)", "unit": "days", "yf_key": None, "higher_is_better": False},
    ],

    "scoring_rules": [
        {"metric": "revenue_growth", "op": ">", "threshold": 18.0, "points": 20, "max": 20},
        {"metric": "revenue_growth", "op": ">", "threshold": 10.0, "points": 12, "max": 20},
        {"metric": "ebitda_margin",  "op": ">", "threshold": 12.0, "points": 20, "max": 20},
        {"metric": "ebitda_margin",  "op": ">", "threshold": 7.0,  "points": 12, "max": 20},
        {"metric": "roe",            "op": ">", "threshold": 25.0, "points": 25, "max": 25},
        {"metric": "roe",            "op": ">", "threshold": 15.0, "points": 15, "max": 25},
        {"metric": "de_ratio",       "op": "<", "threshold": 0.5,  "points": 15, "max": 15},
    ],
    "score_max": 100,

    "risk_factors": [
        "Gold-price volatility affects both inventory valuation and consumer purchase timing — a sharp price spike can temporarily depress volume even as revenue rises on price alone",
        "Working capital is unusually heavy given high-value gold/diamond inventory, making inventory-financing cost and gold-loan hedging a real margin lever",
        "Regulatory scrutiny around gold-import duty changes, hallmarking mandates, and cash-transaction limits directly affects unorganised-sector competition and compliance costs",
        "High organised-vs-unorganised competitive intensity — the unorganised sector still holds a large share of Indian jewellery retail, competing partly on tax/compliance arbitrage",
        "Discretionary consumer spending exposure — jewellery and watches are more cyclical/discretionary than daily staples",
    ],

    "moat_factors": [
        {"factor": "Trust & Purity Assurance Brand", "description": "A branded jewellery retailer's certified purity/hallmarking and buy-back guarantees address the Indian consumer's biggest historical pain point with unorganised jewellers — a trust moat that's hard to replicate quickly"},
        {"factor": "Store Network & Wedding-Season Scale", "description": "A large-format store network across cities lets a branded player capture high-ticket wedding/festival-season demand that a single-city unorganised jeweller cannot serve at the same scale"},
        {"factor": "Design & Category Diversification", "description": "In-house design capability and diversification across jewellery, watches, and eyewear (as with Titan) reduces single-category cyclicality"},
        {"factor": "Working-Capital & Sourcing Scale", "description": "Scale in gold sourcing/hedging and access to cheaper working-capital financing than smaller unorganised players supports better margins at similar price points"},
    ],

    "bull_case": [
        "Continuing formalisation of Indian jewellery retail (organised players taking share from unorganised, aided by hallmarking mandates) supporting structural volume growth",
        "Rising discretionary income supporting premiumisation in watches, eyewear, and diamond jewellery",
        "Store network expansion into smaller cities capturing under-penetrated demand",
        "Wedding/festival-season demand providing a structurally resilient demand floor in the Indian market",
    ],

    "bear_case": [
        "A sharp, sustained gold-price rally suppressing volume growth even as revenue is inflated by price alone",
        "Unorganised-sector competition remaining resilient on price/tax arbitrage, limiting share gains for organised players",
        "A discretionary-spending slowdown disproportionately hitting big-ticket jewellery and watch purchases",
        "Regulatory changes (import duty, hallmarking cost, cash-transaction rules) raising compliance costs",
    ],

    "red_flags": [
        {"condition": "ebitda_margin < 6", "severity": "high",   "message": "EBITDA margin < 6% — thin even for a low-margin, high-turnover jewellery retail model; check discounting intensity or gold-price hedging losses"},
        {"condition": "revenue_growth < 0", "severity": "high", "message": "Negative revenue growth — check whether this reflects a genuine volume decline or just a high gold-price base effect from the prior year"},
        {"condition": "de_ratio > 1.5",     "severity": "medium", "message": "D/E > 1.5x — check whether this is working-capital debt for gold inventory (less concerning) or structural leverage (more concerning)"},
    ],

    "valuation": {
        "primary":   ["P/E", "EV/EBITDA"],
        "secondary": ["P/B", "EV/Sales"],
        "bands": {
            "pe_ratio": {"attractive": (0, 40), "fair": (40, 70), "expensive": (70, 999)},
        },
        "notes": (
            "Branded jewellery/luxury retailers (especially the sector leader) have historically commanded "
            "premium P/E multiples reflecting the formalisation/market-share-gain story, not just current "
            "earnings — but that premium is sensitive to any slowdown in the organised-vs-unorganised "
            "share-gain narrative."
        ),
    },

    "llm_context": (
        "This is a LUXURY GOODS / JEWELLERY RETAIL company (e.g. Titan Company, Kalyan Jewellers, PC "
        "Jeweller) selling branded jewellery, watches, or eyewear. Two things make this sector's numbers "
        "look different from a normal retailer's: (1) gold-price pass-through means headline revenue "
        "growth can be inflated or deflated by bullion price moves independent of actual volume — read it "
        "alongside same-store-sales or grams-sold growth where available, and (2) working capital is "
        "unusually heavy due to high-value gold/diamond inventory, so debt tied to inventory financing is "
        "less concerning than the same D/E ratio would be for a typical retailer. The central competitive "
        "narrative is organised (branded, hallmark-certified) players gaining share from a still-large "
        "unorganised jewellery retail sector — frame growth and moat assessment around that dynamic."
    ),
}
