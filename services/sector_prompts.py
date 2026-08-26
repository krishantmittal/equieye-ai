# services/sector_prompts.py
"""
Sector-specific prompt-engineering fragments used to steer the bull/bear
LLM prompt away from generic corporate framing. Extracted from app.py's
_SECTOR_CLASS_MAP / _FIN_SLUG_CLASS_MAP verbatim — pure data, no
Streamlit dependency. This is tuned prompt IP, not boilerplate; do not
reword without re-validating output quality for the affected sectors.
"""

from __future__ import annotations

# Sector class guardrail map — static, built once at module load.
SECTOR_CLASS_MAP = {
    "Consumer Defensive": (
        "CONSUMER DEFENSIVE (staples)",
        "demand is non-cyclical — consumers buy these products regardless of economic conditions. "
        "Do NOT describe revenue as sensitive to consumer spending cycles or discretionary income. "
        "Valid bear risks: input cost inflation, private-label competition, distribution disruption, regulatory pricing caps."
    ),
    "Consumer Cyclical": (
        "CONSUMER CYCLICAL (discretionary)",
        "demand IS sensitive to economic cycles and disposable income. "
        "Valid bear risks: slowdown in consumer spending, income pressure, premiumisation reversal."
    ),
    "Financial Services": (
        "FINANCIAL SERVICES",
        "revenue is driven by credit growth, NIMs, and asset quality — not consumer spending cycles. "
        "Valid bear risks: NPA rise, margin compression, regulatory tightening, credit cost."
    ),
    "Technology": (
        "TECHNOLOGY / IT SERVICES",
        "revenue is driven by enterprise IT spend and deal wins — not retail consumer spending. "
        "Valid bear risks: deal slowdown, attrition, pricing pressure, currency headwinds."
    ),
    "Energy": (
        "ENERGY",
        "revenue is driven by commodity prices and volumes — not consumer spending cycles. "
        "Valid bear risks: oil/gas price volatility, capex overruns, regulatory risk."
    ),
}

