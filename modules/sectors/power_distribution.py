# modules/sectors/power_distribution.py
"""
Power Distribution — Sector Module
====================================
Split out of power_utilities.py. A distribution licensee (Torrent Power,
CESC) earns off a license-area monopoly on the "last mile" to the consumer
— its economics turn on AT&C (Aggregate Technical & Commercial) losses,
regulatory tariff true-ups, and subsidy receivables from the state
government, none of which are the right frame for a generator's fuel risk
or a transmission company's TBCB bidding dynamics.
"""

SECTOR_CONFIG: dict = {
    "slug": "power_distribution",
    "display_name": "Power Distribution",

    "key_metrics": [
        {"id": "atc_losses",          "label": "AT&C Losses",              "unit": "%", "yf_key": None,             "higher_is_better": False},
        {"id": "collection_efficiency","label": "Billing/Collection Efficiency", "unit": "%", "yf_key": None,       "higher_is_better": True},
        {"id": "regulated_asset_base_growth", "label": "Regulated Asset Base Growth", "unit": "%", "yf_key": None,  "higher_is_better": True},
        {"id": "subsidy_receivable_days", "label": "Subsidy Receivable Days", "unit": "days", "yf_key": None,       "higher_is_better": False},
        {"id": "debt_equity",         "label": "Debt/Equity",              "unit": "x", "yf_key": "debtToEquity",  "higher_is_better": False},
        {"id": "roe",                 "label": "Return on Equity",         "unit": "%", "yf_key": "returnOnEquity","higher_is_better": True},
    ],

    "scoring_rules": [
        {"metric": "atc_losses",              "op": "<", "threshold": 10.0, "points": 25, "max": 25},
        {"metric": "atc_losses",              "op": "<", "threshold": 18.0, "points": 12, "max": 25},
        {"metric": "collection_efficiency",   "op": ">", "threshold": 98.0, "points": 20, "max": 20},
        {"metric": "collection_efficiency",   "op": ">", "threshold": 92.0, "points": 10, "max": 20},
        {"metric": "debt_equity",             "op": "<", "threshold": 1.5,  "points": 20, "max": 20},
        {"metric": "roe",                     "op": ">", "threshold": 14.0, "points": 20, "max": 20},
        {"metric": "subsidy_receivable_days", "op": "<", "threshold": 90.0, "points": 15, "max": 15},
    ],
    "score_max": 100,

    "risk_factors": [
        "Regulatory tariff-setting delays — the state regulator's true-up of actual cost versus approved "
        "tariff can lag by years, creating working-capital and earnings-recognition risk",
        "State government subsidy payment delays (for subsidised consumer categories) straining receivables",
        "AT&C losses (theft, billing inefficiency, collection shortfall) directly eroding realised margin "
        "even when the approved tariff itself is adequate",
        "License/franchise renewal risk in franchise-area distribution models",
        "Geographic concentration — earnings tied to a single license area's economic health and consumer mix",
        "Open-access / competitive-supply policy changes that could erode the captive-consumer base over time",
    ],

    "moat_factors": [
        {"factor": "License-Area Monopoly",        "description": "Exclusive distribution rights in its licensed geography — a structural, not competitive, barrier to a new entrant"},
        {"factor": "Embedded Captive Demand",      "description": "Consumers in the license area have no alternative distributor for standard supply, giving a predictable, low-churn demand base"},
        {"factor": "AT&C Loss Efficiency vs. State Discoms", "description": "Private distribution licensees typically run materially lower AT&C losses than state-run discoms — a genuine operating-efficiency moat within the sector"},
        {"factor": "Regulated Asset Base Growth",  "description": "Capex into the network grows the regulated asset base on which a return is earned — a self-reinforcing, low-risk growth mechanism when tariff true-ups are timely"},
    ],

    "bull_case": [
        "AT&C loss reduction directly and durably improving realised margin, independent of demand growth",
        "License-area demand growth from urbanisation and rising per-capita consumption",
        "Regulated asset base growth from network capex translating into steady, contracted-return earnings "
        "growth",
        "EV charging infrastructure and smart-metering roll-out opening new regulated/adjacent revenue lines",
        "Track record of regulatory tariff true-ups being honoured supporting earnings predictability",
    ],

    "bear_case": [
        "Regulatory tariff-setting or true-up delays creating a working-capital and earnings-recognition gap "
        "between actual cost and approved recovery",
        "State government subsidy payment delays straining receivables and cash flow",
        "AT&C losses eroding realised margin even where the approved tariff is adequate",
        "Franchise/license renewal risk at contract expiry",
        "Open-access policy liberalisation gradually eroding the captive high-margin commercial/industrial "
        "consumer base to alternative suppliers",
    ],

    "red_flags": [
        {"condition": "atc_losses > 20",              "severity": "high",   "message": "AT&C losses > 20% — comparable to underperforming state discoms rather than an efficient private licensee"},
        {"condition": "subsidy_receivable_days > 180", "severity": "high",   "message": "Subsidy receivables > 180 days — significant state-government payment-delay strain"},
        {"condition": "collection_efficiency < 90",    "severity": "medium", "message": "Collection efficiency < 90% — billing/recovery inefficiency dragging on realised revenue"},
        {"condition": "debt_equity > 2.0",              "severity": "medium", "message": "D/E > 2.0x — elevated leverage for a regulated-return distribution business"},
    ],

    "valuation": {
        "primary":   ["P/E", "Dividend Yield"],
        "secondary": ["P/B Ratio"],
        "notes": (
            "Distribution licensees with low AT&C losses and a track record of timely regulatory true-ups "
            "warrant a premium versus peers still working through loss reduction — the multiple should "
            "reflect execution/regulatory-relationship quality, not just headline earnings growth."
        ),
    },

    "llm_context": (
        "This is a POWER DISTRIBUTION company (e.g. Torrent Power, CESC) — the last-mile licensee that bills "
        "and collects from end consumers in its licensed area — distinct from a GENERATION company (NTPC, "
        "Adani Power) that has fuel/PLF risk, and a TRANSMISSION company (Power Grid) that has TBCB-bidding "
        "and availability-based-tariff dynamics. Do not apply fuel-cost, PLF, or coal-linkage framing here — "
        "a distribution company's core economics are AT&C (Aggregate Technical & Commercial) losses, billing "
        "and collection efficiency, and how promptly the state regulator true-ups approved tariffs against "
        "actual cost. "
        "Focus on: license-area monopoly and embedded captive demand, AT&C loss trajectory relative to state "
        "discoms (a genuine efficiency moat for private players), regulated asset base growth from network "
        "capex, and subsidy-receivable risk from the state government (distinct from a generator's discom-"
        "receivable risk, which is about being paid for power supplied, not about a subsidy pass-through). "
        "The dominant BEAR theme is regulatory tariff-setting/true-up delay and subsidy payment delay — not "
        "fuel cost, not stranded generation assets, not TBCB margin compression."
    ),
}
