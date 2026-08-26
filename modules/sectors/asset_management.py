# modules/sectors/asset_management.py
"""
Asset Management (Mutual Fund AMCs) — Sector Module
====================================================
For HDFC AMC, Nippon Life India AMC, UTI AMC, Aditya Birla Sun Life AMC
and similar listed mutual-fund asset managers.

Was previously falling through to "generic". An AMC's economics are
almost entirely a function of Average Assets Under Management (AUM) and
the blended expense ratio it earns on that AUM — an asset-light,
extremely high-margin, high-ROE model with no meaningful capex or
inventory, closer to a royalty/toll-on-savings business than to a normal
industrial or even a normal financial-services company. SEBI's periodic
total-expense-ratio (TER) regulation is the single biggest structural risk
and doesn't map to any generic "regulatory risk" bucket.
"""

SECTOR_CONFIG: dict = {
    "slug": "asset_management",
    "display_name": "Asset Management (Mutual Fund AMC)",

    "key_metrics": [
        {"id": "aum_growth",        "label": "Average AUM Growth (YoY)",   "unit": "%", "yf_key": None, "higher_is_better": True},
        {"id": "equity_aum_mix",    "label": "Equity AUM Mix",             "unit": "%", "yf_key": None, "higher_is_better": True},
        {"id": "revenue_growth",    "label": "Revenue Growth (YoY)",       "unit": "%", "yf_key": "revenueGrowth", "higher_is_better": True},
        {"id": "operating_margin",  "label": "Operating Margin",           "unit": "%", "yf_key": "operatingMargins", "higher_is_better": True},
        {"id": "roe",               "label": "Return on Equity",           "unit": "%", "yf_key": "returnOnEquity", "higher_is_better": True},
        {"id": "sip_flow_growth",   "label": "SIP Flow Growth (YoY)",      "unit": "%", "yf_key": None, "higher_is_better": True},
    ],

    "scoring_rules": [
        {"metric": "revenue_growth",   "op": ">", "threshold": 18.0, "points": 20, "max": 20},
        {"metric": "revenue_growth",   "op": ">", "threshold": 10.0, "points": 12, "max": 20},
        {"metric": "operating_margin", "op": ">", "threshold": 60.0, "points": 25, "max": 25},
        {"metric": "operating_margin", "op": ">", "threshold": 45.0, "points": 15, "max": 25},
        {"metric": "roe",              "op": ">", "threshold": 30.0, "points": 30, "max": 30},
        {"metric": "roe",              "op": ">", "threshold": 20.0, "points": 18, "max": 30},
        {"metric": "de_ratio",         "op": "<", "threshold": 0.2,  "points": 15, "max": 15},
    ],
    "score_max": 100,

    "risk_factors": [
        "SEBI periodically reviews and has tightened total-expense-ratio (TER) caps — a direct, mechanical hit to revenue per rupee of AUM that isn't offset by volume unless AUM growth compensates",
        "Revenue is a call option on equity-market levels — a sustained market correction reduces both AUM (mark-to-market) and net flows simultaneously (pro-cyclical, not just linear)",
        "Intensifying competition from passive/index funds and low-cost platforms compressing active-fund expense ratios structurally over time",
        "Distribution-commission structure changes (regulatory shifts in how distributors are paid) can affect net flows and channel economics",
        "Concentration in a small number of large equity schemes can make performance-driven redemption risk a bigger swing factor than for a diversified AMC",
    ],

    "moat_factors": [
        {"factor": "Brand & Distribution Reach", "description": "A well-known AMC brand backed by a wide bank/distributor network for SIP and lump-sum inflows is difficult for a new entrant to replicate quickly, especially in a trust-sensitive category like long-term savings"},
        {"factor": "Scale Economics on a Fixed Cost Base", "description": "Fund-management and operational costs don't scale linearly with AUM, so an incumbent with a large AUM base earns structurally higher operating margins than a smaller competitor"},
        {"factor": "Track Record & Sticky SIP Flows", "description": "A long performance track record across market cycles builds retail investor trust, and systematic SIP flows (contractual monthly investments) are stickier than lump-sum flows, providing more predictable AUM growth"},
        {"factor": "Parent-Group Distribution Synergies", "description": "AMCs promoted by large banking/financial-services groups (e.g. HDFC, Nippon Life, ABSL) benefit from cross-sell through the parent's branch and digital distribution network"},
    ],

    "bull_case": [
        "Rising financialisation of Indian household savings (shift from physical assets like gold/real estate toward mutual funds) supporting structural AUM growth",
        "SIP culture deepening penetration into smaller cities, providing a steadier, less market-timing-sensitive flow base",
        "Operating leverage as AUM scales on a largely fixed cost base",
        "Growing share of higher-yielding equity AUM (versus lower-yield debt/liquid AUM) improving blended realisation",
    ],

    "bear_case": [
        "A prolonged equity bear market simultaneously shrinking AUM (mark-to-market) and triggering net outflows",
        "Further SEBI TER cuts mechanically compressing revenue per unit of AUM",
        "Passive/index fund share gains structurally capping active-fund expense ratios over the long term",
        "Distribution-commission or regulatory changes disrupting the channel economics AMCs rely on for net inflows",
    ],

    "red_flags": [
        {"condition": "operating_margin < 35", "severity": "high",   "message": "Operating margin < 35% — unusually low for an AMC; check for a one-off cost or aggressive distributor-commission payout"},
        {"condition": "aum_growth < 0",         "severity": "high",   "message": "Negative AUM growth — check whether this is market-driven (correction) or genuine net-outflow-driven, since the two have very different implications"},
        {"condition": "revenue_growth < 0",     "severity": "medium", "message": "Negative revenue growth — likely reflects either a TER cut, an AUM decline, or an unfavourable mix shift toward lower-yield debt/liquid AUM"},
    ],

    "valuation": {
        "primary":   ["P/E", "EV/EBITDA"],
        "secondary": ["P/AUM (Price-to-AUM)", "Dividend Yield"],
        "notes": (
            "AMCs are typically valued on P/E given their high-ROE, asset-light, high-payout profile, with "
            "P/AUM as a useful cross-check on how the market is pricing the underlying AUM base versus "
            "peers. Because revenue and profit are so closely tied to equity-market levels, valuations can "
            "look cheap at a market peak (earnings inflated) and expensive at a market trough (earnings "
            "depressed) — normalise for the market cycle before comparing multiples across time."
        ),
    },

    "llm_context": (
        "This is a MUTUAL FUND ASSET MANAGEMENT COMPANY / AMC (e.g. HDFC AMC, Nippon Life India AMC, UTI "
        "AMC) — an asset-light, high-margin, high-ROE business whose revenue is essentially a percentage "
        "fee (expense ratio) on Average Assets Under Management. There is no meaningful capex, inventory, "
        "or manufacturing here — do NOT apply generic industrial framing. The two dominant, sector-specific "
        "swing factors are: (1) SEBI's periodic total-expense-ratio (TER) regulation, which mechanically "
        "changes revenue per rupee of AUM independent of the AMC's own performance, and (2) equity-market "
        "levels, which affect AUM (and therefore revenue) both via mark-to-market and via net flows "
        "simultaneously — a market correction hits this business twice, not once. SIP flows are the key "
        "quality-of-growth metric to look for versus lump-sum flows."
    ),
}
