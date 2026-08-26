# modules/sectors/epc_engineering.py
"""
EPC / Engineering — Sector Module
===================================
Split out from capital_goods.py: EPC and engineering-construction
contractors (Larsen & Toubro, Thermax, KEC International, Engineers
India, and similar) win large, often fixed-price, multi-year projects
and are judged on execution — order book size and quality, book-to-bill,
project margins, and working capital discipline — not on product/software
IP the way an automation major (ABB, Siemens) is, and not on brand/
distribution the way an electrical-goods company (Havells, Polycab) is.
This module keeps the original capital_goods.py framing (order book,
execution track record, working capital intensity), which is the most
accurate fit for this specific sub-group.
"""

SECTOR_CONFIG: dict = {
    "slug": "epc_engineering",
    "display_name": "EPC / Engineering",

    "key_metrics": [
        {"id": "order_book",           "label": "Order Book",                     "unit": "₹Cr", "yf_key": None, "higher_is_better": True},
        {"id": "book_to_bill",         "label": "Book-to-Bill Ratio",              "unit": "x",   "yf_key": None, "higher_is_better": True},
        {"id": "execution_pace",       "label": "Execution / Revenue Conversion",  "unit": "%",   "yf_key": None, "higher_is_better": True},
        {"id": "working_capital_days", "label": "Working Capital Days",            "unit": "days","yf_key": None, "higher_is_better": False},
        {"id": "ebitda_margin",        "label": "EBITDA Margin",                   "unit": "%",   "yf_key": "ebitdaMargins", "higher_is_better": True},
        {"id": "roce",                 "label": "Return on Capital Employed",      "unit": "%",   "yf_key": "returnOnEquity", "higher_is_better": True},
    ],

    "risk_factors": [
        "Order-book to execution lag — projects can slip, delaying revenue recognition for years",
        "Working capital intensive — long receivable cycles from government/institutional clients",
        "Cyclicality tied to the capex cycle (private + government infrastructure spending)",
        "Raw material (steel, copper) price volatility squeezing fixed-price contract margins",
        "Execution risk on large/complex projects (cost overruns, delays, contractual penalties)",
        "Customer concentration risk — large orders from a handful of government or corporate clients",
    ],

    "moat_factors": [
        {"factor": "Order Book Visibility",  "description": "A large, diversified order book gives multi-year revenue visibility"},
        {"factor": "Execution Track Record", "description": "Proven on-time, on-budget delivery is the key differentiator that wins repeat business and de-risks future bids"},
        {"factor": "Engineering / Design IP","description": "Proprietary process design or technology reduces reliance on licensed foreign technology"},
        {"factor": "Scale & Balance Sheet",  "description": "Balance sheet strength to bid, bond, and fund large projects is itself a barrier smaller contractors can't clear"},
        {"factor": "Diversified Order Mix",  "description": "Spread across sectors (power, infra, hydrocarbon, defence) reduces dependence on any single capex cycle"},
    ],

    "bull_case": [
        "Government infrastructure/capex push (roads, rail, defence, power) driving order inflows",
        "Private sector capex cycle recovery adding to order book beyond government spending",
        "Operating leverage as execution scales against a large order backlog",
        "Import substitution / 'Make in India' policy tailwinds for domestic EPC players",
        "Export/international order wins diversifying away from purely domestic demand",
    ],

    "bear_case": [
        "Order book execution delays due to land acquisition, clearances, or funding issues",
        "Raw material cost spikes eroding margins on fixed-price legacy orders",
        "Government capex slowdown ahead of elections or fiscal tightening",
        "Working capital strain from delayed customer payments (especially government clients)",
        "Intensifying bid competition compressing margins on new order wins",
    ],

    "red_flags": [
        {"condition": "de_ratio > 1.5",    "severity": "high",   "message": "D/E > 1.5x — high leverage in a working-capital-intensive, cyclical business"},
        {"condition": "ebitda_margin < 8",  "severity": "high",   "message": "EBITDA margin < 8% — thin margins leave little cushion for cost overruns"},
        {"condition": "roce < 10",          "severity": "medium", "message": "ROCE < 10% — capital-intensive business not clearing a reasonable cost of capital"},
    ],

    "valuation": {
        "primary":   ["P/E", "EV/EBITDA"],
        "secondary": ["Order Book / Market Cap"],
        "notes": (
            "EPC/engineering companies are usually valued on P/E relative to their order-book growth and "
            "execution track record. A large order book with a poor execution history deserves a valuation "
            "discount versus one with proven on-time delivery. EV/EBITDA is a useful cross-check given the "
            "working-capital and leverage intensity of the business."
        ),
        "bands": {
            "pe_ratio": {"attractive": (0, 20), "fair": (20, 35), "expensive": (35, 999)},
        },
    },

    "llm_context": (
        "This is an EPC / ENGINEERING-CONSTRUCTION company (e.g. Larsen & Toubro, Thermax, KEC International, "
        "Engineers India) — distinct from an industrial automation/product company (ABB, Siemens), which sells "
        "technology products rather than executing fixed-price projects, and distinct from a branded "
        "electrical-goods company (Havells, Polycab), which sells through distribution rather than winning "
        "project contracts. Focus on: order book size and quality, book-to-bill ratio, execution track record, "
        "working capital cycle, and exposure to the government vs. private capex cycle. A large order book "
        "means little without a proven execution track record — flag companies with a history of project "
        "delays or cost overruns. Working capital intensity (especially receivables from government clients) "
        "is a key risk to call out."
    ),
}
