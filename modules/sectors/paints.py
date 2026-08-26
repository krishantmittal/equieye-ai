# modules/sectors/paints.py
"""
Paints — Sector Module
=======================
For Asian Paints, Berger Paints, Kansai Nerolac, Akzo Nobel India etc.

CRITICAL DISTINCTION FROM CHEMICALS: yfinance tags these "Specialty
Chemicals" because paint is manufactured via a chemical process, but the
actual business model is the opposite of a commodity-chemical maker's.
A specialty/commodity chemical producer is a price-taker on inputs and
often on outputs too, competes on cost/scale, and is valued through-cycle
on EV/EBITDA. A decorative-paints major, by contrast, sells a branded,
dealer-network-distributed consumer product with real pricing power —
economics much closer to an FMCG company (Asian Paints itself is
frequently benchmarked against HUL/Nestle India on quality of earnings)
than to Aarti Industries or SRF. Applying the chemicals module's
commodity-cycle framing here materially understates the business's
moat and mischaracterises its margin drivers (brand + dealer reach +
input-cost pass-through lag, not capacity utilisation or export pricing).
"""

SECTOR_CONFIG: dict = {
    "slug": "paints",
    "display_name": "Paints",

    "key_metrics": [
        {"id": "revenue_growth",      "label": "Revenue Growth (YoY)",        "unit": "%", "yf_key": "revenueGrowth", "higher_is_better": True},
        {"id": "gross_margin",        "label": "Gross Margin",                "unit": "%", "yf_key": "grossMargins", "higher_is_better": True},
        {"id": "ebitda_margin",       "label": "EBITDA Margin",               "unit": "%", "yf_key": "ebitdaMargins", "higher_is_better": True},
        {"id": "dealer_network_reach", "label": "Dealer/Retail Touchpoints",  "unit": "#", "yf_key": None, "higher_is_better": True},
        {"id": "roe",                 "label": "Return on Equity",            "unit": "%", "yf_key": "returnOnEquity", "higher_is_better": True},
        {"id": "de_ratio",            "label": "Debt/Equity",                 "unit": "x", "yf_key": "debtToEquity", "higher_is_better": False},
    ],

    "scoring_rules": [
        {"metric": "revenue_growth", "op": ">", "threshold": 12.0, "points": 20, "max": 20},
        {"metric": "revenue_growth", "op": ">", "threshold": 6.0,  "points": 12, "max": 20},
        {"metric": "ebitda_margin",  "op": ">", "threshold": 18.0, "points": 25, "max": 25},
        {"metric": "ebitda_margin",  "op": ">", "threshold": 12.0, "points": 15, "max": 25},
        {"metric": "roe",            "op": ">", "threshold": 25.0, "points": 20, "max": 20},
        {"metric": "roe",            "op": ">", "threshold": 15.0, "points": 12, "max": 20},
        {"metric": "de_ratio",       "op": "<", "threshold": 0.5,  "points": 15, "max": 15},
    ],
    "score_max": 100,

    "risk_factors": [
        "Crude-derivative and titanium dioxide input-cost volatility — a rise in these raw materials compresses margin until the company can pass it through via price hikes, which lag by a quarter or more",
        "Intensifying competition from well-funded new entrants (Grasim's Birla Opus, JSW Paints) attacking the dealer network and ad-spend moat that incumbents built over decades",
        "Real-estate and construction-activity cyclicality drives decorative-paint volumes; a housing slowdown directly hits demand",
        "Raw-material import dependence for certain resins/pigments exposes margins to currency movements",
        "Aggressive discounting or dealer-margin wars during a market-share fight can compress industry-wide profitability even for the largest player",
    ],

    "moat_factors": [
        {"factor": "Brand Trust", "description": "Decades of consumer advertising and colour-consultancy services build a trusted household brand that supports a premium price versus unbranded/regional paint"},
        {"factor": "Dealer & Tinting-Machine Network", "description": "Tens of thousands of exclusive/preferred dealer relationships and colour-tinting machines placed at dealer counters create switching costs for both dealers and painters that a new entrant must replicate one counter at a time"},
        {"factor": "Painter/Applicator Loyalty Programs", "description": "Direct engagement and loyalty programs with the painter community (who heavily influence the end-consumer's brand choice) is a distribution-level moat competitors struggle to copy quickly"},
        {"factor": "Scale Economics in Manufacturing & Distribution", "description": "Large-scale manufacturing and a pan-India logistics network let incumbents serve remote/rural markets more profitably than smaller regional players"},
    ],

    "bull_case": [
        "Rising per-capita income and housing formation supporting structural volume growth in decorative paints",
        "Industrial/automotive paints and adjacent categories (waterproofing, home décor) offering diversification beyond the core decorative segment",
        "Premiumisation mix-shift (emulsions over distemper) lifting realisation per litre over time",
        "Rural penetration still has runway versus urban market saturation",
    ],

    "bear_case": [
        "New, well-capitalised entrants undercutting dealer margins and ad-spend to buy market share, structurally compressing category profitability",
        "A sharp raw-material cost spike that the company cannot fully pass through without hurting volumes",
        "A prolonged real-estate/construction downturn suppressing decorative-paint demand",
        "Market-share erosion at the largest incumbent if new entrants successfully replicate the dealer/tinting-machine network faster than expected",
    ],

    "red_flags": [
        {"condition": "ebitda_margin < 10", "severity": "high",   "message": "EBITDA margin < 10% — unusually thin for a branded paints business; check for an input-cost spike or an active price war"},
        {"condition": "revenue_growth < 0", "severity": "high",   "message": "Negative revenue growth — check whether this is share loss to new entrants or a genuine demand slowdown"},
        {"condition": "de_ratio > 1.5",     "severity": "medium", "message": "D/E > 1.5x — elevated for a historically low-leverage, cash-generative paints business; check the source of the debt"},
    ],

    "valuation": {
        "primary":   ["P/E", "EV/EBITDA"],
        "secondary": ["P/B", "EV/Sales"],
        "bands": {
            "pe_ratio": {"attractive": (0, 40), "fair": (40, 65), "expensive": (65, 999)},
        },
        "notes": (
            "Paints majors have historically traded at premium, FMCG-like P/E multiples reflecting brand "
            "moat and high ROE, not commodity-chemical EV/EBITDA multiples. That premium is now being "
            "tested by new-entrant competition, so compare current multiples against the company's own "
            "history as well as peers rather than assuming the premium is permanent."
        ),
    },

    "llm_context": (
        "This is a PAINTS company (e.g. Asian Paints, Berger Paints, Kansai Nerolac) — NOT a commodity or "
        "specialty chemical producer, even though yfinance tags it 'Specialty Chemicals'. It sells a "
        "branded, dealer-distributed consumer product with real pricing power, brand loyalty, and a "
        "painter/dealer network moat — economics closer to FMCG than to a chemical price-taker. Do NOT "
        "apply commodity-cycle, through-cycle EV/EBITDA, or capacity-utilisation framing here. The current "
        "defining industry dynamic is new, well-funded entrants (Birla Opus, JSW Paints) attacking the "
        "dealer-network moat — factor this into competitive-intensity assessment even if historical "
        "margins look pristine."
    ),
}
