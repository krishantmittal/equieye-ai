# modules/health_score.py
"""
Financial Health Score — Sector-Specific Weighted Scoring
===========================================================
Public API consumed by app.py (signature unchanged):

    compute_health_score(
        pe=None, pb=None, roe_raw=None, de_raw=None,
        profit_margin_raw=None, revenue_cagr=None, profit_cagr=None,
        current_ratio=None, sector="", industry="",
        name="", description="",
    ) -> dict

Returns:
    {
        "score": float (0-10),
        "explanation": str,
        "color": str,
        "sub_scores": dict[pillar_name -> float|None],
        "sector_slug": str,
        "sector_display_name": str,
    }

Each sector has its own pillar weights and pillar definitions.
Pillars map to whichever metrics are available from yfinance.
Banks NEVER use D/E, EBITDA Margin, or FCF.
Loss-making companies are NOT penalised on valuation pillar.
"""

from __future__ import annotations
from modules.sectors import get_sector_config
from modules.sectors.conglomerates import (
    get_blended_ev_ebitda_band, get_blended_pb_band, get_blended_pillar_weights, get_blended_de_divisor,
)
from modules.sector_analysis import classify_sector

# ── P/E bands (unchanged, used by Compare Stocks valuation badge) ──────────

_GENERIC_PE_BANDS = {
    "Technology": (20, 50), "Financial Services": (12, 30),
    "Healthcare": (25, 60), "Consumer Cyclical": (20, 45),
    "Consumer Defensive": (25, 50), "Energy": (10, 25),
    "Utilities": (12, 25), "Industrials": (18, 40),
    "Basic Materials": (12, 28), "Real Estate": (20, 40),
    "Communication Services": (18, 45),
}

def get_pe_bands(sector: str, industry: str, slug: str | None = None):
    # If the caller already resolved a sector slug (using name/description,
    # which this function alone doesn't receive), use it directly instead of
    # re-deriving from just sector/industry — re-deriving without name/
    # description silently mis-detects sectors like "chemicals" (whose
    # yfinance sector/industry strings, e.g. "Basic Materials" /
    # "Agricultural Inputs", don't contain any of the sector's own keywords)
    # and falls back to a much looser generic industry band.
    resolved_slug = slug or classify_sector(sector, industry)
    cfg = get_sector_config(resolved_slug)
    bands = cfg.get("valuation", {}).get("bands", {})
    pe_band = bands.get("pe_ratio")
    if pe_band:
        return (pe_band["attractive"][1], pe_band["fair"][1])
    return _GENERIC_PE_BANDS.get(sector, (15, 35))


# ══════════════════════════════════════════════════════════════════════════════
# SECTOR WEIGHT REGISTRY
# Each entry: pillar_name -> weight (0-100, must sum to 100)
# Pillar names also appear in UI breakdown bars.
# ══════════════════════════════════════════════════════════════════════════════

_SECTOR_WEIGHTS: dict[str, dict[str, int]] = {
    "banking": {
        "Asset Quality":       30,
        "Profitability":       25,
        "Capital Adequacy":    20,
        "Growth":              15,
        "Valuation":           10,
    },
    "nbfc": {
        "Asset Quality":       25,
        "Profitability":       25,
        "Capital Adequacy":    15,
        "Growth":              20,
        "Valuation":           15,
    },
    "insurance": {
        "Embedded Value":      30,
        "Profitability":       20,
        "Capital Adequacy":    20,
        "Growth":              20,
        "Valuation":           10,
    },
    "fmcg": {
        "Profitability":       35,
        "Growth":              10,
        "Balance Sheet":       20,
        "Valuation":           15,
        "Cash Generation":     20,
    },
    "it_services": {
        "Profitability":       30,
        "Growth":              25,
        "Cash Generation":     20,
        "Balance Sheet":       15,
        "Valuation":           10,
    },
    "fintech": {
        "Growth":              30,
        "Profitability":       15,
        "Cash Generation":     20,
        "Balance Sheet":       20,
        "Valuation":           15,
    },
    "pharma": {
        "Profitability":       25,
        "Growth":              20,
        "Balance Sheet":       20,
        "Cash Generation":     20,
        "Valuation":           15,
    },
    "auto_ev": {
        "Growth":              25,
        "Profitability":       25,
        "Balance Sheet":       20,
        "Cash Generation":     15,
        "Valuation":           15,
    },
    "renewable_energy": {
        "Growth":              25,
        "Balance Sheet":       25,
        "Cash Generation":     20,
        "Execution":           15,
        "Valuation":           15,
    },
    "power_utilities": {
        "Cash Generation":     30,
        "Balance Sheet":       25,
        "Growth":              15,
        "Profitability":       15,
        "Valuation":           15,
    },
    "telecom": {
        "Cash Generation":     25,
        "Balance Sheet":       25,
        "Growth":              20,
        "Profitability":       15,
        "Valuation":           15,
    },
    "real_estate": {
        "Balance Sheet":       30,
        "Cash Generation":     25,
        "Growth":              20,
        "Profitability":       15,
        "Valuation":           10,
    },
    "metals_mining": {
        "Profitability":       30,
        "Balance Sheet":       25,
        "Cash Generation":     20,
        "Valuation":           15,
        "Growth":              10,
    },
    "generic": {
        "Profitability":       25,
        "Growth":              25,
        "Balance Sheet":       25,
        "Valuation":           25,
    },
}

