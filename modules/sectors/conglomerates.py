# modules/sectors/conglomerates.py
"""
Conglomerate Valuation Registry
================================
Some large companies genuinely operate multiple, structurally different
businesses (e.g. Reliance = refining + telecom + retail). Scoring their
consolidated EV/EBITDA against a single sub-sector's peer band (e.g. pure-play
oil & gas) systematically misreads them as "expensive" even when each segment
is fairly valued for what it is, because segments like telecom or retail
legitimately trade at richer multiples than refining/E&P.

This registry lets a company's Valuation pillar be scored against a BLENDED
EV/EBITDA band — each segment's own attractive/fair/expensive band, weighted
by that segment's share of consolidated EBITDA — instead of forcing the whole
company through one segment's peer framework.

⚠️ IMPORTANT LIMITATIONS — read before trusting this blindly:
  1. This only covers companies explicitly added below. Everything else
     still uses the normal single-sector band (unaffected, no regression).
  2. Segment EBITDA weights are a SNAPSHOT from the most recent public
     figures available at the time this was written, not a live feed. They
     WILL drift as the business mix shifts (e.g. Jio's IPO, new segments
     launching) and need periodic manual refresh — there is no automatic
     update mechanism here.
  3. Where a segment doesn't cleanly map to one of this app's existing 20
     sector modules (e.g. general retail, media/entertainment), its band is
     a directly-specified estimate noted inline, not derived from a verified
     comps dataset. Sanity-check against real peer multiples if precision
     matters for that segment.
  4. This is a valuation-pillar-only mechanism — it does NOT change which
     sector's Profitability/Growth/Balance Sheet/Cash Generation weights or
     thresholds apply. Those still use the single primary sector (e.g.
     oil_gas for Reliance), which is its own separate approximation for a
     multi-business company and not something this registry addresses.
     UPDATE: this is no longer true — see get_blended_pillar_weights() and
     get_blended_de_divisor() below, added to extend the same blending
     approach to pillar weights and balance-sheet leverage tolerance. Two
     pillars (Profitability, Growth) turned out not to need blending at all
     for Reliance specifically — every one of its segments already lands in
     the same threshold tier in health_score.py's scoring functions, so the
     result would be identical whether blended or not. That won't
     necessarily hold for a future conglomerate added here with a different
     segment mix (e.g. one that combines a fintech/consumer_internet
     segment with something else) — worth re-checking divisor tiers in
     _score_profitability/_score_growth before assuming they're safe to
     skip for a new entry.
"""

from modules.sectors import get_sector_config
# NOTE: deliberately NOT importing from modules.health_score here — that
# module imports get_blended_ev_ebitda_band from this file, so importing
# _SECTOR_WEIGHTS/_LENIENT_LEVERAGE_SECTORS back from health_score would
# create a circular import. Callers pass those in as parameters instead.

