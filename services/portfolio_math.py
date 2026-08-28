# services/portfolio_math.py
"""
Portfolio P&L and allocation arithmetic.

Moved out of modules/portfolio.py, which imports Streamlit at module
level for its session_state CRUD helpers. That top-level import meant any
backend module reaching this pure function dragged the whole Streamlit
runtime into the FastAPI process — a heavy dependency the API has no use
for, and one that would have to be installed on the API host.

The function itself is unchanged. modules/portfolio.py re-exports it, so
the Streamlit app's existing import keeps working.
"""

from __future__ import annotations


def compute_portfolio_stats(holdings: list[dict], live_prices: dict[str, float]) -> dict:
    """
    Compute portfolio P&L and allocation from holdings + live prices.

    live_prices: {ticker: current_price}. A ticker absent from this dict
    is valued at cost with zero P&L rather than being dropped — a failed
    quote must not silently shrink the portfolio's total value, which
    would misreport performance. Callers should surface which tickers were
    unpriced (the API returns them as `stale_tickers`).

    Returns:
      total_invested, current_value, total_pnl, total_pnl_pct,
      holdings_with_stats (list), sector_allocation (dict)
    """
    total_invested = 0
    current_value = 0
    sector_map: dict[str, float] = {}
    holdings_with_stats = []

    for h in holdings:
        ticker = h["ticker"]
        qty = h["qty"]
        buy_price = h["buy_price"]
        sector = h.get("sector") or "Unknown"
        cur_price = live_prices.get(ticker)

        invested = qty * buy_price
        total_invested += invested

        if cur_price is not None:
            cur_val = qty * cur_price
            pnl = cur_val - invested
            pnl_pct = (pnl / invested * 100) if invested else 0
            current_value += cur_val
        else:
            cur_val = invested   # value at cost — see docstring
            pnl = 0
            pnl_pct = 0
            current_value += cur_val

        sector_map[sector] = sector_map.get(sector, 0) + cur_val

        holdings_with_stats.append({
            **h,
            "current_price": cur_price,
            "current_value": cur_val,
            "invested": invested,
            "pnl": pnl,
            "pnl_pct": pnl_pct,
        })

    total_pnl = current_value - total_invested
    total_pnl_pct = (total_pnl / total_invested * 100) if total_invested else 0

    sector_allocation = {}
    if current_value > 0:
        for sec, val in sector_map.items():
            sector_allocation[sec] = round(val / current_value * 100, 1)

    return {
        "total_invested": round(total_invested, 2),
        "current_value": round(current_value, 2),
        "total_pnl": round(total_pnl, 2),
        "total_pnl_pct": round(total_pnl_pct, 2),
        "holdings_with_stats": holdings_with_stats,
        "sector_allocation": sector_allocation,
    }
