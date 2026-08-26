# modules/data_caveats.py
"""
Data Caveats — company-specific known data-quality issues
=============================================================
Some companies are going through a corporate action (demerger, major
divestiture, fiscal-year realignment) that makes yfinance's trailing
YoY growth / cash-flow / margin figures genuinely non-comparable for a
period of time — not because the underlying business is weak, but
because the entity itself has changed shape. Scoring engines (health
score, risk meter) have no way to detect this from the numbers alone,
so a real business-quality issue and a temporary restructuring artifact
can look identical in the sub-scores.

This is a small, explicit, human-maintained registry (same pattern as
modules/sectors/conglomerates.py's blended-weight registry) rather than
an attempt to auto-detect restructuring from yfinance data — there's no
reliable signal for "this company demerged a segment last year" in the
data this app has access to.

To add an entry: match on a lowercase substring of the company name,
and write a short, factual note — no editorializing about whether the
stock is a buy, just what changed and why trailing comparisons may be
distorted.
"""

KNOWN_CAVEATS: dict = {
    "siemens": {
        "match": ["siemens limited", "siemens ltd", "siemens india"],
        # Deliberately excludes "siemens energy" so it doesn't also fire on
        # the newly-demerged Siemens Energy India entity, which is a
        # different stock with its own (much cleaner) comparison base.
        "exclude_match": ["siemens energy"],
        "note": (
            "Siemens Limited is mid-restructuring: it demerged its Energy "
            "business into a separate listed entity (Siemens Energy India), "
            "divested its Low Voltage Motors division, and realigned its "
            "fiscal year-end (creating an 18-month stub reporting period "
            "ending March 2026). All three make trailing YoY revenue, "
            "profit-growth, and cash-flow comparisons genuinely "
            "non-comparable right now — the entity being measured today "
            "isn't the same entity as a year ago. Growth and Cash "
            "Generation scores below may understate the standalone "
            "industrial business more than they reflect a real "
            "deterioration; treat them with extra caution until a few "
            "clean post-restructuring quarters are reported."
        ),
    },
}


def get_data_caveat(name: str) -> str | None:
    """Return a known data-quality caveat note for a company name, if any."""
    if not name:
        return None
    name_lower = name.lower()
    for entry in KNOWN_CAVEATS.values():
        if any(ex in name_lower for ex in entry.get("exclude_match", [])):
            continue
        if any(m in name_lower for m in entry["match"]):
            return entry["note"]
    return None