# Each entry: list of (segment_name, ebitda_weight, band_spec) where
# band_spec is either {"slug": "<existing sector slug>"} to borrow that
# sector's own ev_ebitda band, or a direct {"attractive": (lo,hi), "fair":
# (lo,hi), "expensive": (lo,hi)} dict for segments with no good existing
# sector match.
#
# "pillar_weights": {"slug": "..."} borrows that sector's weight map from
# _SECTOR_WEIGHTS; segments with no matching sector module (Retail, Media)
# fall back to "generic" (an equal 25/25/25/25 split) as a transparent,
# defensible default rather than guessing a custom profile.
#
# "leverage_tier": "lenient" (D/E divisor 2.0, i.e. tolerates higher
# leverage — matches _LENIENT_LEVERAGE_SECTORS in health_score.py) or
# "strict" (divisor 4.0). Segments with no sector module default to
# "strict" since that's the majority-case tier and physical retail/media
# aren't infrastructure-heavy the way telecom/utilities/real estate are —
# a judgment call, not derived from hard data.
CONGLOMERATE_REGISTRY: dict = {
    "reliance industries": {
        "match": ["reliance industries"],
        "source_note": (
            "Segment EBITDA from RIL FY26 annual results (year ended Mar 2026): "
            "O2C ₹60,546 Cr, Jio Platforms ₹76,255 Cr, Retail ₹27,033 Cr, "
            "JioStar (media) ₹5,842 Cr. Oil & Gas E&P (KG-D6 etc.) EBITDA isn't "
            "separately disclosed in the sources used here — folded into O2C's "
            "weight as a reasonable approximation since both use the oil_gas "
            "band. Retail and Media have no dedicated sector module in this "
            "app, so their bands below are directly estimated, not sourced "
            "from a verified comps dataset."
        ),
        "segments": [
            {"name": "O2C + Oil & Gas E&P", "ebitda_weight": 60546,
             "band": {"slug": "oil_gas"}, "pillar_weights": {"slug": "oil_gas"},
             "leverage_tier": "strict"},
            {"name": "Jio (Telecom)", "ebitda_weight": 76255,
             "band": {"slug": "telecom"}, "pillar_weights": {"slug": "telecom"},
             "leverage_tier": "lenient"},
            {"name": "Retail", "ebitda_weight": 27033,
             "band": {"attractive": (0, 10), "fair": (10, 16), "expensive": (16, 999)},
             "pillar_weights": {"slug": "generic"}, "leverage_tier": "strict"},
            {"name": "JioStar (Media)", "ebitda_weight": 5842,
             "band": {"attractive": (0, 8), "fair": (8, 14), "expensive": (14, 999)},
             "pillar_weights": {"slug": "generic"}, "leverage_tier": "strict"},
        ],
    },
    "itc limited": {
        "match": ["itc limited"],
        "source_note": (
            "FY26 segment PBIT/results: Cigarettes ₹21,051 Cr and Agri "
            "₹1,496 Cr are DIRECTLY REPORTED figures from ITC's FY26 "
            "results (confirmed across multiple sources, HIGH confidence). "
            "FMCG-Others (~₹2,430 Cr) and Paperboards (~₹755 Cr) are "
            "ESTIMATES derived from disclosed margin percentages and "
            "quarterly PBIT figures (₹24,321.55 Cr FY26 revenue × ~10% "
            "margin for FMCG-Others; Q1 ₹162.6 Cr + Q4 ₹232.5 Cr + "
            "estimated Q2/Q3 for Paperboards) — MEDIUM confidence, not a "
            "directly-reported full-year segment result. The 'Others' "
            "segment (ITC Infotech IT services + hotel + fresh food, "
            "~₹5,036 Cr revenue, ~2% of total) is excluded entirely — no "
            "PBIT breakdown found and it's a small, heterogeneous bucket. "
            "Cigarettes carries an ESG/regulatory valuation discount "
            "(tobacco stocks structurally trade at much lower multiples "
            "than branded FMCG) so it gets its own band rather than "
            "borrowing fmcg's — using fmcg's premium band for the whole "
            "blend would badly overstate what the market will pay for the "
            "cigarette business specifically, even though cigarettes "
            "dominate ITC's profit pool (~82% of the blend weight)."
        ),
        "segments": [
            {"name": "Cigarettes (Tobacco)", "ebitda_weight": 21051,
             "band": {"attractive": (0, 12), "fair": (12, 20), "expensive": (20, 999)},
             "pillar_weights": {"slug": "generic"}, "leverage_tier": "strict"},
            {"name": "FMCG-Others", "ebitda_weight": 2430,
             # fmcg sector config only defines a pe_ratio band, not
             # ev_ebitda, so a slug lookup here would silently fail (the
             # blend bails safely rather than guessing when a referenced
             # band is missing — this is what actually happened when first
             # tested). Using a direct EV/EBITDA band instead, based on
             # typical listed Indian branded-FMCG multiples (HUL, Nestlé
             # India, Britannia, Dabur commonly trade EV/EBITDA in the
             # 20-40x range) — an approximation, not pulled from a live
             # comps feed.
             "band": {"attractive": (0, 20), "fair": (20, 35), "expensive": (35, 999)},
             "pillar_weights": {"slug": "fmcg"}, "leverage_tier": "strict"},
            {"name": "Agri Business", "ebitda_weight": 1496,
             "band": {"attractive": (0, 10), "fair": (10, 16), "expensive": (16, 999)},
             "pillar_weights": {"slug": "generic"}, "leverage_tier": "strict"},
            {"name": "Paperboards, Paper & Packaging", "ebitda_weight": 755,
             "band": {"attractive": (0, 10), "fair": (10, 16), "expensive": (16, 999)},
             "pillar_weights": {"slug": "generic"}, "leverage_tier": "strict"},
        ],
    },
    "larsen & toubro": {
        "match": ["larsen & toubro", "larsen and toubro"],
        "source_note": (
            "FY26 segment EBITDA computed from L&T's own reported segment "
            "revenue × EBITDA margin (both directly disclosed): "
            "Infrastructure Projects ₹133,910 Cr × 6.9% ≈ ₹9,240 Cr, Energy "
            "Projects ₹54,865 Cr × 6.8% ≈ ₹3,731 Cr, IT&TS ₹53,497 Cr × "
            "19.5% ≈ ₹10,432 Cr, Others/Realty+Industrial Valves ₹7,093 Cr "
            "× 31.3% ≈ ₹2,220 Cr (all HIGH confidence — directly reported "
            "revenue and margin). Development Projects (Power Generation, "
            "thermal & green, now largely divested) EBIT ₹539 Cr — directly "
            "reported (HIGH confidence). Hi-Tech Manufacturing EBITDA "
            "≈₹2,314 Cr is a MEDIUM confidence estimate — L&T disclosed its "
            "16.7% margin and order inflow but not its absolute FY26 "
            "revenue directly, so revenue (~₹13,859 Cr) was backed into by "
            "subtracting all other known segments from L&T's total "
            "consolidated revenue (₹285,874 Cr). "
            "\n\n"
            "⚠️ FINANCIAL SERVICES (L&T Finance) IS DELIBERATELY EXCLUDED "
            "from this blend entirely — not a data gap like ITC's 'Others', "
            "a genuine architectural limitation. L&T Finance is a "
            "consolidated NBFC subsidiary (FY26 net profit ≈₹2,900-3,000 Cr, "
            "roughly 17% of L&T Group's ₹17,238 Cr recurring PAT — this is "
            "MATERIAL, not a rounding error) whose EV/EBITDA and D/E simply "
            "don't mean the same thing as an EPC/manufacturing business's: "
            "NBFC leverage of 3-4x D/E is structurally normal and healthy "
            "for a lender, not distress leverage, and this app's own "
            "scoring engine already special-cases banking/nbfc/insurance "
            "out of the D/E leverage check for exactly that reason (see "
            "_score_balance_sheet in health_score.py). Folding L&T Finance "
            "into this blend naively — treating its P&L like an "
            "industrial EBITDA — would produce a misleading number, and "
            "correctly blending a P/B-scored segment together with "
            "EV/EBITDA-scored segments is genuinely new blending logic "
            "this registry doesn't build, not just a data-sourcing task. "
            "Practical effect: L&T's Valuation pillar here reflects ~83% "
            "of the group (the EPC/manufacturing/IT businesses), not the "
            "consolidated whole — worth knowing if group-level leverage "
            "or valuation precision matters for your use case."
        ),
        "segments": [
            {"name": "Infrastructure Projects", "ebitda_weight": 9240,
             # capital_goods sector config only defines a pe_ratio band, not
             # ev_ebitda (same gap pattern as ITC's fmcg segment) — direct
             # band here, roughly PE-band-equivalent for an EPC/contracting
             # margin profile (~PE 20-35 → ~EV/EBITDA 10-18 is a common
             # rule-of-thumb conversion for moderately-levered industrials,
             # not pulled from a live comps feed).
             "band": {"attractive": (0, 10), "fair": (10, 18), "expensive": (18, 999)},
             "pillar_weights": {"slug": "capital_goods"}, "leverage_tier": "strict"},
            {"name": "Energy Projects (Hydrocarbon/CarbonLite EPC)", "ebitda_weight": 3731,
             "band": {"attractive": (0, 10), "fair": (10, 18), "expensive": (18, 999)},
             "pillar_weights": {"slug": "capital_goods"}, "leverage_tier": "strict"},
            {"name": "IT & Technology Services", "ebitda_weight": 10432,
             "band": {"slug": "it_services"}, "pillar_weights": {"slug": "it_services"},
             "leverage_tier": "strict"},
            {"name": "Hi-Tech Manufacturing (Precision Eng., Defence/Space)", "ebitda_weight": 2314,
             "band": {"attractive": (0, 10), "fair": (10, 18), "expensive": (18, 999)},
             "pillar_weights": {"slug": "capital_goods"}, "leverage_tier": "strict"},
            {"name": "Others (Realty, Industrial Valves, Construction Equip.)", "ebitda_weight": 2220,
             "band": {"attractive": (0, 10), "fair": (10, 18), "expensive": (18, 999)},
             "pillar_weights": {"slug": "capital_goods"}, "leverage_tier": "strict"},
            {"name": "Development Projects (Power Generation)", "ebitda_weight": 539,
             "band": {"slug": "power_utilities"}, "pillar_weights": {"slug": "power_utilities"},
             "leverage_tier": "lenient"},
        ],
    },
    "adani enterprises": {
        "match": ["adani enterprises"],
        "source_note": (
            "AEL FY26 segment EBITDA, sourced from Q4/FY26 results presentation "
            "and Q4 FY26 earnings call highlights (all DIRECTLY REPORTED, HIGH "
            "confidence): ANIL (green energy/solar+wind mfg/green hydrogen) "
            "₹4,532 Cr (FY25 ₹4,776 Cr, -5% — margin compression from a "
            "domestic-sales-heavy solar mix), Airports (AAHL) ₹5,394 Cr "
            "(+55%, >30% of consolidated EBITDA on its own), Roads (ARTL) "
            "₹1,362 Cr (-23%, revenue declining as projects move from "
            "construction to operational/annuity phase), Mining Services "
            "₹1,986 Cr (+18%), IRM/Integrated Resource Management (legacy "
            "commodity trading) ₹2,767 Cr (-23%). These 5 segments sum to "
            "₹16,041 Cr of AEL's ₹16,464 Cr total FY26 EBITDA (~97.4%). "
            "The remaining ~₹423 Cr (~2.6%) — Commercial Mining (hit by "
            "weather disruptions in Australia + mark-to-market markdowns "
            "this year), the newly-commissioned Copper plant (loss-heavy "
            "from fresh depreciation), PVC, and Defence — is excluded "
            "entirely as an immaterial, still-forming residual with no "
            "clean standalone disclosure, same treatment as ITC's 'Others'. "
            "AdaniConnex (data centers) is equity-accounted, not "
            "consolidated, and isn't part of AEL's EBITDA at all. "
            "Airports and Roads have no dedicated sector module in this "
            "app: Airports gets a direct band reflecting the premium, "
            "scarcity-value multiples Indian aviation infra commands (an "
            "estimate, not comps-derived); Roads borrows power_utilities' "
            "band/weights/leverage-tier as a proxy for long-duration, "
            "contracted-cashflow infra (HAM/TOT annuity structure), which "
            "is a reasonable analogy but not a perfect match since it's "
            "literally a power-generation sector profile. IRM is a "
            "low-margin, high-volume trading business — given a direct, "
            "low EV/EBITDA band distinct from Mining Services' own "
            "metals_mining band, since blending trading margins with "
            "actual mining-services margins would misprice both."
        ),
        "segments": [
            {"name": "ANIL (Green Energy: Solar/Wind Mfg + Green Hydrogen)", "ebitda_weight": 4532,
             "band": {"slug": "renewable_energy"}, "pillar_weights": {"slug": "renewable_energy"},
             "leverage_tier": "lenient"},
            {"name": "Airports (AAHL)", "ebitda_weight": 5394,
             # No dedicated "airports"/aviation-infra sector module exists.
             # Indian listed aviation-infra comps are scarce but trade at a
             # scarcity/monopoly premium (long concessions, non-aero revenue
             # optionality) — this band is a direct estimate, not pulled
             # from a verified comps dataset.
             "band": {"attractive": (0, 12), "fair": (12, 20), "expensive": (20, 999)},
             "pillar_weights": {"slug": "generic"}, "leverage_tier": "lenient"},
            {"name": "Roads (ARTL)", "ebitda_weight": 1362,
             # Borrowing power_utilities as a proxy for long-duration,
             # contracted-cashflow infra (HAM/TOT annuity model) — a
             # reasonable analogy given the annuity-like cash flow profile,
             # but power_utilities is literally a power-generation sector
             # profile, not roads-specific. Revisit if a roads/toll-specific
             # module is ever added.
             "band": {"slug": "power_utilities"}, "pillar_weights": {"slug": "power_utilities"},
             "leverage_tier": "lenient"},
            {"name": "Mining Services", "ebitda_weight": 1986,
             "band": {"slug": "metals_mining"}, "pillar_weights": {"slug": "metals_mining"},
             "leverage_tier": "strict"},
            {"name": "IRM (Integrated Resource Management / Commodity Trading)", "ebitda_weight": 2767,
             # Low-margin, high-volume trading business — kept separate from
             # Mining Services' metals_mining band since blending the two
             # would misprice both (trading multiples are structurally
             # lower than mining-services multiples). Direct estimate, not
             # comps-derived.
             "band": {"attractive": (0, 4), "fair": (4, 7), "expensive": (7, 999)},
             "pillar_weights": {"slug": "generic"}, "leverage_tier": "strict"},
        ],
    },
    "aditya birla capital": {
        "match": ["aditya birla capital"],
        "valuation_metric": "price_to_book",  # see note in get_blended_pb_band
        "source_note": (
            "ABCL FY26 segment PBT (DIRECTLY REPORTED in FY26 results press release "
            "and Q4 FY26 investor presentation, HIGH confidence): NBFC (Aditya Birla "
            "Finance) PBT Rs 4,023 Cr (ROA 2.25%, Gross Stage 2&3 2.42%), Housing Finance "
            "(Aditya Birla Housing Finance) PBT Rs 832 Cr (ROA 1.88%, Gross Stage 2&3 "
            "0.76%), Life Insurance (Aditya Birla Sun Life Insurance) operating profit "
            "Rs 1,051 Cr used as the PBT-equivalent weight (VNB margin 20.6%, up 260bps "
            "YoY - insurers report 'operating profit' rather than a standard PBT line "
            "under IRDAI norms, so this is the closest like-for-like segment-mix metric)."
            "\n\n"
            "WARNING: ASSET MANAGEMENT (Aditya Birla Sun Life AMC) AND HEALTH INSURANCE "
            "(Aditya Birla Health Insurance) ARE DELIBERATELY EXCLUDED - not a data "
            "gap, an architectural one. ABCL's own investor presentation footnotes "
            "state AMC, wellness, and health insurance are NOT consolidated into ABCL's "
            "segment financials at all - they're equity-accounted associates/JVs (ABCL "
            "holds ~45% of both), so their profit shows up as a single 'share of "
            "associate profit' line, not real segment PBT comparable to the NBFC/HFC/ "
            "Life Insurance figures above. Worse for AMC specifically: Aditya Birla Sun "
            "Life AMC is ITSELF SEPARATELY LISTED (ABSLAMC.NS) and already scored on its "
            "own ticker elsewhere in this app - blending its numbers into ABCL's would "
            "double-count it, the same double-counting problem that ruled out folding "
            "Godrej Consumer/Properties/Agrovet into a hypothetical Godrej Industries "
            "entry. Health Insurance (ABHI) is smaller, was still loss-making as "
            "recently as FY24/H1FY25 (~Rs 115-182 Cr PBT loss) even though FY26 GWP grew "
            "39% and combined ratio improved to 103%, and has no clean standalone FY26 "
            "PBT disclosure in the sources checked - excluded on materiality/data-gap "
            "grounds too, same treatment as ITC's 'Others' bucket. "
            "Practical effect: this blend covers the genuinely-consolidated lending + "
            "life insurance businesses (the bulk of ABCL's reported consolidated PAT), "
            "not the full economic group - AMC's own listed stock is the correct place "
            "to look for that piece."
            "\n\n"
            "Uses PRICE-TO-BOOK, not EV/EBITDA, as the blend metric - see "
            "get_blended_pb_band() below. EV/EBITDA doesn't mean the same thing for a "
            "lender or insurer (this app's own health_score.py already special-cases "
            "banking/nbfc/insurance onto P/B for exactly that reason), so this entry "
            "reuses the same segment-weighting idea as the rest of this registry but "
            "against each segment's own P/B band instead."
        ),
        "segments": [
            {"name": "NBFC (Aditya Birla Finance)", "ebitda_weight": 4023,
             "band": {"slug": "nbfc"}, "pillar_weights": {"slug": "nbfc"}},
            {"name": "Housing Finance (Aditya Birla Housing Finance)", "ebitda_weight": 832,
             # No dedicated HFC sector module - housing finance is structurally an
             # NBFC (same P/B-scored, spread-based lending model), so it borrows
             # nbfc's band/weights rather than getting a bespoke one.
             "band": {"slug": "nbfc"}, "pillar_weights": {"slug": "nbfc"}},
            {"name": "Life Insurance (Aditya Birla Sun Life Insurance)", "ebitda_weight": 1051,
             "band": {"slug": "insurance"}, "pillar_weights": {"slug": "insurance"}},
        ],
    },
    "mahindra & mahindra": {
        "match": ["mahindra & mahindra", "mahindra and mahindra", "m&m limited", "m&m ltd"],
        "source_note": (
            "M&M Ltd FY26 STANDALONE segment PBIT (directly reported, HIGH "
            "confidence): Automotive ₹10,141 Cr (margin 9.3%, 10.5% excl. "
            "eSUV contract mfg) and Farm Equipment ₹7,206 Cr (margin 19.9%, "
            "+35% YoY, on record 5 lakh+ tractor billings and 43.6% market "
            "share). Deliberately uses STANDALONE M&M Ltd figures, not the "
            "₹1,98,639 Cr consolidated group revenue — the consolidated "
            "number includes Tech Mahindra, Mahindra Finance, Mahindra "
            "Logistics, Mahindra Lifespace, Mahindra Holidays, and other "
            "listed subsidiaries, which each already trade as their own "
            "stock and should be scored independently, not folded into "
            "M&M's own blend (would double-count them). Farm Equipment gets "
            "its own richer band rather than sharing auto_ev's band with "
            "Automotive: tractor pure-plays in India trade materially "
            "richer than mainstream auto OEMs (e.g. Escorts Kubota's "
            "current EV/EBITDA ~21.6x, 3-year average ~30x, vs auto_ev's "
            "existing 8-14x fair band) reflecting higher margins, less "
            "commoditized competition, and rural-demand resilience. This "
            "Farm Equipment band is a direct estimate calibrated off that "
            "comp, not a live comps feed, and Escorts' own multiple has "
            "swung widely (21.6x now vs 30x 3-yr avg), so treat it as "
            "indicative rather than precise."
        ),
        "segments": [
            {"name": "Automotive (SUVs, CVs, EVs)", "ebitda_weight": 10141,
             "band": {"slug": "auto_ev"}, "pillar_weights": {"slug": "auto_ev"},
             "leverage_tier": "strict"},
            {"name": "Farm Equipment (Tractors)", "ebitda_weight": 7206,
             # No dedicated farm-equipment/tractor sector module exists.
             # Calibrated off Escorts Kubota's EV/EBITDA (~21.6x current,
             # ~30x 3-yr avg) as the closest listed pure-play comp — a
             # direct estimate, not pulled from a verified comps dataset.
             "band": {"attractive": (0, 14), "fair": (14, 22), "expensive": (22, 999)},
             "pillar_weights": {"slug": "generic"}, "leverage_tier": "strict"},
        ],
    },
}


