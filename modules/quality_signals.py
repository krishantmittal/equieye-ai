# modules/quality_signals.py
"""
Phase 1 institutional-analyst signals.
Implements the first, fully-data-available slice of the analyst spec:
  - Cyclical sector detection
  - Turnaround-company detection (loss→profit swings, growth off a
    depressed base, aggressive debt paydown)
  - 5-tier sector-relative valuation buckets

All of this is computed from data the app already fetches (yfinance
`financials` / `balance_sheet`, plus the existing sector-relative
Valuation pillar score). No new API calls or data sources required.

Explicitly out of scope here (needs data yfinance doesn't provide —
promoter pledging, customer concentration, buyback history, governance
records): see the Phase 2/3 discussion in chat. Nothing in this module
fabricates a signal for data that isn't actually available.
"""
from __future__ import annotations

_CYCLICAL_KEYWORDS = [
    "steel", "cement", "shipping", "wind", "power equipment",
    "metal", "mining", "chemical", "auto part", "auto ancillary",
    "commodity", "shipbuilding", "sugar", "textile", "paper",
]
_CYCLICAL_SLUGS = {"metals_mining"}


def detect_cyclical(sector_slug: str, industry: str) -> bool:
    """True if the company sits in a structurally cyclical industry —
    earnings/margins swing hard with commodity or capex cycles, so a
    few strong years shouldn't be read as durable compounding."""
    if sector_slug in _CYCLICAL_SLUGS:
        return True
    industry_l = (industry or "").lower()
    return any(kw in industry_l for kw in _CYCLICAL_KEYWORDS)


def _series_from_df(df, row_keys):
    """Pull the first matching row from a yfinance financials/balance_sheet
    DataFrame as a sorted (oldest→newest), NaN-dropped Series. Returns None
    if the frame is empty/missing or fewer than 2 data points are available
    — turnaround detection needs at least an old-vs-new comparison."""
    if df is None or getattr(df, "empty", True):
        return None
    for key in row_keys:
        if key in df.index:
            s = df.loc[key].dropna().sort_index()
            if len(s) >= 2:
                return s
    return None


def detect_turnaround(fin, bs, revenue_cagr: float | None = None) -> dict | None:
    """
    Flags a company as a "turnaround" — current growth/profitability is
    partly a recovery from a depressed base rather than durable multi-year
    compounding — using only the multi-year financials/balance-sheet data
    already fetched elsewhere in the app (no new API calls).

    Detection conditions (any one triggers it):
      - Net income was negative in an earlier reported year but is
        positive in the most recent year (loss → profit swing)
      - Revenue CAGR > 20% AND a loss occurred somewhere in the reported
        window (fast growth off a depressed base, not pure compounding)
      - Total debt has fallen >40% across the reported window
        (balance-sheet repair, often post-distress)

    Returns None if no turnaround signal is found, else:
      {"is_turnaround": True, "reasons": [str, ...]}
    """
    reasons: list[str] = []
    had_loss = False

    ni_series = _series_from_df(
        fin,
        ["Net Income", "Net Income Common Stockholders",
         "Net Income From Continuing Operations",
         "Net Income Including Noncontrolling Interests"],
    )
    if ni_series is not None:
        had_loss = bool((ni_series.iloc[:-1] < 0).any())
        now_profit = float(ni_series.iloc[-1]) > 0
        if had_loss and now_profit:
            reasons.append(
                "Net income swung from a loss in an earlier reported year to a profit "
                "in the most recent year — a recovery pattern, not multi-year compounding."
            )

    if revenue_cagr is not None and revenue_cagr > 20 and had_loss:
        reasons.append(
            f"Revenue CAGR of {revenue_cagr:.0f}% is partly inflated by growth off a "
            "depressed, loss-making base rather than pure organic compounding."
        )

    debt_series = _series_from_df(
        bs, ["Total Debt", "Long Term Debt", "Long Term Debt And Capital Lease Obligation"]
    )
    if debt_series is not None:
        oldest, newest = float(debt_series.iloc[0]), float(debt_series.iloc[-1])
        debt_fell_sharply = oldest > 0 and (newest - oldest) / oldest < -0.4
        # Debt reduction alone isn't a turnaround signal — a highly profitable,
        # well-run compounder paying down debt from strong cash flow looks
        # identical on this one metric to a company deleveraging out of
        # distress. Only treat it as a turnaround signal when it's
        # corroborated by an actual loss or unusually fast (possibly
        # low-base) growth — otherwise it's just good capital discipline.
        high_growth = revenue_cagr is not None and revenue_cagr > 20
        if debt_fell_sharply and (had_loss or high_growth):
            reasons.append(
                "Total debt has fallen by more than 40% across the reported window, "
                "alongside a recent loss or unusually fast growth — consistent with "
                "balance-sheet repair following financial distress."
            )

    if not reasons:
        return None
    return {"is_turnaround": True, "reasons": reasons}


# (min_score_inclusive, label, color)
_VALUATION_BUCKETS = [
    (8.5, "Inexpensive / Potentially Undervalued", "#16A34A"),
    (6.5, "Cheap", "#22C55E"),
    (4.0, "Fair", "#F59E0B"),
    (2.0, "Expensive", "#F97316"),
    (0.0, "Very Expensive", "#EF4444"),
]


def valuation_bucket(score: float | None) -> tuple[str, str]:
    """Map a 0-10 Valuation pillar score to a 5-tier sector-relative label.
    Returns (label, color_hex). The underlying score is already sector-
    relative (scored against each sector's own PE/P-B/EV-EBITDA/P-S bands),
    so this is a finer-grained readout of that number, not a new calc."""
    if score is None:
        return "Unknown", "#6B7280"
    for threshold, label, color in _VALUATION_BUCKETS:
        if score >= threshold:
            return label, color
    return "Very Expensive", "#EF4444"
