# modules/sectors/industrial_automation.py
"""
Industrial Automation — Sector Module
======================================
Split out from capital_goods.py: automation/electrification majors (ABB
India, Siemens India, Honeywell Automation India, and similar) sell
technology-led automation, software, and electrification products into
capex budgets — a fundamentally different economic model from an EPC
contractor (Thermax, L&T, KEC) that wins and executes large fixed-price
projects, or a branded electrical-goods distributor (Havells, Polycab)
selling through a dealer network. Automation majors compete on product/
software IP and typically carry structurally higher margins and cleaner
balance sheets than project-execution players, since they're not
warehousing working capital against multi-year contracts. Treating them
as generic "Capital Goods" produced identical order-book/execution
framing for a software-and-product business as for a construction
contractor, which misses what actually drives the stock.
"""

SECTOR_CONFIG: dict = {
    "slug": "industrial_automation",
    "display_name": "Industrial Automation",

    "key_metrics": [
        {"id": "revenue_growth",    "label": "Revenue Growth (YoY)",       "unit": "%",  "yf_key": "revenueGrowth",  "higher_is_better": True},
        {"id": "ebitda_margin",     "label": "EBITDA Margin",              "unit": "%",  "yf_key": "ebitdaMargins",  "higher_is_better": True},
        {"id": "order_inflow",      "label": "Order Inflow Growth",        "unit": "%",  "yf_key": None,             "higher_is_better": True},
        {"id": "software_mix",      "label": "Software/Digital Revenue Mix","unit": "%", "yf_key": None,             "higher_is_better": True},
        {"id": "roce",              "label": "Return on Capital Employed", "unit": "%",  "yf_key": "returnOnEquity", "higher_is_better": True},
        {"id": "fcf_conversion",    "label": "FCF Conversion",             "unit": "%",  "yf_key": None,             "higher_is_better": True},
    ],

    "risk_factors": [
        "Manufacturing/industrial capex slowdown directly reduces automation order inflows",
        "Import dependence on parent/global technology — currency and transfer-pricing exposure for MNC subsidiaries",
        "Customer concentration in a handful of large industrial/process clients for big-ticket orders",
        "Competitive intensity from both global majors (Rockwell, Schneider, Emerson) and rising domestic/Chinese automation players",
        "Long sales cycles for large automation/electrification contracts create lumpy quarterly order booking",
        "Component/semiconductor supply-chain disruptions can delay delivery on electronics-heavy orders",
    ],

    "moat_factors": [
        {"factor": "Automation & Software IP",  "description": "Proprietary control systems, PLC/SCADA software, and digital-twin platforms create real switching costs once embedded in a client's plant"},
        {"factor": "Installed Base Annuity",    "description": "A large installed base of automation systems generates recurring service, upgrade, and spares revenue over decades"},
        {"factor": "Global Parent Technology Access","description": "MNC subsidiaries get first access to parent-company R&D and product roadmaps that domestic-only competitors can't replicate"},
        {"factor": "Electrification Breadth",   "description": "A full stack from low-voltage products to grid-scale electrification lets these players bundle deals that single-product competitors can't match"},
        {"factor": "Brand & Certification Trust","description": "Process industries (oil & gas, pharma, chemicals) require certified, proven-reliability automation — a high bar for new entrants"},
    ],

    "bull_case": [
        "Manufacturing capex cycle and 'Make in India' push driving new automation order inflows",
        "Electrification of industrial processes (replacing pneumatic/mechanical systems) is a structural multi-year demand driver",
        "Rising software/digital mix (from digital twins, predictive maintenance, IIoT) improving margin quality over time",
        "China+1 manufacturing relocation bringing new greenfield capacity that needs automation from day one",
        "Energy transition and grid-modernization spend expanding the electrification product opportunity",
    ],

    "bear_case": [
        "Industrial capex slowdown or a delayed investment cycle compressing order inflows",
        "Global parent-company transfer pricing or royalty structures pressuring reported margins",
        "Currency exposure on imported components against an INR-denominated order book",
        "Rising competitive intensity from lower-cost domestic and Chinese automation entrants",
        "Order lumpiness — a large deal slipping to the next quarter can meaningfully swing reported growth",
    ],

    "red_flags": [
        {"condition": "revenue_growth < 3",   "severity": "high",   "message": "Revenue growth < 3% — automation order inflows have stalled"},
        {"condition": "ebitda_margin < 10",    "severity": "high",   "message": "EBITDA margin < 10% — thin for a technology/product-mix business, suggests pricing pressure or unfavorable mix"},
        {"condition": "roce < 15",             "severity": "medium", "message": "ROCE < 15% — below what an asset-light automation/software business should clear"},
    ],

    "valuation": {
        "primary":   ["P/E", "EV/EBITDA"],
        "secondary": ["P/E relative to order inflow growth"],
        "notes": (
            "Automation/electrification majors typically command a valuation premium over pure EPC/execution "
            "players because of their higher margins, cleaner balance sheets, and recurring service/software "
            "revenue. P/E should be assessed against order inflow growth and software/digital mix trends, not "
            "just trailing earnings — a rising digital mix usually justifies a higher multiple over time."
        ),
        "bands": {
            "pe_ratio": {"attractive": (0, 30), "fair": (30, 50), "expensive": (50, 999)},
        },
    },

    "llm_context": (
        "This is an INDUSTRIAL AUTOMATION / ELECTRIFICATION company (e.g. ABB India, Siemens India, Honeywell "
        "Automation India) — distinct from an EPC/engineering contractor (L&T, Thermax, KEC), which wins and "
        "executes large fixed-price projects, and distinct from a branded electrical-goods distributor "
        "(Havells, Polycab), which sells through a dealer network. This is a technology/product/software "
        "business selling automation systems, control software, and electrification products into industrial "
        "capex budgets. Key demand drivers: manufacturing capex cycle, electrification of industrial processes, "
        "rising software/digital revenue mix, China+1 manufacturing relocation. Key risks: industrial capex "
        "slowdown, import/currency exposure for MNC subsidiaries, order lumpiness, rising domestic/Chinese "
        "competition. Do NOT apply the order-book/execution-track-record framing that fits an EPC contractor — "
        "this business is judged on order inflow growth, margin quality, and software/digital mix, not on "
        "book-to-bill or project execution risk."
    ),
}
