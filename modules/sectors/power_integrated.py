# modules/sectors/power_integrated.py
"""
Integrated Power Utility — Sector Module
==========================================
For companies genuinely spanning generation, transmission/distribution, and
increasingly renewables/EV under one listed entity (Tata Power is the clear
Indian example). Unlike power_generation/power_transmission/power_distribution,
this module deliberately keeps a cross-segment frame — but still separates
out which risks belong to which part of the business, rather than treating
"Power Utilities" as one undifferentiated blob the way the old module did.
"""

SECTOR_CONFIG: dict = {
    "slug": "power_integrated",
    "display_name": "Integrated Power Utility",

    "key_metrics": [
        {"id": "renewable_capacity_pct", "label": "Renewable Capacity Mix",     "unit": "%", "yf_key": None,             "higher_is_better": True},
        {"id": "atc_losses",             "label": "AT&C Losses (Distribution Arm)", "unit": "%", "yf_key": None,        "higher_is_better": False},
        {"id": "plf",                    "label": "Plant Load Factor (Generation Arm)", "unit": "%", "yf_key": None,    "higher_is_better": True},
        {"id": "debt_equity",            "label": "Debt/Equity",                "unit": "x", "yf_key": "debtToEquity", "higher_is_better": False},
        {"id": "roe",                    "label": "Return on Equity",           "unit": "%", "yf_key": "returnOnEquity","higher_is_better": True},
        {"id": "receivable_days",        "label": "Receivable Days",            "unit": "days", "yf_key": None,         "higher_is_better": False},
    ],

    "scoring_rules": [
        {"metric": "renewable_capacity_pct", "op": ">", "threshold": 40.0, "points": 20, "max": 20},
        {"metric": "renewable_capacity_pct", "op": ">", "threshold": 20.0, "points": 10, "max": 20},
        {"metric": "debt_equity",            "op": "<", "threshold": 1.5,  "points": 20, "max": 20},
        {"metric": "debt_equity",            "op": "<", "threshold": 2.5,  "points": 10, "max": 20},
        {"metric": "roe",                    "op": ">", "threshold": 12.0, "points": 20, "max": 20},
        {"metric": "atc_losses",             "op": "<", "threshold": 12.0, "points": 20, "max": 20},
        {"metric": "receivable_days",        "op": "<", "threshold": 90.0, "points": 20, "max": 20},
    ],
    "score_max": 100,

    "risk_factors": [
        "Legacy thermal generation carries stranded-asset and fuel-cost risk even while the renewable/"
        "distribution arms grow — the segments don't share the same risk profile and shouldn't be assessed "
        "as if they do",
        "Execution complexity of running generation, distribution, and renewables under different regulatory "
        "regimes simultaneously",
        "Discom/distribution-arm receivable and AT&C-loss risk on the distribution business specifically",
        "High consolidated leverage from funding expansion across multiple capital-intensive segments at once",
        "Renewable/EV capex funding risk if execution outpaces cash generation from the legacy business",
    ],

    "moat_factors": [
        {"factor": "Vertical Integration",       "description": "Presence across generation, distribution, and increasingly renewables reduces single-segment counterparty risk versus a pure-play in any one part of the value chain"},
        {"factor": "Brand & Distribution Reach",  "description": "An established consumer-facing brand and distribution network in its license areas is a real, hard-to-replicate asset for a new entrant"},
        {"factor": "Renewable/EV Growth Optionality", "description": "An existing generation and distribution base gives a natural platform to scale renewables and EV-charging infrastructure faster than a green-field entrant"},
        {"factor": "Multi-Regulator Execution Track Record", "description": "Operating successfully across multiple state regulatory regimes simultaneously is a genuine execution capability, not a given"},
    ],

    "bull_case": [
        "Renewable and EV-charging infrastructure build-out is the primary growth engine, structurally "
        "reducing reliance on the legacy thermal generation business over time",
        "Diversified earnings across generation, distribution, and renewables reduce dependence on any single "
        "segment's cycle",
        "Distribution-arm AT&C loss reduction directly improving consolidated margins",
        "Brand and existing distribution reach giving a faster path to scale in new-energy businesses (solar, "
        "EV charging) than a green-field competitor",
    ],

    "bear_case": [
        "Legacy thermal generation exposes part of the business to stranded-asset and fuel-cost risk even as "
        "other segments grow — the group's blended metrics can mask a weak legacy segment",
        "Execution complexity and capital allocation across generation, distribution, and renewables "
        "simultaneously raises the risk of underinvestment in any one segment",
        "Distribution-arm receivable and AT&C-loss risk drags on consolidated cash flow",
        "High consolidated leverage from funding multiple capital-intensive expansion tracks at once, "
        "limiting flexibility without equity dilution",
    ],

    "red_flags": [
        {"condition": "debt_equity > 2.5",     "severity": "high",   "message": "D/E > 2.5x — high consolidated leverage across multiple capital-intensive segments"},
        {"condition": "atc_losses > 18",       "severity": "medium", "message": "Distribution-arm AT&C losses > 18% — dragging on consolidated margins"},
        {"condition": "receivable_days > 120", "severity": "medium", "message": "Receivable days > 120 — payment-delay strain somewhere in the value chain"},
    ],

    "valuation": {
        "primary":   ["Sum-of-the-Parts (SOTP)", "P/E"],
        "secondary": ["EV/EBITDA", "P/B Ratio"],
        "notes": (
            "An integrated utility spanning legacy thermal generation, regulated distribution, and a growing "
            "renewables/EV business is best valued on a sum-of-the-parts basis — a single blended P/E or "
            "EV/EBITDA can understate the renewables arm (which may deserve a growth multiple) or overstate "
            "the legacy thermal book (which may deserve a declining/stranded-asset discount)."
        ),
    },

    "llm_context": (
        "This is a VERTICALLY INTEGRATED power utility (e.g. Tata Power) spanning generation, distribution, "
        "and a growing renewables/EV-charging business — distinct from a pure GENERATION company (NTPC), "
        "pure TRANSMISSION company (Power Grid), or pure DISTRIBUTION company (Torrent Power, CESC). "
        "Because this company spans multiple segments, do not describe it with a single undifferentiated "
        "risk/moat profile — legacy thermal generation carries fuel-cost and stranded-asset risk, the "
        "distribution arm carries AT&C-loss and receivable risk, and the renewables/EV business is the "
        "primary growth driver with its own execution and funding risk. A blended consolidated metric can "
        "mask a weak legacy segment being offset by a strong growth segment; where the source data allows, "
        "note which segment is driving the number rather than presenting it as one uniform business. "
        "The dominant BULL theme is the renewables/EV growth engine built on an existing distribution/brand "
        "platform. The dominant BEAR theme is the drag from legacy thermal stranded-asset risk and "
        "distribution-arm AT&C losses even as the growth segment scales."
    ),
}
