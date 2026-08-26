# modules/sectors/electrical_equipment.py
"""
Electrical Equipment (Branded / FMEG) — Sector Module
========================================================
Split out from capital_goods.py (and, for Havells specifically, out of
consumer_durables.py — see detector.py): branded electrical-equipment
companies (Havells, Polycab, KEI Industries, and similar) sell wires,
cables, switchgear, and fast-moving electrical goods (FMEG) through a
dealer/distribution network to builders, electricians, and households.
This is a brand-and-distribution business, not a project-execution
business (EPC/engineering) or a technology/automation-IP business
(industrial automation) — it competes on brand recall, dealer reach, and
raw-material (primarily copper, also aluminium and PVC) cost pass-
through, and is directly geared to residential/commercial construction
and housing demand rather than industrial capex or government order
books.
"""

SECTOR_CONFIG: dict = {
    "slug": "electrical_equipment",
    "display_name": "Electrical Equipment",

    "key_metrics": [
        {"id": "revenue_growth",  "label": "Revenue Growth (YoY)",     "unit": "%",  "yf_key": "revenueGrowth",   "higher_is_better": True},
        {"id": "ebitda_margin",   "label": "EBITDA Margin",            "unit": "%",  "yf_key": "ebitdaMargins",   "higher_is_better": True},
        {"id": "wires_cables_mix","label": "Wires & Cables Revenue Mix","unit": "%", "yf_key": None,              "higher_is_better": False},
        {"id": "dealer_reach",    "label": "Dealer/Distributor Network Size", "unit": "count", "yf_key": None,    "higher_is_better": True},
        {"id": "roce",            "label": "Return on Capital Employed","unit": "%", "yf_key": "returnOnEquity",  "higher_is_better": True},
        {"id": "de_ratio",        "label": "Debt / Equity",            "unit": "x",  "yf_key": "debtToEquity",    "higher_is_better": False},
    ],

    "risk_factors": [
        "Copper (and aluminium/PVC) price volatility — wires & cables margins are exposed to raw material swings that can't always be fully passed through",
        "Housing/real-estate demand cyclicality — a large share of demand is tied to residential and commercial construction activity",
        "Intense brand competition in the FMEG category (fans, appliances, lighting) compressing pricing power",
        "Channel/dealer inventory destocking cycles can distort quarterly reported growth",
        "Unorganized/local player price competition in wires & cables, a relatively lower-differentiation product category",
        "Working capital tied up in dealer credit and channel financing",
    ],

    "moat_factors": [
        {"factor": "Brand Recall",             "description": "Decades of consumer brand-building create pricing power and trust that new entrants can't buy quickly"},
        {"factor": "Distribution Depth",       "description": "A deep dealer/electrician network built over years is difficult and slow for competitors to replicate"},
        {"factor": "Product Breadth (FMEG)",   "description": "Cross-selling across wires, switchgear, fans, lighting, and appliances raises share-of-wallet with the same dealer base"},
        {"factor": "Manufacturing Scale",      "description": "Scale manufacturing lowers unit costs versus smaller regional/unorganized players"},
        {"factor": "Copper Hedging Discipline","description": "Sophisticated raw-material procurement and hedging protects margins better than smaller unorganized competitors can manage"},
    ],

    "bull_case": [
        "Housing and real-estate upcycle driving wires, cables, and FMEG demand",
        "Premiumization and brand-shift from unorganized to organized/branded players expanding market share",
        "New category launches (e.g. switchgear, water heaters, air coolers) broadening the addressable market per dealer",
        "Government housing and infrastructure schemes (affordable housing, rural electrification) expanding the addressable base",
        "Export opportunity in wires & cables as global supply chains diversify away from China",
    ],

    "bear_case": [
        "Sharp copper price spikes compressing wires & cables margins faster than pricing can catch up",
        "Housing/construction slowdown directly hitting core demand",
        "Aggressive competitive discounting compressing FMEG category margins",
        "Channel destocking creating a sharp, temporary revenue growth air-pocket",
        "Rising input costs (copper, aluminium, PVC resin) squeezing margins in a competitive pricing environment",
    ],

    "red_flags": [
        {"condition": "ebitda_margin < 8",   "severity": "high",   "message": "EBITDA margin < 8% — weak for a branded FMEG business, suggests pricing pressure or an unfavorable low-margin wires & cables-heavy mix"},
        {"condition": "revenue_growth < 3",   "severity": "medium", "message": "Revenue growth < 3% — below what a branded distribution business in a growing housing market should deliver"},
        {"condition": "de_ratio > 1.0",       "severity": "medium", "message": "D/E > 1.0x — elevated for what is typically an asset-light, brand-led distribution business"},
    ],

    "valuation": {
        "primary":   ["P/E", "EV/EBITDA"],
        "secondary": ["P/E relative to FMEG revenue mix and margin trajectory"],
        "notes": (
            "Branded electrical-equipment companies typically trade at a premium to pure commodity wires & "
            "cables players because of their brand and FMEG (fans, appliances, lighting) mix — a rising FMEG "
            "revenue share generally supports a higher multiple than a wires & cables-heavy mix, since FMEG "
            "carries higher and more stable margins."
        ),
        "bands": {
            "pe_ratio": {"attractive": (0, 35), "fair": (35, 55), "expensive": (55, 999)},
        },
    },

    "llm_context": (
        "This is a BRANDED ELECTRICAL EQUIPMENT / FMEG (Fast Moving Electrical Goods) company (e.g. Havells "
        "India, Polycab India, KEI Industries) — distinct from an EPC/engineering contractor (L&T, Thermax), "
        "which executes project contracts, and distinct from an industrial automation company (ABB, Siemens), "
        "which sells technology/software to industrial clients. This is a brand-and-distribution business "
        "selling wires, cables, switchgear, and consumer electrical goods (fans, lighting, appliances) through "
        "a dealer/electrician network, geared to residential/commercial construction and housing demand rather "
        "than industrial capex or government order books. Key demand drivers: brand strength, dealer/"
        "distribution reach, housing/real-estate activity, and copper (raw material) price trends. Key risks: "
        "copper price volatility squeezing wires & cables margins, housing-cycle sensitivity, and competitive "
        "intensity in the FMEG category. Do NOT apply order-book/execution-track-record framing (that fits "
        "EPC contractors) — assess brand strength, distribution depth, and raw-material cost pass-through "
        "instead."
    ),
}
