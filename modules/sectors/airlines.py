# modules/sectors/airlines.py
"""
Airlines / Aviation — Sector Module
====================================
Split out of "generic" — airlines were previously falling through to the
unclassified fallback (no keyword rule existed at all), which produced two
concrete, user-visible problems:

1. CONTRADICTORY DEBT READS. The generic module's red flag rule fires at
   D/E > 1.5x — a normal-industrial threshold. But airline balance sheets
   are structurally different: Ind AS 116 / IFRS 16 requires capitalising
   leased aircraft as right-of-use assets with a matching lease liability,
   which mechanically inflates reported D/E for any carrier that leases
   (rather than owns) most of its fleet — the Indian norm. A D/E of 6-9x is
   commonplace for a healthy airline and does NOT mean the same thing it
   would for an industrial company. Under "generic", the LLM had no sector
   norm to calibrate against and would sometimes praise "reasonable debt
   levels" in the same breath the rule-based detector flagged it "High
   Severity" — two halves of the app contradicting each other. Giving
   airlines their own red_flags thresholds (tuned to lease-inflated norms)
   and an explicit llm_context callout fixes both sides at once.
2. GENERIC BUSINESS/MOAT/BULL/BEAR TEXT. Without a sector match, snapshot,
   moat, and bull/bear text fell back to boilerplate ("operates in the
   Industrials sector", "Cost Structure", "Competition", "Regulatory
   Risks") instead of the real drivers of an airline's economics (ATF
   price, load factor, CASK, fleet commonality, slot access, engine
   groundings, etc.) that any real equity analyst would use.
"""

