# modules/sectors/retail_apparel.py
"""
Apparel & Department Store Retail — Sector Module
==================================================
For Trent (Westside/Zudio), V-Mart Retail, Shoppers Stop and similar
multi-brand fashion/department-store retailers.

Was previously falling through to "generic". Like QSR and hotels, this
is a same-store-sales/network-expansion-driven, lease-heavy retail
business — but unlike QSR, the core competitive lever is private-label
fashion sourcing/merchandising margin and format economics (large-format
department store vs value/discount format), not franchise royalties.
"""

SECTOR_CONFIG: dict = {
    "slug": "retail_apparel",
    "display_name": "Apparel & Department Store Retail",

    "key_metrics": [
        {"id": "same_store_sales_growth", "label": "Same-Store Sales Growth (SSSG)", "unit": "%", "yf_key": None, "higher_is_better": True},
        {"id": "store_area_growth",       "label": "Retail Area Growth (YoY)",       "unit": "%", "yf_key": None, "higher_is_better": True},
        {"id": "revenue_growth",          "label": "Revenue Growth (YoY)",           "unit": "%", "yf_key": "revenueGrowth", "higher_is_better": True},
        {"id": "gross_margin",            "label": "Gross Margin",                   "unit": "%", "yf_key": "grossMargins", "higher_is_better": True},
        {"id": "ebitda_margin",           "label": "EBITDA Margin",                   "unit": "%", "yf_key": "ebitdaMargins", "higher_is_better": True},
        {"id": "de_ratio",                "label": "Debt/Equity (lease-heavy)",       "unit": "x", "yf_key": "debtToEquity", "higher_is_better": False},
    ],

    "scoring_rules": [
        {"metric": "revenue_growth", "op": ">", "threshold": 20.0, "points": 20, "max": 20},
        {"metric": "revenue_growth", "op": ">", "threshold": 10.0, "points": 12, "max": 20},
        {"metric": "ebitda_margin",  "op": ">", "threshold": 15.0, "points": 25, "max": 25},
        {"metric": "ebitda_margin",  "op": ">", "threshold": 8.0,  "points": 15, "max": 25},
        {"metric": "same_store_sales_growth", "op": ">", "threshold": 8.0, "points": 25, "max": 25},
        {"metric": "same_store_sales_growth", "op": ">", "threshold": 3.0, "points": 15, "max": 25},
        {"metric": "store_area_growth", "op": ">", "threshold": 15.0, "points": 15, "max": 15},
    ],
    "score_max": 100,

    "risk_factors": [
        "Same-store-sales growth can mask underlying weakness even as total revenue grows purely from new store/area additions",
        "Fashion-inventory risk — unsold seasonal apparel stock forces margin-eroding end-of-season discounting",
        "Ind AS 116 lease-capitalisation inflates reported D/E for a large-format, lease-heavy retail network — similar caveat to QSR/airlines",
        "Discretionary-spending exposure — apparel/department-store purchases are more cyclical than daily-staple retail",
        "E-commerce and quick-commerce competition for share of discretionary retail wallet, particularly in value/fashion categories",
        "Private-label sourcing/supply-chain execution risk — a merchandising misstep (wrong assortment, late deliveries) directly hits SSSG",
    ],

    "moat_factors": [
        {"factor": "Private-Label Merchandising Capability", "description": "In-house design, sourcing, and fast-fashion private-label execution (e.g. Zudio's value fast-fashion model) captures higher gross margin than a pure third-party-brand retailer and is difficult for a new entrant to replicate quickly"},
        {"factor": "Format & Real-Estate Selection Expertise", "description": "Site-selection and format expertise (large-format department stores in malls/high streets, or compact value-format stores in dense markets) built over years of network expansion is a genuine operating-execution moat"},
        {"factor": "Scale Sourcing Economics", "description": "Large-scale sourcing volume gives cost advantages in private-label manufacturing that a smaller regional retailer cannot match"},
        {"factor": "Brand Portfolio & Store-Format Diversification", "description": "Operating multiple store formats/brands targeting different price points (value, mid-market, premium) diversifies demand exposure versus a single-format competitor"},
    ],

    "bull_case": [
        "Structural growth in India's organised retail penetration (still low versus developed markets) supporting store-network expansion",
        "Private-label/fast-fashion value formats gaining share from both unorganised retail and higher-priced branded competitors",
        "Store-network expansion into tier-2/3 cities extending the addressable market",
        "Improving same-store-sales productivity as newer stores mature and merchandising is optimised",
    ],

    "bear_case": [
        "Weak or negative same-store-sales growth masked by new-store revenue contribution",
        "A discretionary-spending slowdown disproportionately hitting apparel/department-store purchases",
        "Unsold seasonal inventory forcing heavy discounting that compresses gross margin",
        "E-commerce/quick-commerce share gains eroding footfall at physical large-format stores",
    ],

    "red_flags": [
        {"condition": "same_store_sales_growth < 0", "severity": "high",   "message": "Negative same-store-sales growth — underlying per-store demand is shrinking even if total revenue is still growing from new stores"},
        {"condition": "ebitda_margin < 6",            "severity": "high",   "message": "EBITDA margin < 6% — thin; check for heavy discounting or unsold inventory write-downs"},
        {"condition": "revenue_growth < 0",           "severity": "medium", "message": "Negative total revenue growth — check whether store closures, weak SSSG, or both are the driver"},
    ],

    "valuation": {
        "primary":   ["EV/EBITDA", "P/E"],
        "secondary": ["EV/Store", "P/B"],
        "notes": (
            "Fast-growing private-label/value-format retailers (e.g. Trent) often trade on growth-story "
            "multiples reflecting store-network runway, while more mature department-store formats trade "
            "closer to a standard retail P/E — check which growth phase the specific company is in before "
            "benchmarking its multiple against sector averages."
        ),
    },

    "llm_context": (
        "This is an APPAREL / DEPARTMENT STORE RETAIL company (e.g. Trent/Westside-Zudio, V-Mart Retail, "
        "Shoppers Stop). Like QSR, the key operating metric is Same-Store-Sales Growth (SSSG) — always read "
        "it separately from total revenue growth, since new store/area additions can mask deteriorating "
        "per-store demand. Distinguish private-label/fast-fashion value-format retailers (higher gross "
        "margin, merchandising-execution-driven moat) from traditional third-party-brand department stores "
        "(thinner margin, more real-estate/footfall-driven) — these have different margin profiles. "
        "LEVERAGE: Ind AS 116 lease capitalisation inflates reported D/E for this lease-heavy, large-format "
        "retail model — don't apply a flat industrial D/E benchmark without accounting for this."
    ),
}
