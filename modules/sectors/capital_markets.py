# modules/sectors/capital_markets.py
"""
Capital Markets (Brokerage & Wealth Management) — Sector Module
=================================================================
For Angel One, ICICI Securities, Motilal Oswal Financial Services and
similar broker/wealth-management firms.

Was previously falling through to "generic". A brokerage's economics are
driven by client acquisition, active-client counts, average revenue per
client, margin-trading-funding (MTF) book size, and market-wide retail
trading activity — a fundamentally different model from a bank (no
deposit-taking, no NPA risk in the traditional sense) or an exchange (a
broker competes for clients and takes some balance-sheet risk via MTF,
unlike the fee-utility exchange model). Discount-broking price
competition has structurally compressed yields industry-wide over the
last several years, a dynamic a generic financial-services lens misses
entirely.
"""

SECTOR_CONFIG: dict = {
    "slug": "capital_markets",
    "display_name": "Capital Markets (Brokerage & Wealth Management)",

    "key_metrics": [
        {"id": "active_client_growth", "label": "Active Client Growth (YoY)",       "unit": "%", "yf_key": None, "higher_is_better": True},
        {"id": "revenue_growth",       "label": "Revenue Growth (YoY)",             "unit": "%", "yf_key": "revenueGrowth", "higher_is_better": True},
        {"id": "mtf_book_growth",      "label": "Margin Trading Funding Book Growth", "unit": "%", "yf_key": None, "higher_is_better": True},
        {"id": "operating_margin",     "label": "Operating Margin",                  "unit": "%", "yf_key": "operatingMargins", "higher_is_better": True},
        {"id": "roe",                  "label": "Return on Equity",                  "unit": "%", "yf_key": "returnOnEquity", "higher_is_better": True},
        {"id": "de_ratio",             "label": "Debt/Equity (MTF-book-funded)",     "unit": "x", "yf_key": "debtToEquity", "higher_is_better": False},
    ],

    "scoring_rules": [
        {"metric": "revenue_growth",   "op": ">", "threshold": 20.0, "points": 20, "max": 20},
        {"metric": "revenue_growth",   "op": ">", "threshold": 10.0, "points": 12, "max": 20},
        {"metric": "operating_margin", "op": ">", "threshold": 40.0, "points": 25, "max": 25},
        {"metric": "operating_margin", "op": ">", "threshold": 28.0, "points": 15, "max": 25},
        {"metric": "roe",              "op": ">", "threshold": 25.0, "points": 25, "max": 25},
        {"metric": "roe",              "op": ">", "threshold": 15.0, "points": 15, "max": 25},
        {"metric": "active_client_growth", "op": ">", "threshold": 15.0, "points": 15, "max": 15},
    ],
    "score_max": 100,

    "risk_factors": [
        "Revenue is highly correlated with market-wide retail trading activity (especially derivatives volumes) — a bear market or a regulatory clampdown on retail F&O participation directly hits both volumes and yield",
        "Structural, industry-wide brokerage-yield compression from discount-broking price competition over the last several years",
        "Margin Trading Funding (MTF) book carries genuine credit and market risk (collateral value can fall faster than the broker can recover the loan in a sharp downturn)",
        "SEBI regulatory changes to derivatives lot sizes, expiry-day rules, or retail F&O eligibility norms can sharply reduce the highest-yield revenue segment",
        "Client-acquisition cost competition among brokers can compress incremental profitability even as headline client counts grow",
    ],

    "moat_factors": [
        {"factor": "Digital Platform Scale & Brand", "description": "A widely recognised trading app/platform with a large existing active-client base benefits from lower incremental client-acquisition cost and network-driven word-of-mouth versus a new entrant"},
        {"factor": "Cross-Sell into Wealth & Lending Products", "description": "Cross-selling MTF, loans against securities, mutual funds, and insurance to an existing trading client base diversifies revenue beyond pure brokerage and raises revenue per client"},
        {"factor": "Parent-Group Bank/Distribution Backing", "description": "Bank-affiliated brokers (e.g. ICICI Securities) benefit from cross-sell through the parent bank's branch network and existing customer base, a channel a standalone discount broker lacks"},
        {"factor": "Research & Advisory Relationships", "description": "Full-service brokers with strong research franchises retain higher-value, less price-sensitive clients (HNI/institutional) than a pure execution-only discount broker"},
    ],

    "bull_case": [
        "Continuing growth in Indian retail participation in equities and derivatives, expanding the addressable client and trading-volume base",
        "Diversification into MTF, wealth management, and lending products raising revenue per client beyond pure brokerage yield",
        "Operating leverage on a largely fixed technology/compliance cost base as active client counts scale",
        "Consolidation of market share by well-capitalised, digitally scaled brokers at the expense of smaller sub-scale players",
    ],

    "bear_case": [
        "A sustained equity/derivatives bear market sharply reducing retail trading volumes and brokerage revenue",
        "Further SEBI restrictions on retail F&O participation (lot sizes, eligibility, expiry rules) structurally shrinking the highest-yield revenue segment",
        "Continued discount-broking price competition further compressing yield per trade",
        "MTF book credit losses in a sharp market downturn if collateral values fall faster than positions can be unwound",
    ],

    "red_flags": [
        {"condition": "operating_margin < 20", "severity": "high",   "message": "Operating margin < 20% — low for the sector; check for a client-acquisition cost spike or a yield-compression event"},
        {"condition": "revenue_growth < 0",     "severity": "high",   "message": "Negative revenue growth — check whether this reflects lower market-wide trading activity, a regulatory F&O restriction, or client-share loss"},
        {"condition": "de_ratio > 3",            "severity": "medium", "message": "D/E > 3x — check whether this is MTF-book funding debt (routine for this business) versus structural leverage; MTF-funded debt is backed by pledged securities collateral"},
    ],

    "valuation": {
        "primary":   ["P/E", "EV/EBITDA"],
        "secondary": ["P/B", "Dividend Yield"],
        "notes": (
            "Brokerage earnings are highly cyclical with market-wide trading activity, so a single-year P/E "
            "can look deceptively cheap at a trading-volume peak and expensive in a lull — compare across a "
            "full market cycle and cross-check against active-client and revenue-per-client trends rather "
            "than a single year's multiple."
        ),
    },

    "llm_context": (
        "This is a CAPITAL MARKETS / BROKERAGE & WEALTH MANAGEMENT company (e.g. Angel One, ICICI "
        "Securities, Motilal Oswal Financial Services) — NOT an exchange or depository (that's the "
        "market_infrastructure sector) and NOT a bank/NBFC in the traditional deposit-taking or asset-"
        "finance sense. Its economics are driven by active-client counts, revenue per client, Margin "
        "Trading Funding (MTF) book size, and market-wide retail trading/derivatives activity. The dominant "
        "structural industry dynamic of the last several years is discount-broking price competition "
        "compressing brokerage yield industry-wide — factor this into growth and margin assessment even for "
        "the market-share leader. Distinguish MTF-book debt (collateral-backed, routine for this business) "
        "from other leverage when assessing balance-sheet risk."
    ),
}
