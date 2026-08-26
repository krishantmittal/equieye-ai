# modules/sectors/consumer_internet.py
"""
Consumer Internet / E-commerce / Platform Businesses — Sector Module
"""

SECTOR_CONFIG: dict = {
    "slug": "consumer_internet",
    "display_name": "Consumer Internet",

    "key_metrics": [
        {"id": "gmv",               "label": "Gross Merchandise Value (GMV)", "unit": "₹Cr", "yf_key": None, "higher_is_better": True},
        {"id": "take_rate",         "label": "Take Rate",              "unit": "%",  "yf_key": None, "higher_is_better": True},
        {"id": "monthly_active_users", "label": "Monthly Active Users", "unit": "count", "yf_key": None, "higher_is_better": True},
        {"id": "contribution_margin", "label": "Contribution Margin",  "unit": "%",  "yf_key": None, "higher_is_better": True},
        {"id": "revenue_growth",   "label": "Revenue Growth",          "unit": "%",  "yf_key": None, "higher_is_better": True},
    ],

    "risk_factors": [
        "Path to profitability risk — many consumer internet businesses are still cash-burning at scale",
        "Intense, well-funded competition driving discounting wars that compress unit economics",
        "High customer acquisition cost (CAC) relative to lifetime value in early-stage platforms",
        "Regulatory risk (data privacy, FDI rules for e-commerce/marketplaces, gig-worker regulation)",
        "Platform/network effects can reverse quickly if a well-funded competitor undercuts on price",
        "Dependence on continued external funding if free cash flow remains negative",
    ],

    "moat_factors": [
        {"factor": "Network Effects",       "description": "More buyers attract more sellers (and vice versa), reinforcing platform dominance"},
        {"factor": "Brand / Habit",         "description": "Top-of-mind brand recall drives repeat usage without paid acquisition"},
        {"factor": "Data Advantage",        "description": "Scale of transaction/user data improves recommendations, pricing, and fraud detection"},
        {"factor": "Logistics / Fulfilment", "description": "Owned delivery infrastructure is a real, capital-intensive barrier to replicate"},
        {"factor": "Switching Costs",       "description": "Integrated wallets, saved preferences, or loyalty programs raise the cost of switching platforms"},
    ],

    "bull_case": [
        "Path to profitability visible via improving contribution margins and reducing cash burn",
        "Market leadership position defensible against well-funded but distant competitors",
        "Rising monetisation (ads, take rate, premium features) without hurting user growth",
        "Expanding total addressable market as internet/smartphone penetration grows",
        "Operating leverage as fixed technology/logistics costs are spread over growing GMV",
    ],

    "bear_case": [
        "Continued cash burn with no clear, near-term path to sustainable profitability",
        "Well-funded competitor triggers a discounting war, resetting unit economics industry-wide",
        "Regulatory action (FDI rules, gig-worker classification, data privacy) disrupting the business model",
        "User/GMV growth slowing as the market matures and easy growth is exhausted",
        "Dependence on future capital raises if free cash flow remains structurally negative",
    ],

    "red_flags": [
        {"condition": "profit_margin < -20", "severity": "high",   "message": "Net margin below -20% — significant, ongoing cash burn"},
        {"condition": "de_ratio > 1.5",      "severity": "medium", "message": "D/E > 1.5x — elevated leverage for a business without stable profitability"},
    ],

    "valuation": {
        "primary":   ["Price/Sales", "EV/GMV"],
        "secondary": ["PEG (once profitable)"],
        "notes": (
            "Pre-profit consumer internet businesses should not be valued on P/E — Price/Sales (or EV/GMV "
            "for marketplace models) is the standard metric until the business demonstrates sustained "
            "profitability, at which point PEG becomes more relevant."
        ),
        "bands": {
            "price_to_sales": {"attractive": (0, 3), "fair": (3, 8), "expensive": (8, 999)},
        },
    },

    "llm_context": (
        "This is a CONSUMER INTERNET / E-COMMERCE / PLATFORM business (marketplace, food delivery, "
        "quick-commerce, etc.). Focus on: path to profitability (contribution margin trend, not just "
        "revenue growth), competitive intensity and discounting dynamics, network effects and their "
        "durability, and regulatory exposure. Do not judge these companies on trailing P/E — most are "
        "pre-profit by design during their growth phase, and the right question is whether unit economics "
        "are improving, not whether GAAP profit exists yet."
    ),
}