SECTOR_CONFIG: dict = {
    "slug": "airlines",
    "display_name": "Airlines / Aviation",

    "key_metrics": [
        {"id": "load_factor",      "label": "Passenger Load Factor",  "unit": "%", "yf_key": None,            "higher_is_better": True},
        {"id": "cask",             "label": "CASK (Cost per ASK)",    "unit": "₹", "yf_key": None,            "higher_is_better": False},
        {"id": "yield_per_rpk",    "label": "Yield (per RPK)",        "unit": "₹", "yf_key": None,            "higher_is_better": True},
        {"id": "ebitda_margin",    "label": "EBITDAR Margin",         "unit": "%", "yf_key": "ebitdaMargins", "higher_is_better": True},
        {"id": "revenue_growth",   "label": "Revenue Growth (YoY)",   "unit": "%", "yf_key": "revenueGrowth", "higher_is_better": True},
        {"id": "de_ratio",         "label": "Debt/Equity (lease-inflated)", "unit": "x", "yf_key": "debtToEquity", "higher_is_better": False},
    ],

    "scoring_rules": [
        {"metric": "revenue_growth", "op": ">", "threshold": 15.0, "points": 20, "max": 20},
        {"metric": "revenue_growth", "op": ">", "threshold": 8.0,  "points": 12, "max": 20},
        {"metric": "ebitda_margin",  "op": ">", "threshold": 15.0, "points": 20, "max": 20},
        {"metric": "ebitda_margin",  "op": ">", "threshold": 8.0,  "points": 12, "max": 20},
        {"metric": "de_ratio",       "op": "<", "threshold": 3.0,  "points": 20, "max": 20},
        {"metric": "de_ratio",       "op": "<", "threshold": 5.0,  "points": 10, "max": 20},
    ],
    "score_max": 100,

    "risk_factors": [
        "ATF (jet fuel) price volatility — typically 30-40% of operating cost, largely un-hedgeable at scale",
        "Rupee depreciation — fuel, lease rentals, and aircraft/engine maintenance are dollar-denominated",
        "Engine or airframe reliability issues grounding part of the fleet (e.g. Pratt & Whitney geared-turbofan inspections) and forcing costly lease-in of spare capacity",
        "Airport slot and infrastructure congestion at metro hubs capping capacity growth",
        "Fare regulation or government intervention on pricing during demand spikes",
        "Aircraft delivery delays from OEMs (Airbus/Boeing) constraining planned capacity additions",
        "Wage inflation, particularly for pilots, amid industry-wide crew shortages",
        "Geopolitical disruption to international routes (airspace closures, conflict zones)",
        "Reported D/E is structurally inflated by Ind AS 116 lease capitalisation — not directly comparable to a non-aviation industrial company",
    ],

    "moat_factors": [
        {"factor": "Cost Leadership (CASK)",       "description": "Lowest cost-per-ASK among domestic peers, driven by high aircraft utilisation and a low-cost operating model"},
        {"factor": "Domestic Network & Slot Access", "description": "Scale of domestic market share and airport slot holdings at capacity-constrained metro hubs"},
        {"factor": "Fleet Commonality",             "description": "A single narrow-body family (e.g. A320/A321neo) across the fleet reduces pilot training, maintenance, and spare-parts costs versus a mixed fleet"},
        {"factor": "Brand & Loyalty",               "description": "On-time performance reputation and a loyalty/frequent-flyer program driving repeat bookings and ancillary revenue"},
    ],

    "bull_case": [
        "Structural growth in domestic air travel penetration as a large, under-penetrated market matures",
        "Fleet expansion and induction of fuel-efficient next-gen aircraft lowering CASK over time",
        "Low-cost, point-to-point operating model sustaining a cost advantage over full-service rivals",
        "Airport slot leadership at capacity-constrained metro hubs acting as a barrier to new entrants",
        "International network expansion (wide-body induction, codeshare/interline partnerships) opening a higher-yield revenue pool",
        "Ancillary revenue growth (seat selection, baggage, cargo, loyalty) improving margin per passenger",
    ],

    "bear_case": [
        "ATF price spikes compressing margins with limited ability to pass costs through fully via fares",
        "Rupee depreciation raising the real cost of dollar-denominated fuel, leases, and maintenance",
        "Engine or airframe groundings (e.g. geared-turbofan inspections) forcing expensive short-term wet-lease capacity and idling owned aircraft",
        "Airport congestion and slot constraints capping capacity growth at key hubs",
        "Regulatory fare intervention during demand surges limiting pricing power",
        "Aircraft delivery delays from OEMs slowing planned capacity and network expansion",
        "Pilot/crew wage inflation amid an industry-wide shortage",
        "Geopolitical disruption forcing costly route diversions or suspensions on international sectors",
    ],

    "red_flags": [
        # Thresholds are deliberately much higher than a normal-industrial
        # module (generic uses >1.5x) because Ind AS 116 lease capitalisation
        # structurally inflates every Indian airline's reported D/E — see
        # module docstring above. These bands reflect what's actually
        # abnormal for a lease-heavy airline balance sheet, not a generic
        # corporate one.
        {"condition": "de_ratio > 7",       "severity": "high",   "message": "D/E > 7x — elevated even after allowing for Ind AS 116 lease capitalisation; check liquidity and free cash flow before treating this as manageable"},
        {"condition": "de_ratio > 4.5",     "severity": "medium", "message": "D/E > 4.5x — typical range for a lease-heavy airline balance sheet, but still worth tracking against cash reserves"},
        {"condition": "revenue_growth < 0", "severity": "high",   "message": "Negative revenue growth — falling demand or capacity cuts"},
        {"condition": "ebitda_margin < 5",  "severity": "medium", "message": "EBITDAR margin < 5% — thin cushion against fuel/currency shocks"},
    ],

    "valuation": {
        "primary":   ["EV/EBITDAR", "P/E"],
        "secondary": ["P/B", "EV/Available Seat Km"],
        "notes": (
            "EV/EBITDAR (not EV/EBITDA) is the industry-standard airline valuation multiple — it adds back "
            "lease rentals so lessee-heavy and owner-heavy fleets are compared on a like-for-like basis. "
            "P/E and D/E should be read with the understanding that Ind AS 116 lease capitalisation inflates "
            "both reported debt and depreciation relative to a non-aviation industrial company."
        ),
        "bands": {
            "pe_ratio": {"attractive": (0, 12), "fair": (12, 22), "expensive": (22, 999)},
        },
    },

    "llm_context": (
        "This is an AIRLINE / AVIATION company. Focus on: passenger load factor, CASK and yield trends, "
        "fleet size/composition and commonality (e.g. an all-A320-family fleet lowers training/maintenance "
        "cost), domestic market share and airport slot access, ATF cost exposure, and rupee depreciation "
        "impact on dollar-denominated costs. "
        "LEVERAGE: Indian airlines report high D/E (often 4-9x+) because Ind AS 116 capitalises leased "
        "aircraft as right-of-use assets with a matching lease liability — a structural accounting effect "
        "of a lease-funded fleet, not distress by itself. Never call it 'reasonable' or 'low' as if "
        "benchmarked against a normal industrial company; frame it as 'elevated, in line with the sector's "
        "lease-heavy capital structure' and note that liquidity/free cash flow matter more than the raw "
        "ratio. "
        "EARNINGS SWINGS: a large loss-to-profit (or profit-to-loss) swing at an airline is often a "
        "demand-cycle effect — e.g. post-pandemic travel recovery off a depressed base, or an ATF/currency "
        "shock — rather than a corporate action. Don't default to 'likely a demerger or restructuring' "
        "language without explicit evidence; a cyclical recovery or fuel/currency shock is at least as "
        "plausible."
    ),
}
