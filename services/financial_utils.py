# services/financial_utils.py
"""
Financial-statement cleaning helpers. Extracted from app.py's
_is_quarterly_financials() / _trim_to_last_discontinuity() verbatim —
pure pandas logic, no Streamlit dependency.
"""

from __future__ import annotations


def is_quarterly_financials(fin) -> bool:
    """
    True if `fin`'s statement columns are spaced like quarters (~90 days)
    rather than years (~365 days) — i.e. a fetch_stock-style fin/
    quarterly_fin fallback actually returned quarterly data for this ticker.

    Uses the MEDIAN gap across ALL adjacent column pairs, not just the
    most recent pair. Checking only the last gap is fragile: a single
    irregular stub/partial reporting period — e.g. a newly-demerged
    entity's first "annual" column covering a truncated transition
    window (see TMPV.NS, demerged October 2025) — can be <180 days
    after the prior column even though the rest of the series is
    genuinely annual. The median is robust to that one-off irregularity
    where the last-pair-only check is not.
    """
    if fin is None or fin.empty or fin.shape[1] < 2:
        return False
    cols_sorted = sorted(fin.columns)
    gaps = []
    for i in range(1, len(cols_sorted)):
        try:
            gaps.append((cols_sorted[i] - cols_sorted[i - 1]).days)
        except Exception:
            continue
    if not gaps:
        return False
    gaps.sort()
    median_gap = gaps[len(gaps) // 2]
    return median_gap < 180


def trim_to_last_discontinuity(series, drop_threshold=0.5, jump_threshold=3.0):
    """
    Detects an implausible single-period swing in a financials row —
    e.g. revenue dropping >50% or jumping >3x from one statement column
    to the next. This is the signature of a corporate action (demerger,
    spinoff, major divestiture/acquisition) rather than organic
    performance: yfinance/most data providers stitch a newly-listed
    entity's post-split financials onto its former parent's pre-split
    history under one ticker (e.g. TMCV.NS showing the full pre-demerger
    Tata Motors group's ~₹4.3L Cr FY24 revenue, then the standalone CV-
    only entity's ~₹58K Cr FY25 revenue, as if it were one continuous
    company). Computing a CAGR across that break doesn't measure growth
    or decline at all — it measures the size difference between two
    different corporate entities.

    Returns (trimmed_series, discontinuity_found). If found, only the
    most recent contiguous segment after the last detected break is
    kept, so CAGR/YoY are computed on genuinely comparable periods only
    — or left honestly None if that leaves too few data points.
    """
    if series is None or len(series) < 2:
        return series, False
    vals = series.values
    break_idx = None
    for i in range(1, len(vals)):
        prev_v, cur_v = vals[i - 1], vals[i]
        if prev_v is None or prev_v == 0:
            continue
        try:
            ratio = cur_v / prev_v
        except Exception:
            continue
        if ratio <= (1 - drop_threshold) or ratio >= jump_threshold:
            break_idx = i   # keep scanning — use the LAST break found
    if break_idx is None:
        return series, False
    return series.iloc[break_idx:], True