def _resolve_band(band_spec: dict) -> dict | None:
    """Resolve a segment's band spec to an actual attractive/fair/expensive dict."""
    if "slug" in band_spec:
        cfg = get_sector_config(band_spec["slug"])
        return cfg.get("valuation", {}).get("bands", {}).get("ev_ebitda")
    return band_spec


def get_conglomerate_match(company_name: str) -> dict | None:
    """Return the registry entry for company_name, or None if not registered."""
    if not company_name:
        return None
    name_lower = company_name.lower()
    for entry in CONGLOMERATE_REGISTRY.values():
        if any(pat in name_lower for pat in entry["match"]):
            return entry
    return None


def get_blended_ev_ebitda_band(company_name: str) -> tuple[float, float] | None:
    """Return a (low, high) EV/EBITDA band = weighted blend of each segment's
    own attractive/fair boundary, weighted by EBITDA share. Returns None if
    the company isn't in the registry or a segment's band can't be resolved."""
    entry = get_conglomerate_match(company_name)
    if not entry:
        return None

    segments = entry["segments"]
    total_weight = sum(s["ebitda_weight"] for s in segments)
    if total_weight <= 0:
        return None

    blended_low = blended_high = 0.0
    for seg in segments:
        band = _resolve_band(seg["band"])
        if not band:
            return None  # a referenced sector's band is missing — bail rather than silently skip a segment
        frac = seg["ebitda_weight"] / total_weight
        blended_low  += frac * band["attractive"][1]
        blended_high += frac * band["fair"][1]

    return (round(blended_low, 2), round(blended_high, 2))


