# modules/sectors/holding_companies.py
"""
Investment Holding Company Registry
====================================
Some listed Indian companies aren't operating businesses at all — they exist
purely to hold equity stakes in other (usually group) listed companies and
pass through the dividend income. JSW Holdings, Bajaj Holdings & Investment,
Tata Investment Corporation, and similar entities fall in this bucket.

WHY THIS NEEDS ITS OWN REGISTRY (not just a sector slug):
Feeding these through the normal sector-detection → health-score → red-flag
pipeline actively produces WRONG output, not just imprecise output:
  - Sector detection has no good slug for "pure holdco" and (confirmed via
    JSW Holdings) falls through to the LLM fallback, which guesses the
    closest-sounding existing sector (e.g. "banking") since none of the
    real sectors fit — inheriting a scoring framework (Asset Quality,
    Capital Adequacy Ratio, NIM) that has nothing to do with the business.
  - "Revenue" for a holdco is dividend income received from its stakes —
    lumpy by nature (timing-dependent on investee companies' dividend
    declarations), so a normal YoY/CAGR-based Red Flag Detector check
    ("negative revenue growth") misfires as a false severity flag.
  - EBITDA/Net margins look absurd (70-95%+) because there's no COGS
    against dividend income — not a sign of exceptional operating
    efficiency, just a category mismatch.
  - AI-generated business descriptions have been observed hallucinating
    the parent GROUP's operating businesses (e.g. "steel, energy,
    cement, automotive, paints" for JSW Holdings) as if they belonged to
    the holdco itself, when it doesn't operate any of them directly.

WHAT THIS REGISTRY DOES: lets app.py detect a known holdco BEFORE running
the normal scoring pipeline, so it can show an honest "this is an
investment holding company" notice instead of a fabricated health score.

UPDATE: now also computes a real Sum-of-the-Parts NAV vs. market-cap
discount for holdcos whose stakes are curated below (see "stakes" and
compute_nav_discount()) — this used to be explicitly out of scope
("deliberately does NOT attempt automatic NAV/discount-to-holdings
valuation"). It's still a genuinely different computation shape from the
rest of this app: every other number here is sourced once from an annual
report and stays fixed until manually refreshed, but NAV needs a LIVE
market-cap fetch for every underlying stake on every page load, since the
whole point is comparing the holdco's price to its stakes' price *today*.

UPDATE 2: added a second category — "hybrid_operating" entries (currently
just Godrej Industries) — for companies that run a real, sizeable operating
business of their own IN ADDITION TO holding meaningful stakes in separately-
listed subsidiaries. These don't get the "not an operating business" notice
(that would be factually wrong), but they still skip the normal LLM
health-score/moat pipeline, since blending the standalone business with
pass-through stake value into one AI summary risks the same double-counting
and confusion this registry exists to avoid — see the "godrej industries"
entry below and its app.py caller for the different (accurate) messaging.

⚠️ Deliberately an EXPLICIT match list, not a name-keyword heuristic (e.g.
"contains 'Holdings'"). A keyword rule risks false positives on legitimate
operating companies that happen to have "Holdings" in their registered name.
An explicit list needs manual upkeep as new holdcos list/delist, same
maintenance tradeoff as CONGLOMERATE_REGISTRY.

⚠️ STAKE DATA IS PARTIAL BY DESIGN, NOT BY OVERSIGHT — every "stakes" list
below is a FLOOR on NAV, not the full picture:
  - Ownership percentages are sourced from the most recent disclosure found
    per entity (see each stake's "source" field) and drift slowly over time
    as promoter entities buy/sell — re-verify periodically, don't treat as
    permanently fixed.
  - Any stake this app couldn't source a confident, current, single number
    for is left OUT rather than guessed — e.g. Bombay Burmah's Bombay Dyeing
    stake (sources conflict: 15.28% vs 44.39% depending on vintage/whether
    subsidiary holdings are included) and JSW Holdings' "other strategic
    investments" (never quantified in any source checked). Excluding these
    means the computed NAV understates the true figure — the discount-to-NAV
    is therefore a LOWER BOUND on how cheap the holdco looks, never an
    overstatement.
  - Unlisted stakes (e.g. Bajaj Holdings' 18.10% of the now-delisted-from-
    Allianz Bajaj General/Life Insurance) are excluded outright — there's no
    market price to mark them against, so they can't enter a market-value NAV
    at all without a private valuation, which this app doesn't attempt.
  - Tata Investment Corporation and Kalyani Investment are registered (so the
    "this is a holdco" notice still fires) but have an EMPTY stakes list —
    Tata Investment Corp alone holds dozens of small stakes across the Tata
    Group (TCS, Titan, Trent, Tata Chemicals, Voltas, Tata Elxsi, Indian
    Hotels, and more), each individually small; curating that properly is a
    bigger, separate data pass, not something to rush with placeholder
    numbers. compute_nav_discount() returns None for these until populated,
    and the caller should keep showing the plain notice in that case.
"""

