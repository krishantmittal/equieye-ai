# modules/sectors/engineering_rd.py
"""
Engineering R&D (ER&D) — Sector Module
========================================
Split out from it_services.py (see PR discussion): ER&D / product
engineering services companies (L&T Technology Services, Tata
Technologies, KPIT Technologies, Cyient, and similar outsourced
engineering-design players) share IT services' offshore-delivery cost
structure, but sell into a completely different demand cycle — auto
OEM/aerospace/industrial R&D budgets, not enterprise IT budgets — and
their moat is engineering domain IP and design-cycle switching costs,
not client-relationship/talent-pool scale. Treating them as "IT
services" produced identical moat/bull/bear/risk text to TCS/Infosys/
Wipro, which is misleading — they don't compete for the same deals or
face the same demand drivers.
"""

SECTOR_CONFIG: dict = {
    "slug": "engineering_rd",
    "display_name": "Engineering R&D (ER&D)",

    "key_metrics": [
        {"id": "revenue_growth",       "label": "Revenue Growth (YoY)",     "unit": "%",  "yf_key": "revenueGrowth",   "higher_is_better": True},
        {"id": "usd_rev_growth",       "label": "USD Revenue Growth",       "unit": "%",  "yf_key": None,              "higher_is_better": True},
        {"id": "ebitda_margin",        "label": "EBITDA Margin",            "unit": "%",  "yf_key": "ebitdaMargins",   "higher_is_better": True},
        {"id": "client_concentration", "label": "Top-5 Client Revenue",     "unit": "%",  "yf_key": None,              "higher_is_better": False},
        {"id": "auto_vertical_exposure","label": "Auto/Transportation Revenue Mix", "unit": "%", "yf_key": None,      "higher_is_better": False},
        {"id": "deal_wins_tcv",        "label": "Deal Win TCV",             "unit": "$B", "yf_key": None,              "higher_is_better": True},
        {"id": "roe",                  "label": "Return on Equity",         "unit": "%",  "yf_key": "returnOnEquity",  "higher_is_better": True},
        {"id": "fcf_conversion",       "label": "FCF Conversion",           "unit": "%",  "yf_key": None,              "higher_is_better": True},
    ],

    "scoring_rules": [
        {"metric": "revenue_growth",   "op": ">", "threshold": 15.0, "points": 20, "max": 20},
        {"metric": "revenue_growth",   "op": ">", "threshold": 8.0,  "points": 12, "max": 20},
        {"metric": "revenue_growth",   "op": ">", "threshold": 3.0,  "points": 5,  "max": 20},
        {"metric": "ebitda_margin",    "op": ">", "threshold": 22.0, "points": 20, "max": 20},
        {"metric": "ebitda_margin",    "op": ">", "threshold": 16.0, "points": 12, "max": 20},
        {"metric": "ebitda_margin",    "op": ">", "threshold": 12.0, "points": 6,  "max": 20},
        {"metric": "client_concentration", "op": "<", "threshold": 20.0, "points": 15, "max": 20},
        {"metric": "client_concentration", "op": "<", "threshold": 30.0, "points": 8,  "max": 20},
        {"metric": "roe",              "op": ">", "threshold": 22.0, "points": 10, "max": 10},
        {"metric": "roe",              "op": ">", "threshold": 15.0, "points": 6,  "max": 10},
    ],
    "score_max": 100,

    "risk_factors": [
        "Automotive OEM R&D budget cuts — auto is typically the largest single vertical for ER&D players",
        "Aerospace program delays or cancellations push out multi-year engagement revenue",
        "Industrial/manufacturing capex slowdown reduces smart-manufacturing and digital-twin engagement pipelines",
        "US/EU industrial recession compresses discretionary engineering-outsourcing budgets",
        "Client/OEM concentration: a handful of large auto or aerospace clients often account for an outsized revenue share",
        "Currency: majority-USD/EUR revenue against an INR cost base — rupee appreciation compresses margins",
        "In-house insourcing risk: large OEMs building internal engineering-technology centres can claw back outsourced scope",
        "War-for-talent wage inflation in specialized domains (embedded, automotive software, chip design) not fungible with generalist IT hiring",
    ],

    "moat_factors": [
        {"factor": "Engineering IP & Digital Twins",  "description": "Proprietary design accelerators, reusable engineering IP, and digital-twin/simulation platforms reduce delivery time and are hard to replicate from scratch"},
        {"factor": "Domain Certifications",           "description": "Aerospace (AS9100), automotive (ASPICE, ISO 26262 functional safety), and medical device (IEC 62304) certifications are procurement gatekeepers few competitors clear"},
        {"factor": "Embedded & Domain Engineering Talent", "description": "Specialized automotive software, embedded systems, and chip-adjacent engineering talent is a narrower, harder-to-scale pool than generalist IT staffing"},
        {"factor": "Long Design-Cycle Switching Costs","description": "Once embedded in a multi-year vehicle/aircraft/product design program, switching engineering partners means re-certifying and re-onboarding — a structurally higher switching cost than a typical IT services contract"},
        {"factor": "Platform Relationships",           "description": "Being design partner on a client's next-generation platform (EV architecture, aircraft program) creates a multi-year revenue tail tied to that platform's lifecycle"},
    ],

    "bull_case": [
        "ER&D outsourcing penetration is still low relative to IT services — a long structural runway as OEMs offshore more engineering spend",
        "Software-defined vehicle and EV transition is forcing automakers to expand engineering spend on domains (embedded software, battery/motor control) that outsourced ER&D players are built for",
        "Smart manufacturing and digital-twin adoption across industrial clients is a new, higher-margin engagement category beyond legacy product engineering",
        "Medical device and healthcare engineering is a growing, less cyclical diversification vertical away from auto/industrial concentration",
        "Aerospace platform ramp-ups (new aircraft programs, defense localization) can provide long, multi-year revenue tails once won",
    ],

    "bear_case": [
        "Automotive R&D slowdown or an OEM-wide EV capex pause directly hits the largest ER&D demand vertical",
        "Industrial/manufacturing recession in the US or Europe compresses discretionary engineering-outsourcing budgets",
        "Aerospace program delays (a common industry pattern) push out revenue recognition on large multi-year engagements",
        "Loss of or budget cuts at a top client is a materially larger earnings risk here than in diversified IT services, given typically higher client concentration",
        "Large OEMs insourcing engineering capability (building captive GCCs/technology centres) claws back outsourced scope over time",
    ],

    "red_flags": [
        {"condition": "revenue_growth < 2",     "severity": "high",   "message": "Revenue growth < 2% — demand headwinds from OEM/industrial R&D budget cuts"},
        {"condition": "ebitda_margin < 12",      "severity": "high",   "message": "EBITDA margin < 12% — margin compression below sustainable levels for a specialized-talent business"},
        {"condition": "client_concentration > 25", "severity": "medium", "message": "Top-5 clients > 25% revenue — concentration risk is structurally higher here than diversified IT services"},
        {"condition": "auto_vertical_exposure > 40", "severity": "medium", "message": "Automotive vertical > 40% of revenue — high single-cycle exposure to auto OEM R&D spend"},
        {"condition": "usd_rev_growth < 0",      "severity": "high",   "message": "Negative USD revenue growth — real demand contraction underway"},
    ],

    "llm_context": (
        "This is an Engineering R&D (ER&D) / product engineering services company — "
        "distinct from generalist enterprise IT services (TCS/Infosys/Wipro/HCLTech), which "
        "it does not directly compete with for the same deals. "
        "It sells outsourced engineering design, embedded software, digital manufacturing, "
        "and domain engineering (automotive, aerospace, industrial, medical devices) to OEMs "
        "and industrial clients, not enterprise IT/BPO services to CIOs. "
        "Key demand drivers: automotive R&D outsourcing (especially EV/software-defined-vehicle "
        "engineering spend), aerospace program ramps, industrial IoT and smart-manufacturing "
        "adoption, medical device engineering. "
        "Key risks: automotive OEM R&D budget cuts, industrial capex slowdown, aerospace program "
        "delays, and client/OEM concentration (typically higher than diversified IT services). "
        "Do NOT apply generic IT-services framing (T&M billing disruption, visa costs, generalist "
        "attrition) — assess engineering IP, domain certifications (ASPICE/AS9100/IEC 62304), and "
        "design-cycle switching costs instead. D/E and NPA analysis do not apply — this is "
        "asset-light with near-zero debt, like IT services."
    ),
}