# Add aliases for sectors not in the original spec — map to closest model
_SECTOR_WEIGHTS["chemicals"]         = {"Profitability": 30, "Growth": 25, "Balance Sheet": 20, "Cash Generation": 15, "Valuation": 10}
_SECTOR_WEIGHTS["cement"]            = {"Profitability": 30, "Cash Generation": 25, "Balance Sheet": 20, "Growth": 15, "Valuation": 10}
_SECTOR_WEIGHTS["consumer_durables"] = {"Growth": 25, "Profitability": 25, "Balance Sheet": 20, "Cash Generation": 15, "Valuation": 15}
_SECTOR_WEIGHTS["logistics"]         = {"Growth": 25, "Cash Generation": 25, "Profitability": 20, "Balance Sheet": 20, "Valuation": 10}
# Airlines: Balance Sheet weighted down (raw D/E is lease-inflated and
# less discriminating — see _SECTOR_DE_DIVISOR_OVERRIDES above) in favour
# of Cash Generation and Profitability, which matter more for judging
# whether a lease-heavy, cyclical airline can actually service its
# obligations through a downturn.
_SECTOR_WEIGHTS["airlines"]          = {"Profitability": 25, "Cash Generation": 25, "Growth": 20, "Balance Sheet": 15, "Valuation": 15}
# Airport infra: similar logic to airlines (leverage is structural, from
# concession capex rather than lease accounting) — weight down Balance
# Sheet, weight up Growth (passenger traffic ramp) and Cash Generation.
_SECTOR_WEIGHTS["airport_infra"]     = {"Growth": 25, "Cash Generation": 25, "Profitability": 20, "Balance Sheet": 15, "Valuation": 15}
_SECTOR_WEIGHTS["oil_gas"]           = {"Cash Generation": 30, "Profitability": 25, "Balance Sheet": 20, "Growth": 15, "Valuation": 10}
_SECTOR_WEIGHTS["capital_goods"]     = {"Execution": 25, "Growth": 25, "Profitability": 20, "Balance Sheet": 20, "Valuation": 10}  # kept for backward compat — detector.py no longer emits this slug
# Capital goods sub-sectors (split from the old flat "capital_goods" — see
# each module's docstring in modules/sectors/ for the reasoning). The old
# flat weighting applied an EPC-style Execution-heavy profile to every
# capital-goods company, which fits an EPC contractor well but misjudges
# an automation/software major (should be Profitability-led, like an
# asset-light tech business) or a heavy-manufacturing PSU-order name
# (capacity utilization matters as much as pure execution).
_SECTOR_WEIGHTS["industrial_automation"] = {"Profitability": 30, "Growth": 25, "Cash Generation": 20, "Balance Sheet": 15, "Valuation": 10}
_SECTOR_WEIGHTS["epc_engineering"]       = {"Execution": 25, "Growth": 25, "Profitability": 20, "Balance Sheet": 20, "Valuation": 10}
_SECTOR_WEIGHTS["electrical_equipment"]  = {"Growth": 25, "Profitability": 25, "Balance Sheet": 20, "Cash Generation": 15, "Valuation": 15}
_SECTOR_WEIGHTS["heavy_engineering"]     = {"Execution": 25, "Profitability": 25, "Balance Sheet": 20, "Growth": 20, "Valuation": 10}
# Defense & aerospace: order-book/execution matters (mirrors EPC), but this
# sector's balance sheets are typically much cleaner (PSU-dominated,
# government advance payments) than a private EPC contractor's, so Balance
# Sheet gets less weight than epc_engineering and Profitability more —
# margins on sanctioned government programs are usually strong and a better
# differentiator here than leverage discipline.
_SECTOR_WEIGHTS["defense_aerospace"]     = {"Execution": 25, "Profitability": 25, "Growth": 20, "Balance Sheet": 15, "Valuation": 15}
_SECTOR_WEIGHTS["consumer_internet"] = {"Growth": 35, "Profitability": 15, "Cash Generation": 20, "Balance Sheet": 15, "Valuation": 15}