def _resolve_pb_band(band_spec: dict) -> dict | None:
    """Same idea as _resolve_band, but reads a sector's price_to_book band
    instead of ev_ebitda. Used only by financial-conglomerate entries (see
    'aditya birla capital' above) whose segments are lenders/insurers, where
    P/B is the meaningful valuation multiple, not EV/EBITDA."""
    if "slug" in band_spec:
        cfg = get_sector_config(band_spec["slug"])
        return cfg.get("valuation", {}).get("bands", {}).get("price_to_book")
    return band_spec


def get_blended_pb_band(company_name: str) -> tuple[float, float] | None:
    """Return a (low, high) P/B band = weighted blend of each segment's own
    attractive/fair boundary, weighted by PBT share (reusing the same
    'ebitda_weight' field name as the EV/EBITDA path for consistency, even
    though it holds PBT for these entries - EBITDA isn't a meaningful concept
    for a lender or insurer). Only applies to registry entries whose
    'valuation_metric' is explicitly "price_to_book" - everything else falls
    through untouched, so this doesn't affect Reliance/ITC/L&T/Adani/M&M.
    Returns None if the company isn't registered as a P/B-blend entry or a
    segment's band can't be resolved."""
    entry = get_conglomerate_match(company_name)
    if not entry or entry.get("valuation_metric") != "price_to_book":
        return None

    segments = entry["segments"]
    total_weight = sum(s["ebitda_weight"] for s in segments)
    if total_weight <= 0:
        return None

    blended_low = blended_high = 0.0
    for seg in segments:
        band = _resolve_pb_band(seg["band"])
        if not band:
            return None
        frac = seg["ebitda_weight"] / total_weight
        blended_low  += frac * band["attractive"][1]
        blended_high += frac * band["fair"][1]

    return (round(blended_low, 2), round(blended_high, 2))


