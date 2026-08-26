# modules/sectors/capital_goods.py
"""
Capital Goods / Industrial Machinery — Sector Module
"""

SECTOR_CONFIG: dict = {
    "slug": "capital_goods",
    "display_name": "Capital Goods",

    "key_metrics": [
        {"id": "order_book",        "label": "Order Book",             "unit": "₹Cr", "yf_key": None, "higher_is_better": True},
        {"id": "book_to_bill",      "label": "Book-to-Bill Ratio",      "unit": "x",   "yf_key": None, "higher_is_better": True},
        {"id": "execution_pace",    "label": "Execution / Revenue Conversion", "unit": "%", "yf_key": None, "higher_is_better": True},
        {"id": "working_capital_days", "label": "Working Capital Days", "unit": "days", "yf_key": None, "higher_is_better": False},
        {"id": "ebitda_margin",     "label": "EBITDA Margin",          "unit": "%",   "yf_key": "ebitdaMargins", "higher_is_better": True},
        {"id": "roce",              "label": "Return on Capital Employed", "unit": "%", "yf_key": "returnOnEquity", "higher_is_better": True},
    ],

    "risk_factors": [
        "Order-book to execution lag — projects can slip, delaying revenue recognition for years",
        "Working capital intensive — long receivable cycles from government/institutional clients",
        "Cyclicality tied to capex cycle (private + government infrastructure spending)",
        "Raw material (steel, copper) price volatility squeezing fixed-price contract margins",
        "Execution risk on large/complex projects (cost overruns, delays, penalties)",
        "Customer concentration risk — large orders from a handful of government or corporate clients",
    ],

    "moat_factors": [
        {"factor": "Order Book Visibility",   "description": "A large, diversified order book gives multi-year revenue visibility"},
        {"factor": "Execution Track Record",  "description": "Proven on-time, on-budget delivery is the key differentiator that wins repeat business"},
        {"factor": "Engineering / IP",        "description": "Proprietary design or technology reduces reliance on licensed foreign technology"},
        {"factor": "Scale & Manufacturing",   "description": "In-house manufacturing scale lowers unit cost versus smaller fabricators"},
        {"factor": "After-Sales / Service",   "description": "Long-life industrial equipment creates a recurring spares and service annuity"},
    ],

    "bull_case": [
        "Government infrastructure/capex push (roads, rail, defence, power) driving order inflows",
        "Private sector capex cycle recovery adding to order book beyond government spending",
        "Operating leverage as execution scales against a large order backlog",
        "Import substitution / 'Make in India' policy tailwinds for domestic manufacturers",
        "Export order wins diversifying away from purely domestic demand",
    ],

    "bear_case": [
        "Order book execution delays due to land acquisition, clearances, or funding issues",
        "Raw material cost spikes eroding margins on fixed-price legacy orders",
        "Government capex slowdown ahead of elections or fiscal tightening",
        "Working capital strain from delayed customer payments (especially government clients)",
        "Intensifying competition compressing bid margins on new order wins",
    ],

    "red_flags": [
        {"condition": "de_ratio > 1.5",        "severity": "high",   "message": "D/E > 1.5x — high leverage in a working-capital-intensive, cyclical business"},
        {"condition": "ebitda_margin < 8",      "severity": "high",   "message": "EBITDA margin < 8% — thin margins leave little cushion for cost overruns"},
        {"condition": "roce < 10",              "severity": "medium", "message": "ROCE < 10% — capital-intensive business not clearing a reasonable cost of capital"},
    ],

    "valuation": {
        "primary":   ["P/E", "EV/EBITDA"],
        "secondary": ["Order Book / Market Cap"],
        "notes": (
            "Capital goods companies are usually valued on P/E relative to their order-book growth and "
            "execution track record. A large order book with poor execution history deserves a valuation "
            "discount versus one with proven on-time delivery. EV/EBITDA is a useful cross-check, especially "
            "for capital-intensive manufacturers."
        ),
        "bands": {
            "pe_ratio": {"attractive": (0, 20), "fair": (20, 35), "expensive": (35, 999)},
        },
    },

    "llm_context": (
        "This is a CAPITAL GOODS / INDUSTRIAL MACHINERY company. Focus on: order book size and quality, "
        "book-to-bill ratio, execution track record, working capital cycle, and exposure to the government "
        "vs. private capex cycle. A large order book means little without a proven execution track record — "
        "flag companies with a history of project delays or cost overruns. Working capital intensity "
        "(especially receivables from government clients) is a key risk to call out."
    ),
}
