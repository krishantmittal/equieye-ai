# services/verdict.py
"""
Health-score verdict text generation. Extracted from app.py's
_build_smart_verdict() / _outlook_looks_truncated() verbatim — pure
string logic, no Streamlit dependency.
"""

from __future__ import annotations
import re

_TRUNCATION_PATTERNS = [
    r"\blabel\s+competition\b",
    r"\b(and|or|but|with|for|of|in|on|to|the|a|an)\s*[.!?]?\s*$",
    r",\s*$",
]


def build_smart_verdict(score, weights_list):
    """
    Returns a one-line health verdict that calls out divergent sub-scores.
    Never says 'strong' when any pillar is flagged weak (< 5).

    Valuation is deliberately kept OUT of the weak/strong fundamentals list
    below and reported as a separate clause instead. A company with
    genuinely fine business fundamentals but a very rich multiple
    (Valuation score near 0) shouldn't have that 0 lumped in alongside
    real quality pillars in a single "significant concerns in
    Profitability & Growth & ... & Valuation" sentence — reading as "this
    is a weak business" when the correct read is "this is a business
    trading at a demanding price." Those are different problems for an
    investor and shouldn't be worded identically.
    """
    fundamentals = [(lbl, s, w) for lbl, s, w in weights_list if lbl != "Valuation" and s is not None]
    _val_entry = next(((lbl, s, w) for lbl, s, w in weights_list if lbl == "Valuation" and s is not None), None)
    val_score = _val_entry[1] if _val_entry else None
    val_clause = (
        "; trading at a very rich valuation" if val_score is not None and val_score < 3 else
        "; valuation looks stretched" if val_score is not None and val_score < 5 else
        "; valuation looks reasonable" if val_score is not None and val_score >= 7 else
        ""
    )

    if not fundamentals:
        return "Insufficient data for a full assessment."
    weak   = [lbl for lbl, s, _ in fundamentals if s < 5.0]
    strong = [lbl for lbl, s, _ in fundamentals if s >= 7.0]
    if score >= 8.5 and not weak:
        return f"Excellent fundamentals across all dimensions{val_clause}."
    if score >= 7 and not weak:
        return f"Strong financial health — solid across most metrics{val_clause}."
    if score >= 5:
        if weak:
            weak_str = " & ".join(weak)
            if strong:
                strong_str = " & ".join(strong)
                return f"Mixed profile — strong {strong_str} offset by weak {weak_str}{val_clause}."
            return f"Average overall — watch {weak_str}, which is below par{val_clause}."
        if strong:
            # No weak fundamentals pillar, but the blended score still landed
            # in the average band — that's valuation pulling it down, not the
            # business. Credit the strong fundamentals explicitly rather than
            # defaulting to a flat "average" read.
            strong_str = " & ".join(strong)
            return f"Strong {strong_str} fundamentals{val_clause}."
        return f"Average — mixed signals, monitor key metrics{val_clause}."
    if score >= 3:
        if strong and not weak:
            # Fundamentals pillars are actually fine (>=5, some >=7) — a low
            # blended score here is being driven by valuation, not by the
            # underlying business. Say so plainly instead of "weak fundamentals".
            strong_str = " & ".join(strong)
            return f"Solid underlying business (strong {strong_str}){val_clause or ', but the blended score is dragged down by valuation'}."
        if weak:
            weak_str = " & ".join(weak)
            return f"Significant concerns in {weak_str}{val_clause}."
        return f"Weak fundamentals — significant concerns{val_clause}."
    return f"Distressed — poor health across most dimensions{val_clause}."


def outlook_looks_truncated(text: str) -> bool:
    if not text:
        return True
    t = text.strip()
    if len(t.split()) < 12:
        return True
    return any(re.search(pat, t, re.IGNORECASE) for pat in _TRUNCATION_PATTERNS)