def get_blended_pillar_weights(company_name: str, sector_weights: dict) -> dict | None:
    """Return a blended {pillar_name: weight} dict = weighted average of each
    segment's own sector weight map (weighted by EBITDA share), instead of
    using only the primary/dominant segment's weight profile for the whole
    company. sector_weights should be health_score.py's _SECTOR_WEIGHTS dict
    (passed in rather than imported, to avoid a circular import — this
    module is imported BY health_score.py). Returns None if not registered
    or a segment's weight map can't be resolved.

    Example of why this matters: oil_gas weights Cash Generation heavily
    (30%) and Valuation lightly (10%), reflecting that pure upstream/
    refining businesses are judged mainly on cash generation. Telecom
    weights Balance Sheet and Growth more, Cash Generation less. Blending
    means a conglomerate's overall weight profile reflects its actual
    business mix instead of whichever single segment's profile the sector
    detector happened to resolve as "primary".
    """
    entry = get_conglomerate_match(company_name)
    if not entry:
        return None

    segments = entry["segments"]
    total_weight = sum(s["ebitda_weight"] for s in segments)
    if total_weight <= 0:
        return None

    blended: dict[str, float] = {}
    for seg in segments:
        pw_spec = seg.get("pillar_weights")
        if not pw_spec or "slug" not in pw_spec:
            return None
        seg_weights = sector_weights.get(pw_spec["slug"])
        if not seg_weights:
            return None
        frac = seg["ebitda_weight"] / total_weight
        for pillar, w in seg_weights.items():
            blended[pillar] = blended.get(pillar, 0.0) + frac * w

    # Normalize to sum to 100 (segments' own weight maps don't always sum to
    # exactly the same total as each other before blending — e.g. a segment
    # using "generic" which only has 4 pillars vs. oil_gas's 5 — so the
    # blended raw sum can drift slightly from 100).
    total = sum(blended.values())
    if total <= 0:
        return None
    return {k: round(v / total * 100, 1) for k, v in blended.items()}


