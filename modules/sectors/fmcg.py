# modules/sectors/fmcg.py
"""
FMCG (Fast Moving Consumer Goods) — Sector Module
"""

SECTOR_CONFIG: dict = {
    "slug": "fmcg",
    "display_name": "FMCG",

    "key_metrics": [
        {"id": "revenue_growth",   "label": "Revenue Growth (YoY)",     "unit": "%", "yf_key": "revenueGrowth",  "higher_is_better": True},
        {"id": "volume_growth",    "label": "Volume Growth",            "unit": "%", "yf_key": None,             "higher_is_better": True},
        {"id": "gross_margin",     "label": "Gross Margin",             "unit": "%", "yf_key": "grossMargins",   "higher_is_better": True},
        {"id": "ebitda_margin",    "label": "EBITDA Margin",            "unit": "%", "yf_key": "ebitdaMargins",  "higher_is_better": True},
        {"id": "ad_spend_pct",     "label": "Ad Spend (% of Revenue)",  "unit": "%", "yf_key": None,             "higher_is_better": True},
        {"id": "rural_mix",        "label": "Rural Revenue Mix",        "unit": "%", "yf_key": None,             "higher_is_better": True},
        {"id": "roce",             "label": "Return on Capital Employed","unit": "%","yf_key": "returnOnEquity", "higher_is_better": True},
        {"id": "de_ratio",         "label": "Debt/Equity",              "unit": "x", "yf_key": "debtToEquity",   "higher_is_better": False},
    ],

    "scoring_rules": [
        {"metric": "volume_growth",  "op": ">", "threshold": 8.0,  "points": 20, "max": 20},
        {"metric": "volume_growth",  "op": ">", "threshold": 4.0,  "points": 12, "max": 20},
        {"metric": "volume_growth",  "op": ">", "threshold": 0.0,  "points": 5,  "max": 20},
        {"metric": "ebitda_margin",  "op": ">", "threshold": 22.0, "points": 20, "max": 20},
        {"metric": "ebitda_margin",  "op": ">", "threshold": 16.0, "points": 12, "max": 20},
        {"metric": "ebitda_margin",  "op": ">", "threshold": 10.0, "points": 6,  "max": 20},
        {"metric": "roce",           "op": ">", "threshold": 30.0, "points": 20, "max": 20},
        {"metric": "roce",           "op": ">", "threshold": 20.0, "points": 12, "max": 20},
        {"metric": "de_ratio",       "op": "<", "threshold": 0.3,  "points": 15, "max": 15},
        {"metric": "gross_margin",   "op": ">", "threshold": 45.0, "points": 10, "max": 10},
    ],
    "score_max": 100,

    "risk_factors": [
        "Input cost inflation (palm oil, crude derivatives, agri commodities) compressing gross margin",
        "Private-label/regional brand competition eroding share in price-sensitive categories",
        "Rural demand slowdown — rural is typically 35-45% of volumes for staples",
        "GST/regulatory changes on packaging or essential goods taxation",
        "Distribution disruption from quick-commerce reshaping go-to-market economics",
        "Premiumisation reversal in a weak consumption environment",
    ],

    "moat_factors": [
        {"factor": "Brand Equity",         "description": "Decades-old trusted brands command pricing power and top-of-mind recall"},
        {"factor": "Distribution Reach",   "description": "Direct reach to millions of outlets (general trade) is extremely hard to replicate"},
        {"factor": "Portfolio Breadth",    "description": "Multi-category presence spreads risk and leverages shared distribution/manufacturing"},
        {"factor": "Manufacturing Scale",  "description": "Scale lowers unit costs and enables aggressive pricing against regional challengers"},
        {"factor": "R&D / Innovation",     "description": "Consistent new product launches and reformulation defend share against private labels"},
    ],

    "bull_case": [
        "Rural recovery on the back of good monsoon and government transfers boosts volumes",
        "Premiumisation: rising per-capita income shifts mix to higher-margin SKUs",
        "Quick-commerce expansion is a structural tailwind for impulse/replenishment categories",
        "Category expansion into adjacent segments (personal care into wellness, foods into snacking)",
        "Operating leverage as ad spend normalises post a high-investment phase",
    ],

    "bear_case": [
        "Input cost spikes (palm oil, crude) that cannot be fully passed through without volume loss",
        "Aggressive regional/D2C brand competition fragmenting category leadership",
        "Weak rural demand persisting due to inflation eroding real wages",
        "Margin pressure from quick-commerce platform fees and deep discounting",
        "Slowing volume growth masked by price-led revenue growth (low quality growth)",
    ],

    "red_flags": [
        {"condition": "volume_growth < 0",      "severity": "high",   "message": "Negative volume growth — price-led growth is masking demand weakness"},
        {"condition": "gross_margin < 35",       "severity": "medium", "message": "Gross margin < 35% — input cost pressure not being passed through"},
        {"condition": "ebitda_margin < 10",      "severity": "medium", "message": "EBITDA margin < 10% — weak for an FMCG business, check cost structure"},
        {"condition": "ad_spend_pct < 5",        "severity": "low",    "message": "Ad spend < 5% of revenue — brand investment may be under-funded vs peers"},
        {"condition": "de_ratio > 0.5",          "severity": "low",    "message": "D/E > 0.5x — unusual leverage for an asset-light FMCG business"},
    ],

    "valuation": {
        "primary":   ["P/E Ratio", "EV/EBITDA"],
        "secondary": ["P/Sales"],
        "notes": (
            "FMCG leaders command premium P/E (40-60x) for earnings quality, low cyclicality, and high ROCE. "
            "Compression in multiple usually reflects slowing volume growth, not near-term earnings risk. "
            "Watch volume growth (not just revenue growth) — price-led growth is lower quality."
        ),
        "bands": {
            "pe_ratio": {"attractive": (0, 35), "fair": (35, 75), "expensive": (75, 999)},
        },
    },

    "llm_context": (
        "This is an FMCG company. Focus on: volume growth (not just revenue growth), gross margin trends, "
        "rural vs urban mix, ad spend intensity, and ROCE. "
        "Do NOT apply NPA or D/E-heavy industrial analysis — FMCG should be asset-light, high-ROCE, low-debt. "
        "Distinguish volume-led growth (high quality) from price-led growth (lower quality, masks demand weakness). "
        "Quick-commerce disruption to traditional general-trade distribution is a live structural theme to flag."
    ),
}
