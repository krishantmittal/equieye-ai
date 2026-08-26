# modules/sectors/city_gas_distribution.py
"""
City Gas Distribution — Sector Module
======================================
For Indraprastha Gas, Mahanagar Gas, Gujarat Gas and similar CGD entities.

CRITICAL DISTINCTION FROM POWER_UTILITIES: yfinance's literal industry
string ("Utilities - Regulated Gas") contains the substring "utilities -
regulated", which previously matched the power_utilities fallback rule and
applied an electricity-generator framing (plant load factor, fuel-linkage
coal/gas supply agreements, capacity charges) to a business that has
nothing to do with generating power. A CGD company distributes piped
natural gas (PNG) to households/industry and compressed natural gas (CNG)
to vehicles through a local distribution network under an exclusive
geographical-area licence from the regulator (PNGRB in India). The demand
drivers are PNG household/industrial connections and CNG vehicle-
conversion penetration, not electricity demand or generation capacity —
and the moat is an exclusive geographic licence, not a generation asset.
"""

SECTOR_CONFIG: dict = {
    "slug": "city_gas_distribution",
    "display_name": "City Gas Distribution",

    "key_metrics": [
        {"id": "volume_growth",        "label": "Gas Sales Volume Growth (YoY)", "unit": "%", "yf_key": None, "higher_is_better": True},
        {"id": "cng_station_additions", "label": "CNG Station Network Growth",   "unit": "%", "yf_key": None, "higher_is_better": True},
        {"id": "ebitda_margin",        "label": "EBITDA Margin",                 "unit": "%", "yf_key": "ebitdaMargins", "higher_is_better": True},
        {"id": "revenue_growth",       "label": "Revenue Growth (YoY)",          "unit": "%", "yf_key": "revenueGrowth", "higher_is_better": True},
        {"id": "roe",                  "label": "Return on Equity",              "unit": "%", "yf_key": "returnOnEquity", "higher_is_better": True},
        {"id": "de_ratio",             "label": "Debt/Equity",                   "unit": "x", "yf_key": "debtToEquity", "higher_is_better": False},
    ],

    "scoring_rules": [
        {"metric": "revenue_growth", "op": ">", "threshold": 12.0, "points": 20, "max": 20},
        {"metric": "revenue_growth", "op": ">", "threshold": 6.0,  "points": 12, "max": 20},
        {"metric": "ebitda_margin",  "op": ">", "threshold": 20.0, "points": 25, "max": 25},
        {"metric": "ebitda_margin",  "op": ">", "threshold": 14.0, "points": 15, "max": 25},
        {"metric": "roe",            "op": ">", "threshold": 18.0, "points": 20, "max": 20},
        {"metric": "roe",            "op": ">", "threshold": 12.0, "points": 12, "max": 20},
        {"metric": "de_ratio",       "op": "<", "threshold": 0.5,  "points": 15, "max": 15},
    ],
    "score_max": 100,

    "risk_factors": [
        "Domestic natural-gas allocation policy and APM (administered price mechanism) gas pricing changes directly affect input cost and margin",
        "Competition from electric-vehicle adoption structurally displacing CNG demand in the vehicle segment over the long run",
        "Geographic-area licence renewal and marketing/tariff exclusivity terms are set by the regulator (PNGRB) and can change",
        "Industrial PNG demand is tied to the local industrial cycle in the licensed geography, concentrating risk in that region",
        "Gas-price pass-through lag — a spike in spot/imported LNG costs compresses margin until tariffs are revised",
    ],

    "moat_factors": [
        {"factor": "Exclusive Geographic Licence", "description": "PNGRB grants marketing and infrastructure exclusivity for PNG/CNG in a specific geographical area for a fixed period — a regulatory monopoly at that location with no direct competitor"},
        {"factor": "Built-Out Distribution Network", "description": "The underground pipeline network and CNG station footprint built over years represent a capital and regulatory barrier that a new entrant cannot quickly replicate even after exclusivity ends"},
        {"factor": "First-Mover Household Connections", "description": "Once a household is connected to piped gas, switching away has high friction, creating a sticky, annuity-like revenue base"},
        {"factor": "Structural Cost Advantage vs Alternatives", "description": "PNG/CNG is typically priced below LPG/petrol/diesel on a cost-per-unit-energy basis, giving a durable demand pull independent of the operator's own actions"},
    ],

    "bull_case": [
        "Rising CNG vehicle penetration (especially commercial fleets and government mandates in Indian cities) driving volume growth",
        "Industrial PNG conversion from costlier alternative fuels as environmental regulation tightens",
        "New geographic-area licence wins expanding the addressable market beyond the current exclusive zones",
        "Government push toward gas as a 'transition fuel' supporting policy tailwinds for allocation and pricing",
    ],

    "bear_case": [
        "Long-term EV adoption structurally eroding CNG demand in passenger and even commercial vehicles",
        "An adverse domestic-gas allocation or pricing policy change compressing input-cost economics",
        "Regional industrial slowdown in the company's specific licensed geography reducing PNG offtake",
        "Loss of exclusivity or unfavourable terms upon licence renewal in a mature geography",
    ],

    "red_flags": [
        {"condition": "ebitda_margin < 12", "severity": "high",   "message": "EBITDA margin < 12% — thin for a CGD business; check for a gas-cost spike not yet passed through"},
        {"condition": "revenue_growth < 0", "severity": "high",   "message": "Negative revenue growth — falling volumes or realisations"},
        {"condition": "de_ratio > 1",       "severity": "medium", "message": "D/E > 1x — elevated for a historically low-leverage, cash-generative CGD business"},
    ],

    "valuation": {
        "primary":   ["P/E", "EV/EBITDA"],
        "secondary": ["P/B", "DCF"],
        "bands": {
            "pe_ratio": {"attractive": (0, 18), "fair": (18, 28), "expensive": (28, 999)},
        },
        "notes": (
            "CGD companies have historically traded as steady, regulated-utility-like compounders with "
            "annuity-style cash flows — but the long-term EV-adoption overhang on CNG demand should temper "
            "how much of a growth premium is appropriate versus a pure regulated-utility multiple."
        ),
    },

    "llm_context": (
        "This is a CITY GAS DISTRIBUTION (CGD) company (e.g. Indraprastha Gas, Mahanagar Gas, Gujarat Gas) "
        "— NOT a power/electricity utility, even though yfinance's industry tag ('Utilities - Regulated "
        "Gas') contains the substring 'utilities - regulated'. It distributes piped natural gas (PNG) to "
        "households/industry and CNG to vehicles under an exclusive geographic licence from PNGRB — demand "
        "drivers are PNG connections and CNG vehicle penetration, not electricity load or generation "
        "capacity. Do NOT apply plant-load-factor, fuel-linkage, or generation-capacity framing here. The "
        "single most important long-term risk specific to this sector is EV adoption structurally displacing "
        "CNG demand — factor this into the bear case even when near-term volume growth looks healthy."
    ),
}
