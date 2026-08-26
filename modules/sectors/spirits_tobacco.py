# modules/sectors/spirits_tobacco.py
"""
Spirits & Tobacco ("Sin Goods") — Sector Module
================================================
For United Spirits, United Breweries, Godfrey Phillips, ITC's cigarette
business framing, VST Industries and similar alcohol/tobacco companies.

CRITICAL DISTINCTION FROM FMCG: yfinance tags virtually every company in
this space with the bare sector label "Consumer Defensive" — the same
GICS supersector as staples like HUL, Nestle, and Dabur. The old fmcg
detector rule matched on that bare "consumer defensive" keyword alone,
which meant spirits and tobacco companies received the same branded-FMCG
moat/valuation framing as a packaged-foods company. That's the wrong lens:
these businesses carry a materially different risk profile — punitive and
unpredictable excise/GST duty structures set state-by-state (for
alcohol) or nationally with a history of sharp step-changes (for
tobacco), advertising bans, litigation exposure (tobacco health
litigation, alcohol prohibition risk in specific states), and ESG/
institutional-ownership constraints that a staples company doesn't face.
Volume growth is also structurally capped/regulated in ways a normal
FMCG category isn't.
"""

SECTOR_CONFIG: dict = {
    "slug": "spirits_tobacco",
    "display_name": "Spirits & Tobacco",

    "key_metrics": [
        {"id": "revenue_growth",   "label": "Revenue Growth (YoY)",   "unit": "%", "yf_key": "revenueGrowth", "higher_is_better": True},
        {"id": "volume_growth",    "label": "Volume Growth (YoY)",    "unit": "%", "yf_key": None, "higher_is_better": True},
        {"id": "ebitda_margin",   "label": "EBITDA Margin",           "unit": "%", "yf_key": "ebitdaMargins", "higher_is_better": True},
        {"id": "premiumisation_mix", "label": "Premium/Prestige Mix Share", "unit": "%", "yf_key": None, "higher_is_better": True},
        {"id": "roe",             "label": "Return on Equity",        "unit": "%", "yf_key": "returnOnEquity", "higher_is_better": True},
        {"id": "de_ratio",        "label": "Debt/Equity",             "unit": "x", "yf_key": "debtToEquity", "higher_is_better": False},
    ],

    "scoring_rules": [
        {"metric": "revenue_growth", "op": ">", "threshold": 10.0, "points": 15, "max": 15},
        {"metric": "revenue_growth", "op": ">", "threshold": 4.0,  "points": 8,  "max": 15},
        {"metric": "ebitda_margin",  "op": ">", "threshold": 25.0, "points": 25, "max": 25},
        {"metric": "ebitda_margin",  "op": ">", "threshold": 15.0, "points": 15, "max": 25},
        {"metric": "roe",            "op": ">", "threshold": 25.0, "points": 25, "max": 25},
        {"metric": "roe",            "op": ">", "threshold": 15.0, "points": 15, "max": 25},
        {"metric": "de_ratio",       "op": "<", "threshold": 0.5,  "points": 20, "max": 20},
    ],
    "score_max": 100,

    "risk_factors": [
        "Excise duty and taxation is set state-by-state for alcohol (India has no unified national alcohol tax policy) and can change unpredictably, directly hitting realisation and margin",
        "Tobacco carries a well-documented, escalating history of sharp national excise/GST-compensation-cess step-changes, plus advertising and packaging (health-warning) restrictions",
        "Litigation and regulatory exposure is structurally higher than a normal staples company — health litigation risk for tobacco, prohibition risk in specific Indian states for alcohol",
        "ESG-driven institutional-ownership constraints (many funds exclude sin-goods stocks entirely) can structurally cap the investor base and depress valuation multiples versus fundamentals",
        "Distribution in India for alcohol often runs through state-government-controlled retail/wholesale channels, adding a layer of channel risk a staples company doesn't have",
        "Input-cost volatility (extra neutral alcohol/ENA, tobacco leaf, packaging) affects margin alongside the duty structure",
    ],

    "moat_factors": [
        {"factor": "Brand Portfolio & Legal Heritage", "description": "Decades-old brands with strong consumer recall (in spirits, often tied to legally protected geographic/heritage naming) are difficult for a new entrant to replicate, especially under advertising restrictions that limit new-brand-building spend"},
        {"factor": "Distribution & Licensing Relationships", "description": "Navigating state-by-state alcohol licensing and distribution (or national tobacco retail distribution) requires relationships and regulatory know-how built over years, acting as a real barrier to new entrants"},
        {"factor": "Premiumisation Pricing Power", "description": "A shift in consumer mix toward premium/prestige labels lets incumbents raise realisation per unit even when volume growth is capped by regulation or taxation"},
        {"factor": "Regulatory-Barrier-Driven Industry Structure", "description": "Advertising bans and licensing complexity, while a risk factor, also protect incumbents by making it hard for new brands to build awareness — a double-edged moat unique to sin-goods categories"},
    ],

    "bull_case": [
        "Premiumisation (consumers trading up within the category) driving margin expansion even on flat-to-modest volume growth",
        "Rising disposable income in India expanding the addressable premium spirits/tobacco consumer base",
        "Consolidation of brand portfolios and cost discipline improving structural profitability",
        "High entry barriers (licensing, advertising restrictions, brand heritage) protecting incumbent market share from new competition",
    ],

    "bear_case": [
        "A sharp, unexpected excise duty or GST compensation-cess increase compressing margin or forcing price hikes that hurt volumes",
        "Escalating anti-tobacco/anti-alcohol regulation (advertising, packaging, retail-display restrictions, prohibition risk in specific states)",
        "ESG-driven exclusion from institutional portfolios structurally capping the valuation multiple regardless of fundamentals",
        "Adverse litigation outcomes (particularly tobacco health litigation) creating open-ended liability risk",
    ],

    "red_flags": [
        {"condition": "ebitda_margin < 12", "severity": "high",   "message": "EBITDA margin < 12% — check for an unabsorbed excise-duty hike or adverse mix shift"},
        {"condition": "revenue_growth < 0", "severity": "high",   "message": "Negative revenue growth — check whether this reflects a duty-driven price/volume trade-off or genuine demand weakness"},
        {"condition": "de_ratio > 1",       "severity": "medium", "message": "D/E > 1x — elevated for a historically low-leverage, high-ROE spirits/tobacco business"},
    ],

    "valuation": {
        "primary":   ["P/E", "EV/EBITDA"],
        "secondary": ["P/B", "Dividend Yield"],
        "notes": (
            "Spirits and tobacco majors often trade at a persistent valuation discount to comparable-quality "
            "staples FMCG names despite similar or better ROE/margin profiles — this is largely structural "
            "(ESG exclusion, regulatory/tax overhang) rather than a mispricing to be arbitraged away, so "
            "don't assume the discount will close."
        ),
    },

    "llm_context": (
        "This is a SPIRITS or TOBACCO ('sin goods') company (e.g. United Spirits, United Breweries, Godfrey "
        "Phillips, VST Industries) — do NOT treat it as a standard FMCG staples company just because "
        "yfinance's bare sector tag is 'Consumer Defensive'. The risk profile is materially different from "
        "HUL/Nestle-style staples: unpredictable state-by-state alcohol excise duty or national tobacco "
        "excise/cess step-changes, advertising and packaging restrictions, litigation exposure, and "
        "ESG-driven institutional-ownership constraints that structurally cap valuation multiples "
        "independent of fundamentals. Premiumisation (mix-shift to higher price points) is the primary "
        "margin lever here, not volume growth, which is often regulation-capped. Don't be surprised by a "
        "persistent valuation discount to staples peers — that's structural, not necessarily a mispricing."
    ),
}