# ── Granular slug overrides ──────────────────────────────────────────────────
# yfinance's raw sector/industry strings are too coarse for several sectors:
# "Financial Services" lumps banks, NBFCs, insurers, and fintechs into one
# bucket; "Healthcare" lumps generic formulators, API/CDMO manufacturers,
# specialty pharma, and biotech into one bucket. These override the generic
# SECTOR_CLASS_MAP entry above when a more precise sector slug (from
# classify_sector) is available. Fintech is deliberately NOT overridden here
# — it behaves like a normal growth corporate (real revenue/EBITDA/margin
# metrics), so the generic rules and metric variables already fit it fine.
FIN_SLUG_CLASS_MAP = {
    "banking": (
        "BANKING",
        "revenue is driven by credit growth, NIMs, and asset quality — not consumer spending cycles. "
        "Valid bear risks: NPA rise, margin compression, regulatory tightening, credit cost. "
        "BULL HEADLINES — a bank is NEVER analysed like a normal corporate. "
        "Do NOT use generic headlines such as 'Revenue Momentum', 'Compounding Growth', 'Margin Strength', "
        "or 'Pricing Power' — these describe a manufacturer or consumer company, not a lender. "
        "Instead choose bull headlines from: 'Credit Growth' (loan book expansion, grounded in {rev_cagr} "
        "as a proxy since NII tracks the loan book), 'Deposit Growth' / 'CASA Strength' (low-cost funding "
        "franchise), 'Retail Mix' (granular, diversified book), 'NIM Strength' (spread economics — grounded "
        "qualitatively in the company description, not a fabricated NIM number), 'Fee Income Growth' "
        "(cross-sell / non-interest income), 'Return Ratios' (grounded in {roe} and {roa}, NOT relabelled as "
        "generic 'Margin Strength'), OR — and prefer this one over the others if it exists — a recent-development "
        "headline grounded in an item from RECENT NEWS HEADLINES above, if one was genuinely provided there; "
        "a specific real event is stronger evidence than any of the generic themes above and should take one "
        "of the 3 bull slots when available. IMPORTANT: the headline for this one must match what the news "
        "item ACTUALLY describes — 'Strategic Acquisition' and 'Inorganic Growth' are examples for an actual "
        "acquisition/purchase, NOT default labels to reuse regardless of content. A new product or account "
        "launch is 'Product Launch' or 'Distribution Expansion', not an acquisition; a management change is "
        "'Leadership Change'; a rating action is 'Credit Rating Action'. Pick the label that fits the specific "
        "event, don't copy an example that doesn't match. If no numeric metric exists for a theme (e.g. CASA, "
        "NIM, credit growth — yfinance does not provide these for Indian banks), write the explanation "
        "qualitatively from the company description instead of inventing a number, and do not cite "
        "{ttm_net_margin} as if it were NIM."
    ),
    "nbfc": (
        "NBFC / LENDING",
        "revenue is driven by AUM growth, cost of borrowing, and asset quality — not consumer spending cycles. "
        "Unlike a bank, an NBFC does NOT take retail deposits, so 'CASA' and 'Deposit Growth' do not apply. "
        "Valid bear risks: asset-liability mismatch, rising cost of funds, NPA rise, regulatory tightening on "
        "unsecured lending. "
        "BULL HEADLINES — do NOT use generic corporate headlines like 'Revenue Momentum' or 'Margin Strength'. "
        "Instead choose from: 'AUM Growth' (loan book expansion, grounded in {rev_cagr}/{profit_cagr}), "
        "'Disbursement Growth', 'Yield Management' (spread over cost of funds — write qualitatively unless a "
        "real number exists), 'Diversified Borrowing Mix' (funding-source resilience), 'Return Ratios' "
        "(grounded in {roe} and {roa}), OR — and prefer this one over the others if it exists — a "
        "recent-development headline grounded in an item from RECENT NEWS HEADLINES above, if one was "
        "genuinely provided there; a specific real event is stronger evidence than a generic theme and should "
        "take one of the 3 bull slots when available. Do not invent a CASA ratio or NIM figure — those are "
        "bank-only concepts."
    ),
    "insurance": (
        "INSURANCE",
        "revenue is driven by new business premium, persistency, and claims experience — not consumer "
        "spending cycles or a conventional profit margin. "
        "Valid bear risks: rising claims/loss ratio, regulatory changes to commission structures, "
        "declining persistency, solvency pressure. "
        "BULL HEADLINES — do NOT use generic corporate headlines like 'Revenue Momentum' or 'Margin Strength', "
        "and do NOT frame growth as 'Credit Growth' or 'CASA' (those are banking concepts, not insurance). "
        "Instead choose from: 'Premium Growth' (grounded in {rev_cagr}), 'Persistency Strength', "
        "'Product Mix Improvement' (protection vs savings mix), 'Distribution Reach' (agency/bancassurance "
        "network), 'Return Ratios' (grounded in {roe}), OR — and prefer this one over the others if it exists "
        "— a recent-development headline grounded in an item from RECENT NEWS HEADLINES above, if one was "
        "genuinely provided there; a specific real event is stronger evidence than a generic theme and should "
        "take one of the 3 bull slots when available. Write persistency/VNB/embedded-value points "
        "qualitatively from the company description rather than inventing a number — yfinance does not "
        "provide insurance-specific disclosures."
    ),
    # ── Pharma sub-sector overrides ─────────────────────────────────────────
    # Generic-formulator/API/CDMO/specialty/biotech businesses are
    # structurally low-debt (D/E typically well under 1x — see each sector
    # module's llm_context), so without an explicit override the LLM would
    # fall back to the generic "UNCLASSIFIED" bucket and could still default
    # to a generic "Leverage Risk" bear headline even when D/E is nowhere
    # near elevated (e.g. Dr. Reddy's ~0.20x) — the METRIC CONTRADICTION
    # CHECK further down only catches the literal phrase "high debt", not a
    # mislabeled "Leverage Risk" headline sitting next to a low D/E figure.
    "pharma_generics": (
        "PHARMACEUTICALS — GENERIC FORMULATORS",
        "revenue is driven by US ANDA pipeline execution, domestic branded-formulation growth in chronic "
        "therapies, and complex/specialty generics mix — not a conventional consumer-spending or credit cycle. "
        "Valid bull themes: biosimilars pipeline progress/launches, consumer healthcare (OTC/wellness) portfolio "
        "growth, emerging-markets expansion (Russia/CIS, LatAm, Africa), specialty/complex-generics portfolio "
        "(injectables, inhalers, peptides, GLP-1s/biosimilars), India branded-formulations growth in chronic "
        "therapies (diabetes, cardiac, respiratory), Para IV first-to-file wins. "
        "Valid bear risks: USFDA facility/inspection risk (warning letters, import alerts, Form 483 "
        "observations), execution risk on a complex pipeline launch (e.g. a flagship biosimilar or specialty "
        "product), US base-generics pricing erosion, currency exposure (USD/INR and other EM-currency "
        "translation on export/EM revenue), regulatory/approval delays (ANDA or biosimilar review timelines). "
        "LEVERAGE CAVEAT — this business model is structurally low-debt; do NOT default to a generic "
        "'Leverage Risk' or 'High Leverage' bear headline unless {de} is genuinely elevated for this sector "
        "(>1.0x) — a D/E materially under that (e.g. 0.2-0.5x) must NEVER be framed as a leverage risk, and "
        "'Low Leverage'/'Clean Balance Sheet' should be considered as a BULL point instead when {de} is low."
    ),
    "pharma_api": (
        "PHARMACEUTICALS — API / BULK DRUG MANUFACTURER",
        "revenue is driven by API/intermediate volumes sold to formulators, customer concentration, and "
        "China-competition dynamics — not a conventional consumer-spending or credit cycle. "
        "Valid bull themes: capacity expansion, backward integration, customer diversification, regulated-market "
        "(US/EU) qualification wins, PLI-scheme benefits, complex/high-value molecule mix shift. "
        "Valid bear risks: USFDA facility/inspection risk, customer concentration, China-based competitor "
        "price undercutting, currency exposure (export revenue), regulatory/approval delays on new "
        "molecule filings. "
        "LEVERAGE CAVEAT — this business model is structurally low-debt; do NOT default to a generic "
        "'Leverage Risk' bear headline unless {de} is genuinely elevated (>1.0x) for this sector."
    ),
    "pharma_cdmo": (
        "PHARMACEUTICALS — CDMO (CONTRACT MANUFACTURER)",
        "revenue is driven by client relationships, contracted manufacturing volumes, and client concentration "
        "— not a conventional consumer-spending or credit cycle. "
        "Valid bull themes: new client wins/molecule additions, capacity expansion, moving up the value chain "
        "(from intermediate to finished-dose contracts), regulated-market facility approvals. "
        "Valid bear risks: USFDA facility/inspection risk, client concentration (loss of a key contract), "
        "pricing pressure from clients, currency exposure, regulatory/approval delays on client filings. "
        "LEVERAGE CAVEAT — this business model is structurally low-debt; do NOT default to a generic "
        "'Leverage Risk' bear headline unless {de} is genuinely elevated (>1.0x) for this sector."
    ),
    "pharma_specialty": (
        "PHARMACEUTICALS — SPECIALTY",
        "revenue is driven by patent-protected/differentiated product sales and pipeline execution — binary "
        "clinical/regulatory outcomes matter more here than for a generics-only peer. "
        "Valid bull themes: pipeline readouts/approvals, patent-life runway on lead products, specialty "
        "portfolio expansion, biosimilars pipeline optionality, emerging-markets expansion. "
        "Valid bear risks: USFDA facility/inspection risk, clinical/regulatory pipeline setbacks (CRLs, trial "
        "failures), patent-cliff exposure on lead products, pricing pressure, currency exposure, regulatory/"
        "approval delays. "
        "LEVERAGE CAVEAT — this business model is structurally low-debt; do NOT default to a generic "
        "'Leverage Risk' bear headline unless {de} is genuinely elevated (>1.0x) for this sector."
    ),
    "biotech": (
        "PHARMACEUTICALS — BIOTECH",
        "revenue and value are driven by binary clinical/regulatory pipeline outcomes and manufacturing "
        "complexity — not a conventional consumer-spending or credit cycle, and often not yet profitable. "
        "Valid bull themes: pipeline readouts/approvals, biosimilars portfolio progress, manufacturing-scale-up "
        "milestones, partnership/licensing deals, emerging-markets expansion. "
        "Valid bear risks: clinical/regulatory pipeline setbacks (CRLs, trial failures), USFDA facility/"
        "inspection risk, manufacturing-complexity execution risk, cash-runway/funding risk, currency exposure, "
        "regulatory/approval delays. "
        "LEVERAGE CAVEAT — do NOT default to a generic 'Leverage Risk' bear headline unless {de} is genuinely "
        "elevated (>1.0x) for this sector — biotech risk is dominated by pipeline/regulatory outcomes, not debt."
    ),
    # ── Commodity-cyclical override ──────────────────────────────────────────
    # yfinance's "Basic Materials"/"Energy" sector tags read like any other
    # corporate — the default bucket produces generic "Revenue Momentum" /
    # "Pricing Power" / "Debt Risk" bull/bear themes lifted straight from a
    # branded-consumer or IT-services playbook, which misses what actually
    # moves a commodity stock: global price cycles, not demand elasticity or
    # pricing power the company itself controls.
    "metals_mining": (
        "METALS & MINING (COMMODITY CYCLICAL)",
        "revenue and margins are driven primarily by global commodity price cycles (aluminium, zinc, iron ore, "
        "copper, oil & gas — as applicable) and China demand/supply dynamics, NOT by pricing power, brand, or "
        "a conventional demand cycle the company itself controls — a high net margin here usually reflects "
        "where the commodity cycle currently sits, not durable pricing power, so do NOT frame a strong TTM "
        "margin as 'Pricing Power' the way you would for a branded consumer or platform business. "
        "Valid bull themes: captive raw-material integration (owned mines reducing input-cost exposure), "
        "brownfield capacity expansion (cheaper/faster than greenfield), value-added/specialty product mix "
        "shift (e.g. auto-grade steel, specialty alloys) improving realisation over commodity-grade pricing, "
        "China supply-side reform or property-sector slowdown easing global oversupply, infrastructure/"
        "construction capex cycle demand, and diversification across multiple commodities/geographies reducing "
        "single-commodity-price dependence. "
        "Valid bear risks: a commodity price downturn (global recession, China hard-landing, oversupply), "
        "input-cost inflation (energy, coking coal, freight) compressing margins independent of output prices, "
        "leverage amplifying downside specifically during a cyclical trough (unlike a branded consumer "
        "business, leverage genuinely matters more here — do NOT suppress a leverage-risk bear point the way "
        "you would for a low-cyclicality sector), regulatory/mining-lease renewal risk, and — for diversified "
        "conglomerate miners with a listed parent/holding structure — group-level governance or cash-"
        "upstreaming risk (e.g. dividend payouts to a leveraged parent entity) IS a valid bear theme, but only "
        "state it if grounded in something the company description or provided data actually supports, never "
        "invented. "
        "Do NOT use generic corporate bull headlines like 'Revenue Momentum' or 'Pricing Power' without tying "
        "them explicitly to the commodity cycle or a structural cost/integration advantage — a commodity "
        "company's margin strength this year says more about where prices are in the cycle than about the "
        "business."
    ),
    # ── Defense & aerospace override ─────────────────────────────────────────
    # This sector had no coverage at all before — companies like Hindustan
    # Aeronautics fell into the generic/unclassified bucket, producing
    # generic "Brand & Market Position" / "Slowing growth relative to peer
    # set" bull/bear themes lifted from a normal industrial playbook, which
    # misses the sector's defining trait: revenue concentrated in a single
    # government customer, not open-market competition.
    "defense_aerospace": (
        "DEFENSE & AEROSPACE",
        "revenue is driven overwhelmingly by a single customer (the Ministry of Defence / Indian Armed "
        "Forces) and government budget allocation/indigenization policy, NOT by open-market competition, "
        "brand, or a conventional demand cycle — frame customer concentration in those specific single-"
        "customer terms, not generic industrial-customer-concentration language. "
        "Valid bull themes: indigenization/Atmanirbhar Bharat policy tailwind directing new orders to "
        "domestic players, export order wins diversifying beyond the single-customer domestic base, margin "
        "expansion as indigenous content share rises versus licensed/imported-component production, rising "
        "global defense spending amid geopolitical tensions, platform-life annuity (spares/MRO/upgrade "
        "revenue from a large installed base). "
        "Valid bear risks: order execution delays on complex indigenous programs (a well-documented pattern "
        "in Indian defense manufacturing) pushing out revenue recognition, government budget allocation risk "
        "(defense capex is subject to fiscal/political priorities and can be deferred), single-customer "
        "concentration risk (a policy shift or budget cut at the MoD has outsized impact versus a diversified "
        "industrial customer base), execution/margin risk on first-of-a-kind indigenous platforms, and "
        "working-capital strain from government payment cycles. "
        "LEVERAGE CAVEAT — this sector (especially the PSU names) is typically low-debt, often carrying "
        "near-zero leverage given government-backed order books and advance payments; do NOT default to a "
        "generic 'Leverage Risk' bear headline unless {de} is genuinely elevated (>1.0x) for this sector."
    ),
}