# Pharma sub-sectors (split from the old flat "pharma" — see
# modules/sectors/pharma_*.py docstrings). classify_sector() no longer ever
# emits the bare "pharma" slug, so without these explicit entries every one
# of these companies was silently falling back to the flat 25/25/25/25
# "generic" profile (dropping the Cash Generation pillar entirely) instead
# of a pharma-appropriate weighting.
# Generics/API/CDMO: same profile as the original flat pharma model —
# margin/growth-driven, R&D-light relative to specialty/biotech, balance
# sheet and cash generation matter given capex + regulatory capex cycles.
_SECTOR_WEIGHTS["pharma_generics"]   = {"Profitability": 25, "Growth": 20, "Balance Sheet": 20, "Cash Generation": 20, "Valuation": 15}
_SECTOR_WEIGHTS["pharma_api"]        = {"Profitability": 25, "Growth": 20, "Balance Sheet": 20, "Cash Generation": 20, "Valuation": 15}
_SECTOR_WEIGHTS["pharma_cdmo"]       = {"Profitability": 25, "Growth": 20, "Balance Sheet": 20, "Cash Generation": 20, "Valuation": 15}
# Specialty/biotech: binary clinical/regulatory pipeline outcomes make
# Growth the primary swing factor (pipeline optionality), at the expense of
# Balance Sheet/Cash Generation, which matter less than for a cash-generative
# generics business.
_SECTOR_WEIGHTS["pharma_specialty"]  = {"Growth": 30, "Profitability": 20, "Balance Sheet": 15, "Cash Generation": 15, "Valuation": 20}
_SECTOR_WEIGHTS["biotech"]           = {"Growth": 30, "Profitability": 20, "Balance Sheet": 15, "Cash Generation": 15, "Valuation": 20}
# Diagnostics: asset-light, high-margin, non-discretionary demand — mirrors
# it_services' profile shape for the same reason (asset-light services model).
_SECTOR_WEIGHTS["diagnostics"]       = {"Profitability": 30, "Growth": 25, "Cash Generation": 20, "Balance Sheet": 15, "Valuation": 10}
# Hospitals: capex-heavy with long occupancy-ramp gestation, so Balance
# Sheet matters more than for asset-light healthcare peers, but demand is
# stable rather than cyclical.
_SECTOR_WEIGHTS["hospitals"]         = {"Profitability": 25, "Balance Sheet": 25, "Growth": 20, "Cash Generation": 20, "Valuation": 10}
# Engineering R&D (split from it_services): same asset-light delivery model
# as capital_goods' Execution-inclusive profile, since delivery execution
# against client engineering programs is as important as growth here.
_SECTOR_WEIGHTS["engineering_rd"]    = {"Execution": 25, "Growth": 25, "Profitability": 20, "Balance Sheet": 20, "Valuation": 10}
# Media/broadcasting: ad-revenue cyclicality makes Growth and Profitability
# (EBITDA margin) the primary swing factors; Cash Generation matters because
# content-cost amortisation distorts reported earnings; Balance Sheet is
# weighted like other content/rights-heavy models (not asset-light like IT).
_SECTOR_WEIGHTS["media"]             = {"Profitability": 25, "Growth": 25, "Cash Generation": 20, "Balance Sheet": 20, "Valuation": 10}

# New sectors added to fix misclassification/generic-fallback gaps (see
# modules/sectors/detector.py and each sector module's docstring).
# Paints: branded, dealer-network consumer good — mirrors consumer_durables/
# electrical_equipment's shape (Growth + Profitability led) rather than
# chemicals' commodity through-cycle profile.
_SECTOR_WEIGHTS["paints"] = {"Profitability": 30, "Growth": 20, "Balance Sheet": 20, "Cash Generation": 15, "Valuation": 15}
# Port infra: same reasoning as airport_infra — leverage is structural
# concession capex, so Balance Sheet weighted down in favour of Growth
# (cargo volume ramp) and Cash Generation.
_SECTOR_WEIGHTS["port_infra"] = {"Growth": 25, "Cash Generation": 25, "Profitability": 20, "Balance Sheet": 15, "Valuation": 15}
# City gas distribution: regulated, cash-generative, annuity-like utility
# economics — similar shape to pharma_generics/hospitals rather than a
# growth story.
_SECTOR_WEIGHTS["city_gas_distribution"] = {"Profitability": 25, "Growth": 20, "Balance Sheet": 20, "Cash Generation": 20, "Valuation": 15}
# Spirits & tobacco: high-ROE, premiumisation-led margin story rather than
# volume growth (often regulation-capped) — Profitability weighted highest.
_SECTOR_WEIGHTS["spirits_tobacco"] = {"Profitability": 30, "Growth": 15, "Balance Sheet": 20, "Cash Generation": 20, "Valuation": 15}
# Luxury goods & jewellery retail: store-network/same-store-sales growth
# story with real pricing power — Valuation weighted up given persistent
# growth-premium multiples in this space.
_SECTOR_WEIGHTS["luxury_goods_jewelry"] = {"Growth": 25, "Valuation": 20, "Profitability": 20, "Balance Sheet": 20, "Cash Generation": 15}
# Asset management (AMC): asset-light, fee-based, extremely high-margin —
# Balance Sheet barely matters (little capex/debt), Profitability and
# Growth (AUM growth) dominate.
_SECTOR_WEIGHTS["asset_management"] = {"Profitability": 35, "Growth": 25, "Cash Generation": 15, "Valuation": 15, "Balance Sheet": 10}
# Hospitality/hotels: high-operating-leverage, RevPAR-driven — similar
# shape to airlines/airport_infra (Balance Sheet weighted down given
# owned-asset-heavy but improving asset-light mix).
_SECTOR_WEIGHTS["hospitality"] = {"Profitability": 25, "Growth": 20, "Cash Generation": 20, "Balance Sheet": 20, "Valuation": 15}
# Market infrastructure (exchanges/depositories): asset-light, near-
# monopoly fee-utility — same shape as asset_management.
_SECTOR_WEIGHTS["market_infrastructure"] = {"Profitability": 35, "Growth": 25, "Cash Generation": 15, "Valuation": 15, "Balance Sheet": 10}
# Capital markets (brokerage): client/volume-growth-driven with real
# balance-sheet exposure via the MTF book, unlike the exchange/AMC model.
_SECTOR_WEIGHTS["capital_markets"] = {"Growth": 25, "Profitability": 25, "Cash Generation": 20, "Balance Sheet": 15, "Valuation": 15}
# Textiles & apparel manufacturing: spans commodity-yarn to branded-apparel
# — a balanced profile similar to consumer_durables/electrical_equipment.
_SECTOR_WEIGHTS["textiles_apparel"] = {"Profitability": 25, "Balance Sheet": 20, "Cash Generation": 20, "Growth": 20, "Valuation": 15}
# QSR restaurants: same-store-sales/network-expansion growth story, lease-
# heavy — Growth weighted highest, similar shape to consumer_internet but
# less extreme given QSR's more mature unit economics.
_SECTOR_WEIGHTS["qsr_restaurants"] = {"Growth": 30, "Profitability": 20, "Cash Generation": 20, "Balance Sheet": 15, "Valuation": 15}
# Apparel/department store retail: same reasoning as qsr_restaurants —
# same-store-sales/network-expansion driven.
_SECTOR_WEIGHTS["retail_apparel"] = {"Growth": 30, "Profitability": 20, "Cash Generation": 20, "Balance Sheet": 15, "Valuation": 15}
# Tyre manufacturing: auto ancillary with real commodity (rubber) input-
# cost exposure — balanced profile similar to textiles_apparel/chemicals.
_SECTOR_WEIGHTS["tyre_manufacturing"] = {"Profitability": 25, "Balance Sheet": 20, "Cash Generation": 20, "Growth": 20, "Valuation": 15}

