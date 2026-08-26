# modules/sectors/airport_infrastructure.py
"""
Airport Infrastructure / Operators — Sector Module
====================================================
For companies like GMR Airports Infrastructure (Delhi, Hyderabad airports)
or Adani Airport Holdings — was previously falling through to "generic",
same gap as airlines had before the airlines.py module was added.

CRITICAL DISTINCTION FROM AIRLINES: an airport operator does not fly
planes. It owns/operates the physical airport asset under a long-term
regulated concession, earning aeronautical revenue (landing, parking, user
development fees — set/reset periodically by the regulator, AERA in India)
and non-aeronautical revenue (retail, duty-free, cargo, real-estate/city-
side development on airport land). Passenger traffic is still the core
demand driver, but the business economics, regulatory relationship, and
leverage profile are structurally different from an airline's — a
project-finance/concession-capex balance sheet, not a lease-capitalisation
one — so this should NOT reuse the airlines module's Ind AS 116 leverage
framing verbatim.
"""

SECTOR_CONFIG: dict = {
    "slug": "airport_infra",
    "display_name": "Airport Infrastructure",

    "key_metrics": [
        {"id": "passenger_traffic_growth", "label": "Passenger Traffic Growth (YoY)", "unit": "%", "yf_key": None, "higher_is_better": True},
        {"id": "aero_revenue_per_pax",      "label": "Aeronautical Revenue / Passenger", "unit": "₹", "yf_key": None, "higher_is_better": True},
        {"id": "non_aero_revenue_share",    "label": "Non-Aeronautical Revenue Share",   "unit": "%", "yf_key": None, "higher_is_better": True},
        {"id": "ebitda_margin",             "label": "EBITDA Margin",                    "unit": "%", "yf_key": "ebitdaMargins", "higher_is_better": True},
        {"id": "revenue_growth",            "label": "Revenue Growth (YoY)",             "unit": "%", "yf_key": "revenueGrowth", "higher_is_better": True},
        {"id": "de_ratio",                  "label": "Debt/Equity (concession-capex heavy)", "unit": "x", "yf_key": "debtToEquity", "higher_is_better": False},
    ],

    "scoring_rules": [
        {"metric": "revenue_growth",         "op": ">", "threshold": 15.0, "points": 20, "max": 20},
        {"metric": "revenue_growth",         "op": ">", "threshold": 8.0,  "points": 12, "max": 20},
        {"metric": "ebitda_margin",          "op": ">", "threshold": 40.0, "points": 20, "max": 20},
        {"metric": "ebitda_margin",          "op": ">", "threshold": 25.0, "points": 12, "max": 20},
        {"metric": "non_aero_revenue_share", "op": ">", "threshold": 40.0, "points": 15, "max": 15},
        {"metric": "de_ratio",               "op": "<", "threshold": 2.0,  "points": 20, "max": 20},
        {"metric": "de_ratio",               "op": "<", "threshold": 3.5,  "points": 10, "max": 20},
    ],
    "score_max": 100,

    "risk_factors": [
        "AERA (or the relevant regulator) periodically resets aeronautical tariffs — an adverse tariff order directly compresses landing/parking/UDF yield per passenger",
        "Passenger traffic is exposed to airline capacity decisions and airline financial health — a struggling or capacity-cutting airline at the airport reduces footfall the operator can't control directly",
        "Long-gestation concession capex — a new terminal or runway takes years to reach the passenger volume that justifies its cost, depressing near-term returns on invested capital",
        "High leverage from project-finance-style concession capex — structurally elevated D/E versus a normal industrial company, though for a different reason than an airline's lease accounting",
        "Non-aeronautical monetisation risk — retail, duty-free, and real-estate/city-side development revenue depend on footfall conversion and execution, not guaranteed by passenger volume alone",
        "Concession-agreement and regulatory risk — revenue-share obligations to the airport authority/state government, and concession-renewal terms, are set outside the company's control",
        "Corporate/group structure complexity — the sector has a history of demergers and restructuring (e.g. separating power/roads businesses from the airport entity), which can genuinely distort year-over-year financials, unlike a typical single-business industrial company",
    ],

    "moat_factors": [
        {"factor": "Regulatory / Concession Scarcity", "description": "Typically only one designated operator per metro airport under a decades-long concession — a structural, government-granted monopoly at that specific location"},
        {"factor": "Scale at Flagship Metro Airports",  "description": "High passenger volume at hub airports (e.g. Delhi, Hyderabad) drives both aeronautical and non-aeronautical revenue per available capacity"},
        {"factor": "Non-Aeronautical Revenue Diversification", "description": "Retail, duty-free, cargo, and real-estate monetisation of airport land reduce dependence on regulator-set aeronautical tariffs alone"},
        {"factor": "Long Concession Tenure",            "description": "30+ year BOT-style concession agreements provide long-duration visibility on the right to operate, unlike a business that must re-win contracts periodically"},
    ],

    "bull_case": [
        "India's air-travel penetration remains low relative to its population and income growth — a long structural runway for passenger traffic",
        "Non-aeronautical revenue mix shift (retail, duty-free, real-estate monetisation of airport land) improving margins as it scales faster than regulator-capped aeronautical tariffs",
        "Tariff order resets allowing aeronautical yield growth once a new control period is approved",
        "New terminal/runway capacity monetising as recently-added infrastructure ramps toward its designed passenger volume",
        "International traffic and hub-connectivity growth adding a higher-yield passenger mix versus purely domestic traffic",
    ],

    "bear_case": [
        "An adverse AERA tariff order compressing aeronautical revenue per passenger for the new control period",
        "Airline capacity cuts or financial distress at a key airline operating from the airport reducing passenger volumes outside the operator's control",
        "High leverage from concession capex limiting financial flexibility, particularly during a demand shock",
        "Slower-than-planned non-aeronautical monetisation (retail/duty-free footfall conversion, real-estate development timelines)",
        "Concession-renewal or revenue-share renegotiation risk with the airport authority or state government",
        "Corporate restructuring or group-level related-party transactions (e.g. with affiliated power/roads entities) affecting reported financials",
    ],

    "red_flags": [
        {"condition": "de_ratio > 4",               "severity": "high",   "message": "D/E > 4x — high even accounting for the sector's project-finance/concession-capex-heavy balance sheets; check debt maturity profile and refinancing risk"},
        {"condition": "de_ratio > 2.5",              "severity": "medium", "message": "D/E > 2.5x — elevated, typical during an active capacity-expansion phase; monitor against the capex cycle stage"},
        {"condition": "revenue_growth < 0",          "severity": "high",   "message": "Negative revenue growth — falling passenger traffic or aeronautical yield"},
        {"condition": "ebitda_margin < 20",          "severity": "medium", "message": "EBITDA margin < 20% — thin for an airport operator; check whether a tariff order or traffic shock is compressing margins"},
    ],

    "valuation": {
        "primary":   ["EV/EBITDA", "DCF (concession-cash-flow based)"],
        "secondary": ["EV/Passenger", "P/B"],
        "notes": (
            "Airport concessions are long-duration cash-flow assets, so a DCF or EV/EBITDA view over the "
            "full control-period cycle is more appropriate than a single-year P/E, especially during an "
            "active capex/ramp-up phase when reported earnings understate steady-state economics. EV/"
            "Passenger is a useful cross-check on how the market is pricing capacity versus peers."
        ),
    },

    "llm_context": (
        "This is an AIRPORT INFRASTRUCTURE / OPERATOR company (e.g. GMR Airports Infrastructure, Adani "
        "Airport Holdings) — NOT an airline. It doesn't fly planes; it owns/operates the physical airport "
        "under a long-term regulated concession, earning aeronautical revenue (landing, parking, user "
        "development fees — periodically reset by the regulator, AERA in India) and non-aeronautical "
        "revenue (retail, duty-free, cargo, real-estate/city-side development on airport land). Passenger "
        "traffic is the core demand driver, but don't apply airline-specific framing (load factor, CASK, "
        "fleet, ATF cost exposure) here — that belongs to the airlines module, not this one. "
        "LEVERAGE: D/E here is structurally elevated by project-finance/concession capex (terminal and "
        "runway construction), not by lease accounting the way an airline's is — frame it against the "
        "capex/expansion cycle stage rather than either a flat industrial benchmark or the airline lease "
        "caveat. "
        "EARNINGS SWINGS: unlike an airline, this sector genuinely does undergo real corporate "
        "restructuring — demergers separating non-airport businesses (power, roads) from the airport entity "
        "are a documented pattern in this space — so a large single-year swing is plausibly a real "
        "corporate action here, not just a demand-cycle effect; check for one rather than defaulting to "
        "either explanation."
    ),
}