HOLDING_COMPANY_REGISTRY: dict = {
    "jsw holdings": {
        "match": ["jsw holdings"],
        "holds_stakes_in": "JSW Group listed companies (JSW Steel, JSW Energy, etc.)",
        "stakes": [
            {"name": "JSW Steel", "ticker": "JSWSTEEL.NS", "ownership_pct": 7.42,
             "source": "JSW Holdings company profile, disclosed as of 31-Mar-2025 (most recent found)"},
        ],
        "nav_note": (
            "JSW Holdings also holds unquantified 'other strategic investments in Group "
            "Companies' beyond its JSW Steel stake — NAV below covers JSW Steel only, so "
            "treat it as a floor, not the complete picture."
        ),
    },
    "bajaj holdings": {
        "match": ["bajaj holdings"],
        "holds_stakes_in": "Bajaj Auto and Bajaj Finserv",
        "stakes": [
            {"name": "Bajaj Auto", "ticker": "BAJAJ-AUTO.NS", "ownership_pct": 36.68,
             "source": "5paisa shareholding summary, FY26"},
            {"name": "Bajaj Finserv", "ticker": "BAJAJFINSV.NS", "ownership_pct": 38.41,
             "source": "Block-deal disclosure, 28-Apr-2026 (most recent transactional figure found; "
                        "other sources cite 40-41.5% and may reflect a different date/methodology)"},
        ],
        "nav_note": (
            "Also holds an 18.10% stake (acquired Jan-Mar 2026) in the now Allianz-free Bajaj "
            "General Insurance and Bajaj Life Insurance — excluded from NAV since these are "
            "unlisted with no market price to mark against."
        ),
    },
    "tata investment corporation": {
        "match": ["tata investment corporation"],
        "holds_stakes_in": "various Tata Group listed companies",
        "stakes": [],  # not yet curated — see module docstring
        "nav_note": (
            "Portfolio spans dozens of individually-small Tata Group listed stakes (TCS, Titan, "
            "Trent, Tata Chemicals, Voltas, Tata Elxsi, Indian Hotels, and more) — not yet "
            "curated stake-by-stake, so NAV can't be computed yet."
        ),
    },
    "kalyani investment": {
        "match": ["kalyani investment"],
        "holds_stakes_in": "Kalyani/Bharat Forge Group listed companies",
        "stakes": [],  # not yet curated — see module docstring
        "nav_note": "Stake percentages not yet curated, so NAV can't be computed yet.",
    },
    "bombay burmah": {
        # NOTE: Bombay Burmah Trading Corp is a Wadia Group holding entity
        # with a small standalone tea/plantation operating business too —
        # borderline case, included since its market value is overwhelmingly
        # driven by its Britannia Industries stake, not its own operations.
        "match": ["bombay burmah"],
        "holds_stakes_in": "Britannia Industries (majority of its value) plus a small standalone plantation business",
        "stakes": [
            {"name": "Britannia Industries", "ticker": "BRITANNIA.NS", "ownership_pct": 50.5,
             "source": "Wikipedia / multiple sources, consistently ~50.5-50.75% across recent years"},
        ],
        "nav_note": (
            "Also holds a stake in Bombay Dyeing & Manufacturing — excluded because sources "
            "conflict on the current number (15.28% vs 44.39% depending on vintage and whether "
            "subsidiary holdings are netted in). Britannia alone is reported to represent the "
            "large majority of BBTC's value, so this is a reasonable floor, not a wild understatement."
        ),
    },
    "godrej industries": {
        "match": ["godrej industries"],
        # Unlike every other entry above, this is NOT a pure investment
        # holdco — Godrej Industries runs a genuine, sizeable standalone
        # operating business (oleochemicals) alongside its subsidiary
        # stakes. It was explicitly evaluated and rejected for
        # CONGLOMERATE_REGISTRY (see modules/sectors/conglomerates.py,
        # the Aditya Birla Capital entry's note) because Godrej Consumer
        # Products, Godrej Properties, and Godrej Agrovet are all
        # separately listed and already get their own full analysis on
        # their own tickers elsewhere in this app — blending them into a
        # "Godrej Industries" score would double-count them.
        # Prior to this entry, Godrej Industries had NO shortcut at all
        # and ran the full LLM pipeline (moat verdict + combined
        # snapshot/bull/bear, with a real chance of hitting the JSON
        # retry path given how hard it is for a model to describe a
        # hybrid chemicals-manufacturer-plus-investment-vehicle identity
        # concisely) — several Groq calls for a single ticker, on top of
        # whatever the sibling tickers (GCPL/Properties/Agrovet) cost
        # when checked separately in the same session.
        # "hybrid_operating": True signals app.py to show a DIFFERENT
        # message than the pure-holdco notice below (it's factually wrong
        # to tell someone "this is not an operating business" when it
        # manufactures fatty acids/alcohols/surfactants at real plants),
        # while still skipping the expensive LLM analysis, since the
        # subsidiary-stake portion of its value is already covered
        # elsewhere and blending it with the chemicals business into one
        # AI-written summary risks the same confusion this entry exists
        # to avoid.
        "hybrid_operating": True,
        "operating_business": (
            "one of the world's largest standalone oleochemicals manufacturers — fatty acids, "
            "fatty alcohols, surfactants, and glycerine, used as inputs for home/personal care, "
            "pharma, and food industries — a real, sizeable operating business, not a shell"
        ),
        "holds_stakes_in": "Godrej Consumer Products, Godrej Properties, and Godrej Agrovet",
        "stakes": [
            {"name": "Godrej Consumer Products", "ticker": "GODREJCP.NS", "ownership_pct": 23.7,
             "source": "Godrej Industries FY26 (year ended Mar-2026) results coverage, May-2026"},
            {"name": "Godrej Properties", "ticker": "GODREJPROP.NS", "ownership_pct": 44.8,
             "source": "Godrej Industries FY26 results coverage, May-2026 — NOTE: a Jun-2026 "
                        "Business Standard report on the Godrej family settlement structure cites "
                        "47.3% instead; sources conflict on vintage/methodology, re-verify against "
                        "the latest shareholding pattern if precision matters"},
            {"name": "Godrej Agrovet", "ticker": "GODREJAGRO.NS", "ownership_pct": 64.9,
             "source": "Business Standard, Jun-2026, on the Godrej family settlement structure"},
        ],
        "nav_note": (
            "Unlike every other holdco in this registry, Godrej Industries also runs a real, "
            "sizeable operating business (oleochemicals) alongside these three stakes — so the "
            "NAV below covers ONLY the listed subsidiary stakes, not the chemicals business. "
            "Comparing that stakes-only NAV to Godrej Industries' FULL market cap is therefore "
            "NOT a clean discount/premium read the way it is for a pure holdco like JSW Holdings "
            "or Bajaj Holdings — some of any gap between the two also reflects the market's own "
            "standalone valuation of the chemicals business, not purely holdco-structure "
            "discounting. Treat the number as directional, not a precise NAV discount."
        ),
    },
}