# Sectors where the Balance Sheet pillar tolerates higher leverage (D/E
# scored with a gentler divisor) because the business model is structurally
# capital-intensive/infrastructure-heavy. Named here (rather than left as an
# inline tuple inside _score_balance_sheet) so modules/sectors/conglomerates.py
# can reuse the exact same membership test when blending a multi-segment
# company's leverage tolerance — passed in as a parameter to avoid a
# circular import (conglomerates.py is imported by this module).
_LENIENT_LEVERAGE_SECTORS = ("renewable_energy", "power_utilities", "telecom", "real_estate")

# Per-sector D/E divisor overrides — for balance sheets where reported
# leverage is structurally inflated by an accounting mechanism, not
# operating risk, and even the gentler _LENIENT_LEVERAGE_SECTORS divisor
# (2.0) would still floor the score at 0. Airlines: Ind AS 116 / IFRS 16
# requires capitalising leased aircraft as right-of-use assets with a
# matching lease liability, which mechanically inflates D/E for any
# lease-heavy carrier — the Indian norm — to routinely 4-9x+ even for a
# healthy, well-run airline. A flat 4.0x (or even the lenient 2.0x)
# divisor would score every major Indian carrier 0/10 on Balance Sheet
# regardless of how well or poorly levered they actually are relative to
# each other, which isn't a meaningful signal. 0.6 keeps the pillar
# discriminating within the sector's own (higher) normal range instead.
_SECTOR_DE_DIVISOR_OVERRIDES = {
    "airlines": 0.6,
    # Airport operators run genuinely elevated D/E from project-finance/
    # concession capex (terminal & runway construction) — real, but a less
    # extreme accounting effect than an airline's Ind AS 116 lease
    # capitalisation, so a gentler override than airlines' but still
    # meaningfully more lenient than the flat 4.0x default.
    "airport_infra": 0.9,
}


# ══════════════════════════════════════════════════════════════════════════════
# PILLAR SCORERS
# Each pillar scorer receives the available metrics dict and returns 0-10.
# Returns None when no relevant data exists for that pillar.
# ══════════════════════════════════════════════════════════════════════════════

def _score_profitability(m: dict, slug: str) -> float | None:
    scores = []
    roe = m.get("roe")
    pm  = m.get("profit_margin")
    roa = m.get("roa")

    if roe is not None:
        # Banking/NBFC: higher ROE threshold (15% = good)
        if slug in ("banking", "nbfc"):
            scores.append(min(10, max(0, roe / 1.8)))
        else:
            scores.append(min(10, max(0, roe / 3.0)))
    if pm is not None:
        if slug in ("banking", "nbfc", "insurance"):
            # Net margin for financials is structurally lower — use roa instead
            pass
        elif slug in ("fmcg", "power_utilities", "metals_mining"):
            # Same "mature, structurally lower-margin" tier already used for
            # growth scoring below. A flat /2.5 (25% margin = perfect) is a
            # software/pharma-tier bar — Britannia at 13.2% net margin (genuinely
            # excellent for a bakery/staples FMCG, on par with category leaders)
            # was scoring only ~5.3/10 against it. /1.8 (18% = perfect) reflects
            # the real ceiling for this sector — HUL/Nestle-tier margins, not an
            # arbitrary generic number.
            scores.append(min(10, max(0, pm / 1.8)))
        else:
            scores.append(min(10, max(0, pm / 2.5)))
    if roa is not None and slug in ("banking", "nbfc"):
        # ROA is the key profitability metric for banks (>1.5% = excellent).
        # yfinance's returnOnAssets is always a decimal fraction (e.g. 0.021
        # for 2.1% ROA) — convert to percentage first, same as roe/profit_margin
        # in _build_metrics_dict. Without this, a genuinely excellent ~2% ROA
        # was read as "0.02%" against the 0.18 threshold, scoring near zero
        # and dragging a strong bank's Profitability pillar down by half.
        scores.append(min(10, max(0, (roa * 100) / 0.18)))

    return round(sum(scores) / len(scores), 1) if scores else None


