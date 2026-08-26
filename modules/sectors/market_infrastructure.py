# modules/sectors/market_infrastructure.py
"""
Financial Market Infrastructure (Exchanges & Depositories) — Sector Module
===========================================================================
For BSE Ltd, Central Depository Services (CDSL), Multi Commodity Exchange
(MCX) and similar market-infrastructure institutions.

Was previously falling through to "generic". These are NOT brokers —
they don't take client trading risk or compete for retail wallet share.
They are regulated, often near-monopoly (in their specific market segment)
transaction-processing utilities that earn a small, fixed fee per trade/
transaction/account, with revenue almost mechanically tied to market-wide
trading volumes and new demat-account growth rather than any individual
company's execution. Structurally different bull/bear drivers (market
turnover, new-investor-account growth, regulatory fee caps) than a
brokerage, which competes on client acquisition, margin funding, and
research/service quality.
"""

SECTOR_CONFIG: dict = {
    "slug": "market_infrastructure",
    "display_name": "Financial Market Infrastructure (Exchanges/Depositories)",

    "key_metrics": [
        {"id": "market_turnover_growth", "label": "Market Turnover / Volume Growth (YoY)", "unit": "%", "yf_key": None, "higher_is_better": True},
        {"id": "new_accounts_growth",    "label": "New Demat/Trading Account Growth",      "unit": "%", "yf_key": None, "higher_is_better": True},
        {"id": "revenue_growth",         "label": "Revenue Growth (YoY)",                  "unit": "%", "yf_key": "revenueGrowth", "higher_is_better": True},
        {"id": "operating_margin",       "label": "Operating Margin",                       "unit": "%", "yf_key": "operatingMargins", "higher_is_better": True},
        {"id": "roe",                    "label": "Return on Equity",                       "unit": "%", "yf_key": "returnOnEquity", "higher_is_better": True},
        {"id": "market_share",           "label": "Segment Market Share",                   "unit": "%", "yf_key": None, "higher_is_better": True},
    ],

    "scoring_rules": [
        {"metric": "revenue_growth",   "op": ">", "threshold": 20.0, "points": 20, "max": 20},
        {"metric": "revenue_growth",   "op": ">", "threshold": 10.0, "points": 12, "max": 20},
        {"metric": "operating_margin", "op": ">", "threshold": 55.0, "points": 30, "max": 30},
        {"metric": "operating_margin", "op": ">", "threshold": 40.0, "points": 18, "max": 30},
        {"metric": "roe",              "op": ">", "threshold": 20.0, "points": 25, "max": 25},
        {"metric": "roe",              "op": ">", "threshold": 12.0, "points": 15, "max": 25},
        {"metric": "de_ratio",         "op": "<", "threshold": 0.2,  "points": 15, "max": 15},
    ],
    "score_max": 100,

    "risk_factors": [
        "Revenue is directly tied to market-wide trading turnover/volumes — a prolonged bear market or a sharp drop in retail participation compresses transaction revenue with no offsetting lever",
        "SEBI periodically reviews transaction charges and fee structures (e.g. options-lot-size changes, transaction-fee caps) — a direct, mechanical hit to per-trade revenue",
        "Segment concentration risk — a single-product exchange (e.g. a commodity exchange dependent on a few key contracts) is more exposed to a regulatory or product-specific volume shock than a diversified exchange",
        "Regulatory approval is required for new products/contracts, and delays or rejections directly cap growth avenues",
        "Competitive/regulatory risk of new exchange licences being granted, eroding the near-monopoly position in a specific segment",
    ],

    "moat_factors": [
        {"factor": "Regulatory Licence Scarcity", "description": "Operating a stock/commodity exchange or a securities depository requires a SEBI licence that is granted to very few entities — a structural, government-gated near-monopoly or duopoly in each specific market segment"},
        {"factor": "Network Effects", "description": "Liquidity begets liquidity — traders go where order books are deepest, and brokers/depository-participants integrate with the dominant player, making it very hard for a new entrant to bootstrap volume away from the incumbent"},
        {"factor": "High Operating Leverage on a Technology Platform", "description": "Once the trading/settlement technology platform is built, incremental transaction volume carries very low marginal cost, driving industry-leading operating margins for the scale leader"},
        {"factor": "Mandatory Participation", "description": "Market participants (brokers, depository participants, institutional investors) have no practical alternative to using the exchange/depository for a given asset class, creating captive, recurring transaction revenue"},
    ],

    "bull_case": [
        "Structural growth in Indian retail equity/derivatives participation and new demat account additions expanding the addressable transaction base",
        "New product launches (index derivatives, commodity contracts, new asset classes) adding incremental, high-margin transaction revenue",
        "Operating leverage on a largely fixed technology cost base as volumes grow",
        "Market-share gains in a specific segment (e.g. options, a commodity contract) versus a competing exchange",
    ],

    "bear_case": [
        "A prolonged equity/commodity bear market or a sharp regulatory-driven drop in retail derivatives participation (e.g. tighter futures & options eligibility norms) compressing turnover",
        "SEBI fee-structure or lot-size changes mechanically reducing per-trade revenue",
        "Loss of market share in a key product/segment to a competing exchange",
        "Regulatory delay or rejection of new product approvals capping growth avenues",
    ],

    "red_flags": [
        {"condition": "operating_margin < 30", "severity": "high",   "message": "Operating margin < 30% — low for a market-infrastructure utility; check for a one-off cost or fee-structure change"},
        {"condition": "revenue_growth < 0",     "severity": "high",   "message": "Negative revenue growth — check whether this reflects falling market-wide turnover, a regulatory fee cut, or share loss to a competing exchange"},
        {"condition": "de_ratio > 0.5",         "severity": "medium", "message": "D/E > 0.5x — unusually leveraged for this typically capital-light, cash-generative business model"},
    ],

    "valuation": {
        "primary":   ["P/E", "EV/EBITDA"],
        "secondary": ["P/B", "Dividend Yield"],
        "notes": (
            "Exchanges and depositories typically command premium multiples reflecting their near-monopoly, "
            "high-margin, high-ROE profile — but because revenue tracks market-wide turnover, earnings (and "
            "therefore trailing multiples) can look artificially cheap at a market-activity peak and "
            "expensive at a lull. Normalise for the market-cycle stage before comparing across time."
        ),
    },

    "llm_context": (
        "This is a FINANCIAL MARKET INFRASTRUCTURE company — a stock/commodity EXCHANGE or a securities "
        "DEPOSITORY (e.g. BSE Ltd, CDSL, MCX) — NOT a broker. It doesn't take client trading risk, compete "
        "for retail investor wallet share, or offer margin funding/research — it's a regulated, near-"
        "monopoly transaction-processing utility earning a small, largely fixed fee per trade/transaction/"
        "account. Revenue is mechanically tied to market-wide trading turnover and new-account growth "
        "rather than to any individual company's client-acquisition execution — do NOT apply brokerage-style "
        "framing (client acquisition cost, margin funding book, research quality) here. The single biggest "
        "sector-specific regulatory risk is SEBI's periodic transaction-fee or derivatives-lot-size "
        "structure reviews, which directly and mechanically change per-trade revenue."
    ),
}
