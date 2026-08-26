# modules/sectors/defense_aerospace.py
"""
Defense & Aerospace — Sector Module
======================================
India's listed defense/aerospace manufacturers (Hindustan Aeronautics,
Bharat Electronics, Bharat Dynamics, Mazagon Dock Shipbuilders, Garden
Reach Shipbuilders, Cochin Shipyard, BEML, Astra Microwave, Data
Patterns, and similar) had NO dedicated sector module before this —
they fell into the generic/unclassified bucket, which produces a flat
market/competitive-risk framework instead of the sector's actual, quite
distinctive economics: revenue overwhelmingly concentrated in a single
customer (the Ministry of Defence / Indian Armed Forces), demand driven
by government budget allocation and indigenization policy rather than
open-market competition, and a real regulatory/licensing moat (defense
manufacturing is largely closed to foreign competition and requires
security clearances) that's structurally different from a normal
capital-goods or EPC business.
"""

SECTOR_CONFIG: dict = {
    "slug": "defense_aerospace",
    "display_name": "Defense & Aerospace",

    "key_metrics": [
        {"id": "order_book",            "label": "Order Book",                    "unit": "₹Cr", "yf_key": None, "higher_is_better": True},
        {"id": "book_to_bill",          "label": "Book-to-Bill Ratio",             "unit": "x",   "yf_key": None, "higher_is_better": True},
        {"id": "export_revenue_pct",    "label": "Export Revenue Mix",             "unit": "%",   "yf_key": None, "higher_is_better": True},
        {"id": "indigenous_content_pct","label": "Indigenous Content Mix",         "unit": "%",   "yf_key": None, "higher_is_better": True},
        {"id": "ebitda_margin",         "label": "EBITDA Margin",                  "unit": "%",   "yf_key": "ebitdaMargins", "higher_is_better": True},
        {"id": "roce",                  "label": "Return on Capital Employed",     "unit": "%",   "yf_key": "returnOnEquity", "higher_is_better": True},
    ],

    "risk_factors": [
        "Revenue overwhelmingly concentrated in a single customer (Ministry of Defence / Indian Armed Forces) — a policy shift or budget cut has outsized impact versus a diversified industrial customer base",
        "Government defense budget allocation and fiscal priorities directly determine order flow, independent of the company's own execution",
        "Long, lumpy order/sanction cycles — large contracts are booked infrequently, causing sharp quarter-to-quarter revenue swings unrelated to underlying demand",
        "Execution/delivery delay risk on complex, often first-of-a-kind indigenous defense programs — well-documented history of program timeline slippage in Indian defense manufacturing",
        "Working capital intensity from government payment and audit cycles, which can be slower than a private-sector customer",
        "Export order flow depends on government clearances and geopolitical relationships, not just competitiveness",
    ],

    "moat_factors": [
        {"factor": "Licensing & Security Clearance Barrier", "description": "Defense manufacturing requires government licensing and security clearances that are largely closed to new entrants and foreign competition — a structural barrier unique to strategic sectors"},
        {"factor": "Qualified Vendor Status",   "description": "Becoming an approved, trusted, long-standing vendor to the Ministry of Defence/Armed Forces itself takes years — new entrants face a multi-year qualification cycle"},
        {"factor": "Technology & IP",           "description": "Decades of R&D, design authority, and (often exclusive) technology-transfer agreements create real barriers competitors can't quickly replicate"},
        {"factor": "Order Book Visibility",     "description": "Large, multi-year sanctioned government orders provide revenue visibility well beyond a typical industrial order book"},
        {"factor": "Policy Tailwind (Indigenization)", "description": "'Make in India'/Atmanirbhar Bharat defense-indigenization policy actively favors qualified domestic incumbents over imports"},
    ],

    "bull_case": [
        "Rising defense budget allocation and the indigenization push (Atmanirbhar Bharat) directing new orders to domestic players",
        "Export order wins diversifying revenue beyond the historically single-customer (MoD) domestic base",
        "Margin expansion as indigenous content share rises relative to licensed/imported-component production",
        "Global geopolitical tensions structurally increasing defense spending across export markets",
        "Platform-life annuity — decades of spares, maintenance, overhaul, and upgrade revenue from a large installed base",
    ],

    "bear_case": [
        "Order execution delays on complex indigenous programs pushing out revenue recognition",
        "Government budget allocation risk — defense capex is subject to fiscal and political priorities and can be deferred",
        "Customer concentration risk — a policy shift or budget cut at a single customer (MoD) has an outsized impact versus a diversified industrial customer base",
        "Execution/margin risk on first-of-a-kind indigenous platforms without a prior production track record",
        "Working capital strain from government payment and audit cycles",
    ],

    "red_flags": [
        {"condition": "ebitda_margin < 10", "severity": "high",   "message": "EBITDA margin < 10% — weak for a sector where sanctioned government programs typically carry high margins"},
        {"condition": "roce < 12",           "severity": "medium", "message": "ROCE < 12% — below what a qualified-vendor, policy-tailwind business with strong order visibility should clear"},
        {"condition": "de_ratio > 1.0",      "severity": "medium", "message": "D/E > 1.0x — unusual for this sector, which is typically low-leverage (PSU-dominated with government-backed order books and advance payments)"},
    ],

    "valuation": {
        "primary":   ["P/E", "EV/EBITDA"],
        "secondary": ["Order Book / Market Cap", "P/E relative to order book growth"],
        "notes": (
            "Defense/aerospace names often trade at a premium reflecting the indigenization policy tailwind and "
            "scarcity value — there are relatively few pure-play listed options in this space. Valuation should "
            "be assessed against order book growth, export diversification progress, and execution track "
            "record, not just trailing P/E — a company with a large sanctioned order book but a history of "
            "execution delays deserves a valuation discount versus one with proven on-time delivery."
        ),
        "bands": {
            "pe_ratio": {"attractive": (0, 25), "fair": (25, 40), "expensive": (40, 999)},
        },
    },

    "llm_context": (
        "This is a DEFENSE & AEROSPACE company (e.g. Hindustan Aeronautics, Bharat Electronics, Bharat "
        "Dynamics, Mazagon Dock, Garden Reach, Cochin Shipyard, BEML, Astra Microwave, Data Patterns) — "
        "distinct from a generic capital-goods/EPC business. Most important structural fact: revenue is "
        "overwhelmingly concentrated in one customer (MoD/Indian Armed Forces) — frame 'customer "
        "concentration' in those specific terms, not generic industrial language. Demand is driven by "
        "government defense budget allocation and the indigenization/Atmanirbhar Bharat push, not "
        "open-market or consumer demand. The moat is real but comes from licensing/security-clearance "
        "barriers, qualified-vendor status built over years, and technology/design-authority IP — not "
        "brand or pricing power. Order book size means little without an on-time execution track record — "
        "flag companies with a history of program delays (well-documented in Indian defense manufacturing) "
        "rather than taking a large order book at face value. "
        "LEVERAGE: this sector (especially PSU names) is typically low-debt, often near-zero, given "
        "government-backed order books and advance payments — don't default to a generic 'Leverage Risk' "
        "bear headline unless D/E is genuinely elevated (>1.0x) for this sector."
    ),
}