def _growth_divisor(slug: str) -> float:
    """
    Shared revenue/profit-growth divisor lookup, tiered by sector maturity —
    used by both _score_growth (the Growth pillar) and _score_execution
    (which uses revenue growth as a fallback proxy when no direct execution
    metric like capacity utilisation is available). Keeping both pillars on
    the same divisor per sector avoids an illogical situation where the
    Execution proxy demands a STEEPER growth bar than the Growth pillar
    itself for an identical number — which is what happened before this was
    unified: Execution's old flat /3.0 (30% for a perfect score) was steeper
    than every tier below, including the default /2.5, so a mature,
    steady-growth business (e.g. a defense PSU on ~8% revenue growth, which
    is genuinely healthy for large multi-year government-sanctioned
    programs) scored respectably on Growth but was then dragged down again
    by Execution scoring the *same* growth number as if it were weak.
    """
    if slug in ("fintech", "consumer_internet"):
        return 4.0   # 40% = 10/10 — genuine high-growth sectors
    if slug in ("fmcg", "power_utilities", "metals_mining"):
        return 0.9   # 9% = 10/10 — mature, structurally lower-growth sectors
    if slug in ("it_services", "engineering_rd", "defense_aerospace",
                "epc_engineering", "heavy_engineering", "capital_goods"):
        # 10% = 10/10 — mature industrial/services businesses where high-
        # single-digit-to-low-double-digit growth is the normal, healthy
        # case, not a growth concern. defense_aerospace/epc_engineering/
        # heavy_engineering/capital_goods added here for the same reason as
        # it_services/engineering_rd above: these are large, order-book-
        # driven industrial businesses, not high-growth compounders — a
        # steady ~8-10% is a good outcome, not a weak one.
        return 1.0
    return 2.5       # default — 25% = 10/10


def _score_growth(m: dict, slug: str) -> float | None:
    scores = []
    rev_g = m.get("revenue_growth")
    prof_g = m.get("profit_growth")
    divisor = _growth_divisor(slug)

    if rev_g is not None:
        scores.append(min(10, max(0, rev_g / divisor)))
    if prof_g is not None:
        # Clamp extreme turnaround values
        clamped = min(prof_g, 100)
        # Mirror the same sector tiers used for revenue growth above — a flat
        # /3.0 for every sector meant FMCG needed 30% profit CAGR for full
        # marks, a far steeper bar than the 12% CAGR that earns full marks
        # on the revenue side of the same pillar for the same sector.
        scores.append(min(10, max(0, clamped / divisor)))

    return round(sum(scores) / len(scores), 1) if scores else None


def _score_balance_sheet(m: dict, slug: str, de_divisor: float | None = None) -> float | None:
    scores = []
    de    = m.get("de_ratio")
    cr    = m.get("current_ratio")

    if de is not None and slug not in ("banking", "nbfc", "insurance"):
        if de_divisor is not None:
            # Blended divisor from a conglomerate registry match — see
            # modules/sectors/conglomerates.py get_blended_de_divisor().
            scores.append(min(10, max(0, 10 - de * de_divisor)))
        elif slug in _SECTOR_DE_DIVISOR_OVERRIDES:
            scores.append(min(10, max(0, 10 - de * _SECTOR_DE_DIVISOR_OVERRIDES[slug])))
        elif slug in _LENIENT_LEVERAGE_SECTORS:
            # Capital-intensive sectors tolerate higher D/E
            scores.append(min(10, max(0, 10 - de * 2.0)))
        else:
            scores.append(min(10, max(0, 10 - de * 4.0)))
    if cr is not None:
        scores.append(min(10, max(0, cr * 4.0)))

    return round(sum(scores) / len(scores), 1) if scores else None


