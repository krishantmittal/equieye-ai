# modules/sectors/railway_travel_services.py
"""
Railway Ticketing, Catering & Tourism Services — Sector Module
================================================================
For Indian Railway Catering and Tourism Corporation (IRCTC) and any
similarly-structured government-granted exclusive railway services
platform.

Was previously falling through to "generic" — and worse, a bare
"hospital" keyword in the hospitals sector rule was matching IRCTC's own
description (which legitimately mentions "hospitality" services as part
of its catering/tourism business), misrouting it into a hospital-chain
framework entirely. See detector.py's hospitals-rule fix for that half
of the bug.

IRCTC's economics don't resemble any existing sector: it is not an
e-commerce marketplace, not a QSR/restaurant chain, not a hotel/
hospitality operator, and not a generic industrial. It holds an
exclusive, government-granted monopoly (from Indian Railways, its own
parent) across three linked verticals — online ticketing, on-board/
station catering, and packaged tourism — with a captive user base of
hundreds of millions of Indian Railways passengers who have no
alternative platform for railway e-ticketing. That regulatory exclusivity
plus captive demand (not network effects or technology moat in the
market-infrastructure sense) is the actual moat, and needs its own
framing rather than reusing an exchange/depository or hospital-chain
module.
"""

SECTOR_CONFIG: dict = {
    "slug": "railway_travel_services",
    "display_name": "Railway Ticketing, Catering & Tourism Services",

    "key_metrics": [
        {"id": "revenue_growth",   "label": "Revenue Growth (YoY)",             "unit": "%", "yf_key": "revenueGrowth", "higher_is_better": True},
        {"id": "operating_margin", "label": "Operating Margin",                  "unit": "%", "yf_key": "operatingMargins", "higher_is_better": True},
        {"id": "roe",              "label": "Return on Equity",                  "unit": "%", "yf_key": "returnOnEquity", "higher_is_better": True},
        {"id": "ticket_volume_growth", "label": "Tickets Booked / User Growth",  "unit": "%", "yf_key": None, "higher_is_better": True},
        {"id": "tourism_revenue_mix",  "label": "Tourism & Packages Revenue Mix", "unit": "%", "yf_key": None, "higher_is_better": True},
    ],

    "scoring_rules": [
        {"metric": "revenue_growth",   "op": ">", "threshold": 15.0, "points": 20, "max": 20},
        {"metric": "revenue_growth",   "op": ">", "threshold": 8.0,  "points": 12, "max": 20},
        {"metric": "operating_margin", "op": ">", "threshold": 30.0, "points": 30, "max": 30},
        {"metric": "operating_margin", "op": ">", "threshold": 20.0, "points": 18, "max": 30},
        {"metric": "roe",              "op": ">", "threshold": 25.0, "points": 25, "max": 25},
        {"metric": "roe",              "op": ">", "threshold": 15.0, "points": 15, "max": 25},
        {"metric": "de_ratio",         "op": "<", "threshold": 0.2,  "points": 15, "max": 15},
    ],
    "score_max": 100,

    "risk_factors": [
        "Single ultimate parent/regulator (Indian Railways / Ministry of Railways) — any policy change to the exclusivity arrangement, convenience-fee structure, or catering licence terms directly hits revenue with no commercial recourse",
        "Convenience fee on ticketing (a major profit contributor) has previously been revised or waived by government directive, showing this revenue line is policy-dependent, not purely commercial",
        "Catering margins are exposed to input food-cost inflation and standardised pricing set in coordination with Railways, limiting pricing power versus a normal restaurant business",
        "Tourism/packages segment carries normal discretionary-travel demand cyclicality (unlike the captive ticketing/catering base) and is more exposed to macro slowdowns or travel disruptions",
        "As a majority government-owned enterprise, subject to broader PSU governance, disinvestment, and policy-continuity risk",
    ],

    "moat_factors": [
        {"factor": "Exclusive Government-Granted Ticketing Monopoly", "description": "IRCTC is the sole entity authorised by Indian Railways to sell railway e-tickets online — a structural, non-replicable monopoly granted by its own parent, not something a private competitor can bid for or build around"},
        {"factor": "Captive User Base", "description": "Every Indian Railways passenger booking online has no alternative platform, creating an enormous, effectively guaranteed transaction base tied to railway travel demand rather than to IRCTC's own customer acquisition"},
        {"factor": "Integrated Catering + Tourism Ecosystem", "description": "On-board catering, station catering (base kitchens), packaged drinking water (Rail Neer), and tourism packages (e.g. Bharat Gaurav trains) are all cross-sold off the same captive railway-passenger relationship, widening revenue per user beyond the ticketing fee alone"},
        {"factor": "Brand Trust & Switching Costs", "description": "Decades as the only official channel for railway ticketing has built default consumer trust and habit; there is no meaningful switching incentive since no substitute platform exists for booking Indian Railways tickets"},
    ],

    "bull_case": [
        "Growth in online railway ticket volumes and registered user base as more of India's rail travel shifts to digital booking",
        "Cross-sell expansion of tourism packages and premium train products (e.g. Bharat Gaurav, Vande Bharat-linked packages) monetising the same captive user base at higher ticket sizes",
        "Operating leverage on a largely fixed technology/ticketing platform as transaction volumes grow",
        "Potential new revenue levers (e.g. advertising on the platform, data-led personalisation, bundled travel insurance) layered onto the existing captive base",
    ],

    "bear_case": [
        "Government directive to reduce, cap, or waive the online ticketing convenience fee — has happened before and remains a standing policy risk given IRCTC's PSU/monopoly status",
        "Renegotiation or dilution of catering/tourism licence terms by Indian Railways, given IRCTC operates entirely at its parent's discretion",
        "Food-cost inflation compressing catering margins without full pass-through pricing flexibility",
        "Discretionary tourism/package demand pulling back in a travel-spending slowdown, unlike the more resilient ticketing/catering base",
    ],

    "red_flags": [
        {"condition": "operating_margin < 15", "severity": "high",   "message": "Operating margin < 15% — low for a business built on a fee-based, largely fixed-cost ticketing platform; check for a one-off cost or a convenience-fee policy change"},
        {"condition": "revenue_growth < 0",     "severity": "high",   "message": "Negative revenue growth — check whether this reflects a fee waiver/cap directive, a catering contract change, or a genuine drop in rail travel volumes"},
        {"condition": "de_ratio > 0.3",         "severity": "medium", "message": "D/E > 0.3x — unusually leveraged for this typically capital-light, cash-generative government-monopoly platform"},
    ],

    "valuation": {
        "primary":   ["P/E", "EV/EBITDA"],
        "secondary": ["P/B", "Dividend Yield"],
        "bands": {
            "pe_ratio": {"attractive": (0, 22), "fair": (22, 32)},
        },
        "notes": (
            "IRCTC's monopoly, high-ROE, asset-light profile typically commands a premium multiple versus "
            "a generic industrial or travel-services company — but because a meaningful share of profit "
            "comes from a government-set convenience fee rather than purely commercial pricing, treat "
            "policy/fee-structure risk as a real overhang on the multiple, not just a line item."
        ),
    },

    "llm_context": (
        "This is a GOVERNMENT-GRANTED EXCLUSIVE RAILWAY SERVICES MONOPOLY (IRCTC or a similarly-structured "
        "entity) — NOT a market infrastructure/exchange company, NOT a hospital or healthcare-delivery "
        "company, NOT a QSR/restaurant chain, and NOT a generic hotel/hospitality operator, even though its "
        "own business description may use the word 'hospitality' in the context of catering/tourism "
        "services. It holds the sole right, granted by its own parent Indian Railways, to sell railway "
        "e-tickets online, and layers on-board/station catering, packaged drinking water, and tourism "
        "packages on top of that same captive passenger base. The moat is regulatory exclusivity plus a "
        "captive user base — NOT network effects, NOT a technology platform advantage, and NOT brand-driven "
        "hotel/restaurant competition. The single biggest sector-specific risk is that a meaningful share of "
        "profit comes from a convenience fee and licence terms set by its own government parent, which can "
        "be revised, capped, or waived by policy directive rather than by competitive market forces."
    ),
}
