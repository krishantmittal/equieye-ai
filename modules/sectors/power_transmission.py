# modules/sectors/power_transmission.py
"""
Power Transmission — Sector Module
====================================
Split out of power_utilities.py, which previously described generation,
transmission, and distribution as one undifferentiated business. A pure
transmission company (Power Grid Corporation, Adani Energy Solutions'
transmission arm) doesn't generate power and carries none of a generator's
fuel risk — it moves power for a regulated fee, paid on availability of its
lines, not on how much power flows through them. Mixing in PPAs, plant load
factor, coal-linkage/fuel security, and "diversified generation mix" (all
genuinely generation-side concepts) produced moat/bull/bear text for Power
Grid that discussed fuel security and generation diversification — things
that don't apply to a transmission-only business at all.
"""

SECTOR_CONFIG: dict = {
    "slug": "power_transmission",
    "display_name": "Power Transmission",

    "key_metrics": [
        {"id": "transmission_availability", "label": "System Availability",        "unit": "%", "yf_key": None,             "higher_is_better": True},
        {"id": "regulated_equity_pct",      "label": "Regulated Equity Mix",       "unit": "%", "yf_key": None,             "higher_is_better": True},
        {"id": "debt_equity",               "label": "Debt/Equity",                "unit": "x", "yf_key": "debtToEquity",  "higher_is_better": False},
        {"id": "roe",                       "label": "Return on Equity",           "unit": "%", "yf_key": "returnOnEquity","higher_is_better": True},
        {"id": "receivable_days",           "label": "Receivable Days (State Utilities)", "unit": "days", "yf_key": None,   "higher_is_better": False},
        {"id": "network_km",                "label": "Transmission Network (ckm)", "unit": "ckm", "yf_key": None,          "higher_is_better": True},
        {"id": "tbcb_win_rate",             "label": "TBCB Project Win Rate",      "unit": "%", "yf_key": None,             "higher_is_better": True},
    ],

    "scoring_rules": [
        {"metric": "transmission_availability", "op": ">", "threshold": 99.5, "points": 25, "max": 25},
        {"metric": "transmission_availability", "op": ">", "threshold": 98.0, "points": 12, "max": 25},
        {"metric": "regulated_equity_pct",       "op": ">", "threshold": 70.0, "points": 20, "max": 20},
        {"metric": "regulated_equity_pct",       "op": ">", "threshold": 50.0, "points": 10, "max": 20},
        {"metric": "debt_equity",                "op": "<", "threshold": 1.5,  "points": 20, "max": 20},
        {"metric": "debt_equity",                "op": "<", "threshold": 2.5,  "points": 10, "max": 20},
        {"metric": "roe",                        "op": ">", "threshold": 14.0, "points": 20, "max": 20},
        {"metric": "receivable_days",            "op": "<", "threshold": 60.0, "points": 15, "max": 15},
    ],
    "score_max": 100,

    "risk_factors": [
        "State transmission utility / discom payment delays — receivables can strain working capital even "
        "though the company itself has no fuel-cost exposure",
        "Competitive bidding (TBCB — Tariff-Based Competitive Bidding) is compressing IRRs on new transmission "
        "projects versus the older cost-plus regulated-return regime",
        "Regulatory risk: CERC-set allowed ROE can be revised downward at tariff resets",
        "Project execution and cost-overrun risk on new large transmission lines (right-of-way delays, land "
        "acquisition disputes)",
        "High leverage from long-gestation, capital-intensive network buildout",
        "Revenue concentration in a small number of large state/inter-state transmission contracts",
    ],

    "moat_factors": [
        {"factor": "Regulated Monopoly in Service Territory", "description": "Once built, a transmission line has no competing route — this is a structural, not competitive, monopoly within its corridor"},
        {"factor": "Availability-Based Tariff (Not Volume-Based)", "description": "Paid on system availability, not on how much power actually flows — this removes demand/offtake risk that a generator or distributor carries"},
        {"factor": "Regulated Asset Base / Cost-Plus Returns",     "description": "CERC-regulated ROE on the asset base provides bond-like earnings visibility, distinct from a merchant or volume-driven business"},
        {"factor": "Right-of-Way & Execution Barrier",             "description": "Land acquisition and right-of-way for new corridors takes years — a structural barrier to new entrants, independent of capital availability"},
        {"factor": "Pan-India / Interstate Network Scale",         "description": "An incumbent's existing interstate network and grid-integration experience gives it a real execution edge in competitive bids (TBCB) for new lines"},
    ],

    "bull_case": [
        "Renewable energy integration is driving a large multi-year capex cycle in new evacuation "
        "infrastructure — transmission is a direct, structural beneficiary of the energy transition, not "
        "a business it competes against",
        "Grid modernisation and inter-regional transmission corridor buildout supporting sustained capex "
        "growth",
        "Regulated-equity-model earnings are bond-like and largely insulated from the commodity/fuel cycles "
        "that affect generation",
        "Incumbent scale and execution track record support a strong win rate in competitive (TBCB) bidding "
        "for new lines",
        "Grid strengthening and smart-grid/digitalisation initiatives opening new regulated capex avenues",
    ],

    "bear_case": [
        "Competitive bidding (TBCB) structurally compresses the return premium on new projects versus the "
        "company's older cost-plus regulated asset base — new capex earns a lower incremental ROE than the "
        "legacy book",
        "State transmission utility / discom payment delays straining receivables and working capital",
        "Regulatory ROE cuts at periodic tariff resets directly compress the earnings base",
        "Execution and cost-overrun risk on large new corridors (land acquisition, right-of-way delays)",
        "High leverage from capital-intensive network buildout limits flexibility without equity dilution",
    ],

    "red_flags": [
        {"condition": "receivable_days > 120",       "severity": "high",   "message": "Receivable days > 120 — state utility/discom payment delays straining cash flow"},
        {"condition": "debt_equity > 2.5",            "severity": "high",   "message": "D/E > 2.5x — high leverage for a capital-intensive regulated network business"},
        {"condition": "transmission_availability < 98","severity": "medium","message": "System availability < 98% — below the threshold that typically maximises regulated incentive income"},
        {"condition": "regulated_equity_pct < 40",    "severity": "low",    "message": "Low regulated-equity mix — more exposure to competitive-bid (TBCB) returns, less bond-like earnings stability"},
    ],

    "valuation": {
        "primary":   ["P/B Ratio", "Dividend Yield"],
        "secondary": ["EV/EBITDA"],
        "notes": (
            "Regulated transmission utilities are valued like infrastructure/bond proxies — P/B anchored to "
            "the allowed regulatory ROE (typically 1.5-2.5x book for a stable ~14-16% RoE business), with "
            "dividend yield as a core part of the return, not just capital appreciation. This is NOT a "
            "generation company — do not apply fuel-cost or PLF-driven valuation logic here."
        ),
    },

    "llm_context": (
        "This is a POWER TRANSMISSION company (e.g. Power Grid Corporation, Adani Energy Solutions' "
        "transmission arm) — distinct from GENERATION (NTPC, Adani Power, JSW Energy) and DISTRIBUTION/"
        "discom (Torrent Power, CESC). Don't use generation-side concepts: no plant load factor, no fuel/"
        "coal-linkage security, no PPAs (signed by generators, not transmission companies), no 'diversified "
        "generation mix'. This company moves power others generate, under a regulated, availability-based "
        "tariff, and is paid whether or not power actually flows — unlike a generator paid per unit sold. "
        "Focus on: regulated-equity/cost-plus ROE model, system availability (not PLF), TBCB win rate and "
        "margin compression on new projects versus the legacy regulated book, state discom receivable "
        "delays, and execution track record on large capital projects (right-of-way, land acquisition). "
        "BULL theme: renewable integration needs massive new transmission evacuation infrastructure — this "
        "company is a direct beneficiary of the energy transition, the opposite of a thermal generator "
        "threatened by it. BEAR theme: TBCB margin compression on new projects and discom payment delays — "
        "not fuel cost, stranded generation assets, or renewables commodity-cycle competition."
    ),
}