def _score_valuation(m: dict, slug: str, sector: str, industry: str, name: str = "") -> float | None:
    pe = m.get("pe_ratio")
    pb = m.get("pb_ratio")
    ev_ebitda = m.get("ev_ebitda")
    price_to_sales = m.get("price_to_sales")

    cfg = get_sector_config(slug)
    bands = cfg.get("valuation", {}).get("bands", {})

    def _score_from_band(value, low, high):
        span = high - low if high != low else low or 1
        score = 10 - ((value - low) / span) * 10
        if score < 0:
            # Previously clipped straight to 0 the instant a value crossed
            # the "expensive" boundary — meaning e.g. an EV/EBITDA of 11x
            # and 40x scored identically (both hard 0/10), losing all
            # differentiation between "somewhat expensive" and "wildly
            # expensive". Found when Reliance Industries' real EV/EBITDA
            # (~12-14x, well-sourced) hit the same flat 0 a dramatically
            # overvalued pure-play would get. This adds a soft tail —
            # decaying from 1 down to 0 over the next two band-widths —
            # so nearby-expensive and extremely-expensive still differ.
            # Does NOT change any score for values inside the sector's own
            # attractive/fair/expensive band (only triggers once score<0).
            score = max(0, 1 + score / 20)
        return round(min(10, max(0, score)), 1)

    def _band_score(value, band_key):
        band = bands.get(band_key)
        if not band:
            return None
        return _score_from_band(value, band["attractive"][1], band["fair"][1])

    # Diversified conglomerates (Reliance etc.) — before falling into the
    # normal single-sector EV/EBITDA path, check whether this company is in
    # the curated conglomerate registry. If so, score against a BLENDED band
    # (each business segment's own peer band, weighted by EBITDA share)
    # instead of judging the whole company against just one segment's sector
    # (e.g. Reliance's Jio/Retail segments legitimately trade richer than
    # pure oil & gas, so the plain oil_gas band alone understates it). See
    # modules/sectors/conglomerates.py for the registry and its limitations.
    if ev_ebitda is not None and ev_ebitda > 0:
        blended = get_blended_ev_ebitda_band(name)
        if blended:
            low, high = blended
            return _score_from_band(ev_ebitda, low, high)

    # Banks/NBFCs/Insurance: use P/B not P/E, scored against each sector's
    # own price_to_book bands (not a hardcoded formula) so config changes —
    # e.g. widening the band to reflect a quality bank's structural premium
    # — actually take effect instead of being silently ignored.
    if slug in ("banking", "nbfc", "insurance"):
        if pb is not None and pb > 0:
            # Financial-services conglomerates (e.g. Aditya Birla Capital,
            # spanning NBFC + Housing Finance + Life Insurance) - check the
            # P/B blend registry first, same pattern as the EV/EBITDA check
            # above but on price-to-book. See get_blended_pb_band() and the
            # "aditya birla capital" entry in conglomerates.py for the
            # registry, sourcing, and what's deliberately excluded (AMC,
            # Health Insurance - equity-accounted, not consolidated).
            blended_pb = get_blended_pb_band(name)
            if blended_pb:
                low, high = blended_pb
                return _score_from_band(pb, low, high)
            s = _band_score(pb, "price_to_book")
            if s is not None:
                return s
            # Fallback if a sector config has no price_to_book band defined
            return round(min(10, max(0, 10 - (pb - 0.5) * 3.5)), 1)
        return None

    # Capital-intensive / cash-flow-driven sectors that declare EV/EBITDA as
    # their valuation framework (metals_mining, power_utilities, telecom,
    # renewable_energy) — score on EV/EBITDA when we actually have it.
    if "ev_ebitda" in bands and ev_ebitda is not None and ev_ebitda > 0:
        s = _band_score(ev_ebitda, "ev_ebitda")
        if s is not None:
            return s

    # Pre-profit / high-growth sectors that declare Price/Sales as their
    # valuation framework (fintech) — score on P/S when we have it.
    if "price_to_sales" in bands and price_to_sales is not None and price_to_sales > 0:
        s = _band_score(price_to_sales, "price_to_sales")
        if s is not None:
            return s

    # Loss-making or no P/E — don't penalise, return neutral
    if pe is None or pe <= 0 or pe > 200:
        # For high-growth pre-profit companies: neutral 5.0
        if slug in ("fintech", "consumer_internet", "auto_ev"):
            return 5.0
        return None

    low, high = get_pe_bands(sector, industry, slug=slug)
    band = high - low if high != low else 20
    score = 10 - ((pe - low) / band) * 10
    return round(min(10, max(0, score)), 1)


def _score_cash_generation(m: dict, slug: str) -> float | None:
    fcf = m.get("fcf")
    ocf = m.get("ocf")
    rev = m.get("revenue")

    scores = []
    # FCF yield proxy: if we have FCF and revenue, compute FCF margin
    if fcf is not None and rev is not None and rev > 0:
        fcf_margin = (fcf / rev) * 100
        scores.append(min(10, max(0, fcf_margin / 1.5)))
    elif fcf is not None:
        # Positive FCF = reasonable score, negative = 0-2
        scores.append(7.0 if fcf > 0 else max(0, 2 + fcf / 1e10))
    if ocf is not None:
        scores.append(7.5 if ocf > 0 else 2.0)

    return round(sum(scores) / len(scores), 1) if scores else None


def _score_asset_quality(m: dict) -> float | None:
    """Banking/NBFC only."""
    gnpa = m.get("gross_npa")
    pcr  = m.get("pcr")
    scores = []
    if gnpa is not None:
        # GNPA < 1% = 10; > 8% = 0
        scores.append(min(10, max(0, 10 - gnpa * 1.4)))
    if pcr is not None:
        # PCR > 85% = 10; < 60% = 0
        scores.append(min(10, max(0, (pcr - 55) / 3.5)))
    return round(sum(scores) / len(scores), 1) if scores else None


def _score_capital_adequacy(m: dict, slug: str) -> float | None:
    """Banking/NBFC/Insurance."""
    cet1    = m.get("cet1_ratio")
    car     = m.get("car")
    solvency = m.get("solvency_ratio")
    scores = []
    if cet1 is not None:
        scores.append(min(10, max(0, (cet1 - 8) / 1.2)))
    if car is not None:
        scores.append(min(10, max(0, (car - 10) / 2.0)))
    if solvency is not None:
        scores.append(min(10, max(0, (solvency - 1.0) * 8.0)))
    # If no sector-specific capital data, fall back to current ratio
    cr = m.get("current_ratio")
    if not scores and cr is not None:
        scores.append(min(10, max(0, cr * 3.5)))
    return round(sum(scores) / len(scores), 1) if scores else None