def get_blended_commodity_weight(company_name: str, commodity_slugs: tuple) -> float | None:
    """Return the fraction (0-1) of a registered conglomerate's EBITDA that
    sits in commodity-price-driven segments (per `commodity_slugs`, e.g.
    oil_gas/metals_mining).

    Used by moat_analysis.py to scale its commodity-cyclicality discount
    proportionally, instead of applying the FULL discount to a company's
    entire moat score just because its single primary sector label (from
    classify_sector) happens to be oil_gas/metals_mining. Reliance is the
    motivating case: classify_sector() resolves it to "oil_gas" (its
    yfinance sector/industry strings), so without this the commodity
    discount was being applied at full strength even though O2C+E&P is only
    ~36% of consolidated EBITDA — Jio/Retail/Media (not commodity-cyclical)
    make up the rest.

    Returns None if the company isn't registered here, letting the caller
    fall back to its own primary-sector-based (all-or-nothing) logic.
    """
    entry = get_conglomerate_match(company_name)
    if not entry:
        return None

    segments = entry["segments"]
    total_weight = sum(s["ebitda_weight"] for s in segments)
    if total_weight <= 0:
        return None

    commodity_weight = 0.0
    for seg in segments:
        pw_spec = seg.get("pillar_weights", {})
        slug = pw_spec.get("slug") if isinstance(pw_spec, dict) else None
        if slug in commodity_slugs:
            commodity_weight += seg["ebitda_weight"]

    return round(commodity_weight / total_weight, 4)