def get_holding_company_match(company_name: str) -> dict | None:
    """Return the registry entry for company_name, or None if it isn't a
    known pure investment holding company."""
    if not company_name:
        return None
    name_lower = company_name.lower()
    for entry in HOLDING_COMPANY_REGISTRY.values():
        if any(pat in name_lower for pat in entry["match"]):
            return entry
    return None


def compute_nav_discount(entry: dict, holdco_market_cap: float, fetch_market_cap_fn) -> dict | None:
    """Sum-of-the-Parts NAV vs. market-cap discount for an already-matched
    holding company registry entry (i.e. call get_holding_company_match()
    first and pass its result in here).

    entry              : a HOLDING_COMPANY_REGISTRY value (from get_holding_company_match)
    holdco_market_cap  : the holdco's OWN current market cap, in the same
                          currency unit fetch_market_cap_fn returns (Rupees)
    fetch_market_cap_fn: callable(ticker: str) -> float | None — deliberately
                          injected rather than importing yfinance directly
                          here, so this module has no direct dependency on
                          app.py's caching/retry layer. Pass in something
                          built on the existing fetch_stock() in app.py so
                          stake prices benefit from the same 5-min cache and
                          Yahoo-throttling retry logic already in place.

    Returns None if:
      - entry has no curated stakes yet (e.g. Tata Investment Corp, Kalyani) —
        caller should fall back to the plain "this is a holdco" notice.
      - holdco_market_cap is missing/zero.
      - every stake's live market cap fetch fails.

    Returns a dict:
      {
        "nav": float,               # sum of (ownership % x subsidiary market cap)
        "holdco_market_cap": float,
        "discount_pct": float,      # positive = trades BELOW NAV (the normal case)
        "stake_details": [ {"name", "ticker", "ownership_pct", "market_cap",
                             "stake_value"} , ... for stakes that resolved ],
        "unresolved_stakes": [ names that failed to fetch, if any ],
      }
    """
    stakes = entry.get("stakes") or []
    if not stakes or not holdco_market_cap:
        return None

    nav = 0.0
    stake_details = []
    unresolved = []
    for stake in stakes:
        sub_mcap = fetch_market_cap_fn(stake["ticker"])
        if not sub_mcap:
            unresolved.append(stake["name"])
            continue
        stake_value = sub_mcap * (stake["ownership_pct"] / 100.0)
        nav += stake_value
        stake_details.append({
            "name": stake["name"],
            "ticker": stake["ticker"],
            "ownership_pct": stake["ownership_pct"],
            "market_cap": sub_mcap,
            "stake_value": stake_value,
        })

    if not stake_details:
        return None

    discount_pct = (nav - holdco_market_cap) / nav * 100.0 if nav > 0 else None

    return {
        "nav": nav,
        "holdco_market_cap": holdco_market_cap,
        "discount_pct": discount_pct,
        "stake_details": stake_details,
        "unresolved_stakes": unresolved,
    }