def _score_embedded_value(m: dict) -> float | None:
    """Insurance only."""
    vnb = m.get("vnb_margin")
    ev_g = m.get("embedded_value_growth")
    pers = m.get("persistency_13m")
    scores = []
    if vnb is not None:
        scores.append(min(10, max(0, vnb / 3.0)))
    if ev_g is not None:
        scores.append(min(10, max(0, ev_g / 2.5)))
    if pers is not None:
        scores.append(min(10, max(0, (pers - 60) / 3.0)))
    # Fallback: use ROE if insurance-specific metrics unavailable
    if not scores:
        roe = m.get("roe")
        if roe is not None:
            scores.append(min(10, max(0, roe / 2.0)))
    return round(sum(scores) / len(scores), 1) if scores else None


def _score_execution(m: dict, slug: str) -> float | None:
    """Renewable/Auto-EV/Capital Goods/Power — proxy via capacity utilisation,
    revenue growth, and asset turnover when specific execution metrics absent."""
    cu  = m.get("capacity_util")
    rev_g = m.get("revenue_growth")
    scores = []
    if cu is not None:
        scores.append(min(10, max(0, cu / 10)))
    if rev_g is not None:
        # Execution shows up in revenue delivery. Uses the SAME sector-tiered
        # divisor as the Growth pillar (_growth_divisor) — the old flat /3.0
        # here demanded 30% revenue growth for a perfect score, steeper than
        # even the Growth pillar's own default (25%) and far steeper than the
        # tiers used for mature industrial sectors (10%). That meant a
        # steady, healthy grower (e.g. a defense PSU or EPC contractor on
        # ~8% growth) could score reasonably on Growth but then get
        # penalized again on Execution for the exact same number, as if
        # execution and growth were unrelated questions with different
        # answers for the same company.
        scores.append(min(10, max(0, rev_g / _growth_divisor(slug))))
    # Fallback: balance-sheet proxy (low leverage = more execution flexibility)
    if not scores:
        de = m.get("de_ratio")
        if de is not None:
            scores.append(min(10, max(0, 10 - de * 2.0)))
    return round(sum(scores) / len(scores), 1) if scores else None


# ── Pillar dispatcher ────────────────────────────────────────────────────────

def _compute_pillar(pillar: str, m: dict, slug: str, sector: str, industry: str, name: str = "", de_divisor: float | None = None) -> float | None:
    if pillar == "Profitability":    return _score_profitability(m, slug)
    if pillar == "Growth":           return _score_growth(m, slug)
    if pillar == "Balance Sheet":    return _score_balance_sheet(m, slug, de_divisor=de_divisor)
    if pillar == "Valuation":        return _score_valuation(m, slug, sector, industry, name=name)
    if pillar == "Cash Generation":  return _score_cash_generation(m, slug)
    if pillar == "Asset Quality":    return _score_asset_quality(m)
    if pillar == "Capital Adequacy": return _score_capital_adequacy(m, slug)
    if pillar == "Embedded Value":   return _score_embedded_value(m)
    if pillar == "Execution":        return _score_execution(m, slug)
    return None


# ── Metrics dict builder ─────────────────────────────────────────────────────

def _build_metrics_dict(pe, pb, roe_raw, de_raw, profit_margin_raw,
                         revenue_cagr, profit_cagr, current_ratio) -> dict:
    m: dict = {}
    if pe is not None:
        m["pe_ratio"] = pe
    if pb is not None:
        m["pb_ratio"] = pb
    if roe_raw is not None:
        m["roe"] = roe_raw * 100  # yfinance returnOnEquity is always a decimal fraction
    if de_raw is not None:
        # yfinance returns debtToEquity in percentage form for NSE stocks —
        # always divide by 100. The old ">5" heuristic wrongly left very
        # small raw values (e.g. ITC's ~3.29, true D/E 0.0329x) unconverted,
        # which the Balance Sheet pillar then read as D/E=3.29x — a company
        # that's nearly debt-free scored as if dangerously over-leveraged.
        m["de_ratio"] = de_raw / 100
    if profit_margin_raw is not None:
        m["profit_margin"] = profit_margin_raw * 100  # yfinance profitMargins is always a decimal fraction
    if revenue_cagr is not None:
        m["revenue_growth"] = revenue_cagr
    if profit_cagr is not None:
        m["profit_growth"] = profit_cagr
    if current_ratio is not None:
        m["current_ratio"] = current_ratio
    return m


# ── Main scorer ──────────────────────────────────────────────────────────────

