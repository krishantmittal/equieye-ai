# modules/sectors/media.py
"""
Media, Broadcasting & Entertainment — Sector Module
Covers TV broadcasters/GECs, news networks, print & digital media,
film/content production studios, and cinema exhibition (multiplex) chains
— e.g. Network18, TV18 Broadcast, Zee Entertainment, Sun TV Network,
PVR Inox, Dish TV.
"""

SECTOR_CONFIG: dict = {
    "slug": "media",
    "display_name": "Media & Entertainment",

    "key_metrics": [
        {"id": "ad_revenue_growth",       "label": "Ad Revenue Growth (YoY)",     "unit": "%", "yf_key": None,           "higher_is_better": True},
        {"id": "subscription_revenue_growth", "label": "Subscription Rev. Growth", "unit": "%", "yf_key": None,           "higher_is_better": True},
        {"id": "ebitda_margin",           "label": "EBITDA Margin",                "unit": "%", "yf_key": "ebitdaMargins", "higher_is_better": True},
        {"id": "content_cost_to_revenue", "label": "Content Cost / Revenue",       "unit": "%", "yf_key": None,           "higher_is_better": False},
        {"id": "viewership_share",        "label": "Viewership / GRP Share",       "unit": "%", "yf_key": None,           "higher_is_better": True},
        {"id": "revenue_growth",          "label": "Revenue Growth (YoY)",         "unit": "%", "yf_key": "revenueGrowth", "higher_is_better": True},
        {"id": "de_ratio",                "label": "Debt/Equity",                  "unit": "x", "yf_key": "debtToEquity",  "higher_is_better": False},
    ],

    "scoring_rules": [
        {"metric": "ad_revenue_growth",       "op": ">", "threshold": 12.0, "points": 20, "max": 20},
        {"metric": "ad_revenue_growth",       "op": ">", "threshold": 5.0,  "points": 12, "max": 20},
        {"metric": "ebitda_margin",           "op": ">", "threshold": 25.0, "points": 20, "max": 20},
        {"metric": "ebitda_margin",           "op": ">", "threshold": 15.0, "points": 12, "max": 20},
        {"metric": "content_cost_to_revenue", "op": "<", "threshold": 35.0, "points": 15, "max": 15},
        {"metric": "content_cost_to_revenue", "op": "<", "threshold": 50.0, "points": 8,  "max": 15},
        {"metric": "subscription_revenue_growth", "op": ">", "threshold": 8.0, "points": 15, "max": 15},
        {"metric": "viewership_share",        "op": ">", "threshold": 20.0, "points": 15, "max": 15},
        {"metric": "de_ratio",                "op": "<", "threshold": 0.5,  "points": 15, "max": 15},
        {"metric": "de_ratio",                "op": "<", "threshold": 1.0,  "points": 8,  "max": 15},
    ],
    "score_max": 100,

    "risk_factors": [
        "Ad-spend cyclicality — advertising budgets are among the first cut in an economic slowdown",
        "Audience fragmentation as viewers shift from linear TV to OTT/digital and short-form video",
        "Content cost inflation (sports rights, star talent, production) without commensurate pricing power",
        "Regulatory exposure (TRAI tariff orders, cross-media ownership rules, content/censorship regulation)",
        "Piracy and unauthorised redistribution eroding subscription and box-office revenue",
        "Promoter/related-party concentration common in Indian media groups, raising governance scrutiny",
        "Cord-cutting and DTH/cable subscriber decline pressuring distribution revenue for broadcasters",
    ],

    "moat_factors": [
        {"factor": "Content Library / IP",  "description": "Owned film/show libraries and franchises generate durable syndication and licensing revenue"},
        {"factor": "Channel Distribution",  "description": "Bouquet strength and must-carry/prime placement on cable & DTH platforms raises switching friction for MSOs"},
        {"factor": "Brand & Viewership Habit", "description": "Long-run news/GEC brand recall drives default viewership and appointment-based ratings"},
        {"factor": "Sports & Marquee Rights", "description": "Exclusive sports or event broadcast rights are a scarce, hard-to-replicate draw for advertisers"},
        {"factor": "Regional Language Dominance", "description": "Deep regional-language content moats (e.g. South Indian GECs) are difficult for national players to contest"},
    ],

    "bull_case": [
        "Ad-market recovery driving double-digit growth off a cyclically depressed base",
        "Successful OTT/digital pivot converting linear-TV decline into a new subscription revenue stream",
        "Operating leverage as content costs are amortised over a growing, digitally-distributed audience",
        "Consolidation among broadcasters reducing content-cost bidding wars (e.g. sports rights)",
        "Regional-language and news franchise strength defending share against larger national competitors",
    ],

    "bear_case": [
        "Structural ad-spend migration to global digital/social platforms (Google, Meta) bypassing traditional media entirely",
        "Continued linear TV subscriber erosion from cord-cutting without offsetting digital monetisation",
        "Content cost inflation (sports rights renewal, star fees) outpacing revenue growth and compressing margins",
        "Promoter-group related-party transactions or governance concerns triggering a valuation discount",
        "Regulatory tariff changes (TRAI) or ownership caps disrupting the existing distribution economics",
    ],

    "red_flags": [
        {"condition": "de_ratio > 1.5",                "severity": "high",   "message": "D/E > 1.5x — high leverage for a business with cyclical ad-revenue cash flows"},
        {"condition": "ebitda_margin < 10",             "severity": "high",   "message": "EBITDA margin < 10% — weak profitability, likely content-cost or ad-market pressure"},
        {"condition": "content_cost_to_revenue > 60",   "severity": "medium", "message": "Content cost > 60% of revenue — thin cushion against further cost inflation"},
        {"condition": "revenue_growth < -5",            "severity": "high",   "message": "Revenue declining >5% YoY — ad-market or subscriber base contracting"},
        {"condition": "ad_revenue_growth < 0",           "severity": "medium", "message": "Ad revenue shrinking — core linear/broadcast monetisation under pressure"},
    ],

    "valuation": {
        "primary":   ["EV/EBITDA", "P/E Ratio"],
        "secondary": ["Price/Sales (pre-profit digital/OTT arms)"],
        "notes": (
            "Traditional broadcasters and multiplex operators are typically valued on EV/EBITDA "
            "(content amortisation and depreciation distort P/E), generally in the high-single to "
            "low-double digits for Indian peers. Profitable, well-capitalised media companies can "
            "be cross-checked on P/E. Loss-making digital/OTT-only arms are better assessed on "
            "Price/Sales until profitability is established."
        ),
        "bands": {
            "ev_ebitda": {"attractive": (0, 8), "fair": (8, 14), "expensive": (14, 999)},
            "pe_ratio":  {"attractive": (0, 15), "fair": (15, 28), "expensive": (28, 999)},
        },
    },

    "llm_context": (
        "This is a MEDIA / BROADCASTING / ENTERTAINMENT company (TV channels/GEC, news network, "
        "print or digital media, film/content production, or cinema exhibition). Focus on: "
        "ad-revenue cyclicality and its dependence on the broader economy, the linear-TV-to-digital/OTT "
        "transition and how well the company is monetising it, content cost trends (sports rights, "
        "production, talent) relative to revenue, EBITDA margin resilience, and leverage. Value primarily "
        "on EV/EBITDA rather than P/E, since depreciation/content amortisation can distort reported "
        "earnings. Flag promoter/related-party governance concerns where relevant — common in Indian "
        "media conglomerates — and do not assume a sports-rights or content-cost step-up is one-off "
        "unless the company has explicitly said so."
    ),
}