def get_blended_de_divisor(company_name: str, lenient_sectors: tuple, lenient_divisor: float = 2.0,
                            strict_divisor: float = 4.0) -> float | None:
    """Return a blended D/E scoring divisor for the Balance Sheet pillar's
    leverage-tolerance check — weighted average of each segment's own
    lenient/strict tier, by EBITDA share. lenient_sectors should be
    health_score.py's _LENIENT_LEVERAGE_SECTORS tuple (passed in for the
    same circular-import reason as above). Returns None if not registered.
    """
    entry = get_conglomerate_match(company_name)
    if not entry:
        return None

    segments = entry["segments"]
    total_weight = sum(s["ebitda_weight"] for s in segments)
    if total_weight <= 0:
        return None

    blended = 0.0
    for seg in segments:
        tier = seg.get("leverage_tier")
        if tier is None:
            # Fall back to deriving from the segment's own sector slug, if
            # it has one, using the same membership test health_score.py
            # itself uses — keeps this consistent if a future registry
            # entry forgets to set leverage_tier explicitly.
            pw_spec = seg.get("pillar_weights", {})
            slug = pw_spec.get("slug") if isinstance(pw_spec, dict) else None
            tier = "lenient" if slug in lenient_sectors else "strict"
        divisor = lenient_divisor if tier == "lenient" else strict_divisor
        frac = seg["ebitda_weight"] / total_weight
        blended += frac * divisor

    return round(blended, 3)