def compute_health_score(
    pe=None, pb=None, roe_raw=None, de_raw=None,
    profit_margin_raw=None, revenue_cagr=None, profit_cagr=None,
    current_ratio=None, sector: str = "", industry: str = "",
    name: str = "", description: str = "",
    extra_metrics: dict | None = None,
) -> dict:
    slug = classify_sector(sector, industry, name, description)
    cfg  = get_sector_config(slug)

    m = _build_metrics_dict(pe, pb, roe_raw, de_raw, profit_margin_raw,
                             revenue_cagr, profit_cagr, current_ratio)
    if extra_metrics:
        m.update({k: v for k, v in extra_metrics.items() if v is not None})

    # Get sector weight map — fall back to generic if slug not explicitly mapped
    weights = _SECTOR_WEIGHTS.get(slug) or _SECTOR_WEIGHTS["generic"]

    # Diversified conglomerates (Reliance etc.) — use a blended weight
    # profile (each segment's own weight map, weighted by EBITDA share)
    # instead of just the single primary sector's profile. Falls straight
    # through to the line above unchanged for every non-registered company.
    # See modules/sectors/conglomerates.py for the registry + limitations.
    _blended_weights = get_blended_pillar_weights(name, _SECTOR_WEIGHTS)
    if _blended_weights:
        weights = _blended_weights
    _de_divisor = get_blended_de_divisor(name, _LENIENT_LEVERAGE_SECTORS)

    # Score each pillar
    pillar_scores: dict[str, float | None] = {}
    for pillar in weights:
        pillar_scores[pillar] = _compute_pillar(pillar, m, slug, sector, industry, name=name, de_divisor=_de_divisor)

    # Some pillars (Embedded Value, Execution) require specialized metrics
    # that yfinance never actually supplies (VNB margin, persistency,
    # capacity utilisation, etc.) — see _score_embedded_value /
    # _score_execution. When those keys are absent, the pillar still returns
    # a score via a generic fallback (ROE for Embedded Value, revenue growth
    # or D/E for Execution) rather than the real specialized metric. Flag
    # this so the UI can disclose "this number is a stand-in", the same way
    # it discloses genuinely missing pillars — otherwise a relabeled generic
    # metric looks identical to real sector-specific analysis.
    _PROXY_PILLAR_KEYS = {
        "Embedded Value": ("vnb_margin", "embedded_value_growth", "persistency_13m"),
        "Execution": ("capacity_util",),
    }
    proxy_pillars: list[str] = []
    proxy_explanations: dict[str, str] = {}
    for pillar, specialized_keys in _PROXY_PILLAR_KEYS.items():
        if pillar in pillar_scores and pillar_scores[pillar] is not None:
            if not any(m.get(k) is not None for k in specialized_keys):
                proxy_pillars.append(pillar)
                if pillar == "Embedded Value":
                    proxy_explanations[pillar] = (
                        "Embedded Value / VNB / persistency data isn't available from the data "
                        "source — this score is a stand-in based on ROE, not true embedded-value analysis."
                    )
                else:
                    proxy_explanations[pillar] = (
                        "Capacity utilisation data isn't available from the data source — this score "
                        "is a stand-in based on revenue growth or leverage, not true execution tracking."
                    )

    # Weighted average over pillars that have data
    total_weight = 0
    weighted_sum = 0.0
    for pillar, w in weights.items():
        s = pillar_scores[pillar]
        if s is not None:
            weighted_sum += s * w
            total_weight += w

    score = round(weighted_sum / total_weight, 1) if total_weight > 0 else None

    color = "#22C55E" if (score or 0) >= 7 else "#F59E0B" if (score or 0) >= 5 else "#EF4444"
    explanation = _build_explanation(score, pillar_scores, weights, cfg)

    # Return sub_scores keyed by pillar name (UI reads this for breakdown bars)
    return {
        "score": score if score is not None else 5.0,
        "explanation": explanation,
        "color": color,
        "sub_scores": pillar_scores,
        "sector_slug": slug,
        "sector_display_name": cfg["display_name"],
        "_weights": weights,
        "proxy_pillars": proxy_pillars,
        "proxy_explanations": proxy_explanations,
    }


# ── Explanation builder ──────────────────────────────────────────────────────

def _build_explanation(score, pillar_scores: dict, weights: dict, cfg: dict) -> str:
    sector_name = cfg["display_name"]
    available = {k: v for k, v in pillar_scores.items() if v is not None}

    if not available or score is None:
        return f"Financial Health: N/A — insufficient data for {sector_name} scoring."

    # Sort by score descending to identify strongest/weakest
    sorted_pillars = sorted(available.items(), key=lambda x: x[1], reverse=True)
    strongest = [p for p, s in sorted_pillars if s >= 7.0]
    weakest   = [p for p, s in sorted_pillars if s < 5.0]

    # Top-2 contributors by weight × score (most impactful to final score)
    impact = sorted(
        [(p, weights.get(p, 0) * v) for p, v in available.items()],
        key=lambda x: -x[1]
    )
    top_contributors = [p for p, _ in impact[:2]]

    score_str = f"{score:.1f}/10"

    if score >= 8.5:
        body = f"Strong across all key {sector_name} pillars."
    elif score >= 7.0:
        if strongest:
            body = f"Strong {' & '.join(strongest[:2])} drive the score."
        else:
            body = f"Solid fundamentals across most {sector_name} metrics."
    elif score >= 5.0:
        if strongest and weakest:
            body = f"Strong {' & '.join(strongest[:2])} offset by weak {' & '.join(weakest[:2])}."
        elif weakest:
            body = f"Watch {' & '.join(weakest[:2])}, which lag {sector_name} benchmarks."
        else:
            body = f"Mixed signals across {sector_name} metrics."
    elif score >= 3.0:
        if weakest:
            body = f"Significant concerns in {' & '.join(weakest[:2])}."
        else:
            body = f"Below-par fundamentals across most {sector_name} metrics."
    else:
        body = f"Distressed profile — most {sector_name} metrics are weak."

    # Sector-specific note for the most impactful pillars
    sector_note = ""
    if top_contributors:
        pillars_str = " and ".join(top_contributors)
        sector_note = f" Sector-weighted {sector_name} scoring prioritises {pillars_str}."

    return f"Financial Health: {score_str} — {body}{sector_note}"
