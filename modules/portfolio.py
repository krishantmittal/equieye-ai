"""
modules/portfolio.py
--------------------
Portfolio tracker helpers for EquiEye AI.

Handles:
- Holdings management (add/remove)
- P&L calculation
- Sector exposure
- Portfolio health score
"""

from __future__ import annotations
import streamlit as st


def init_portfolio():
    """Initialize portfolio in session state."""
    if "portfolio_holdings" not in st.session_state:
        st.session_state.portfolio_holdings = []
        # Each holding: {ticker, name, qty, buy_price, sector}


def add_holding(ticker: str, name: str, qty: float, buy_price: float, sector: str = ""):
    init_portfolio()
    # Remove existing if same ticker
    st.session_state.portfolio_holdings = [
        h for h in st.session_state.portfolio_holdings if h["ticker"] != ticker
    ]
    st.session_state.portfolio_holdings.append({
        "ticker": ticker,
        "name": name,
        "qty": qty,
        "buy_price": buy_price,
        "sector": sector,
    })


def remove_holding(ticker: str):
    init_portfolio()
    st.session_state.portfolio_holdings = [
        h for h in st.session_state.portfolio_holdings if h["ticker"] != ticker
    ]


def update_holding(ticker: str, qty: float, buy_price: float):
    """Update qty and buy_price for an existing holding in-place."""
    init_portfolio()
    for h in st.session_state.portfolio_holdings:
        if h["ticker"] == ticker:
            h["qty"] = qty
            h["buy_price"] = buy_price
            break


def get_holdings():
    init_portfolio()
    return st.session_state.portfolio_holdings


def compute_portfolio_stats(holdings: list[dict], live_prices: dict[str, float]) -> dict:
    """
    Compute portfolio P&L and allocation from holdings + live prices.

    live_prices: {ticker: current_price}

    Returns:
      total_invested, current_value, total_pnl, total_pnl_pct,
      holdings_with_stats (list), sector_allocation (dict)
    """
    total_invested = 0
    current_value  = 0
    sector_map: dict[str, float] = {}
    holdings_with_stats = []

    for h in holdings:
        ticker    = h["ticker"]
        qty       = h["qty"]
        buy_price = h["buy_price"]
        sector    = h.get("sector", "Unknown")
        cur_price = live_prices.get(ticker)

        invested = qty * buy_price
        total_invested += invested

        if cur_price is not None:
            cur_val = qty * cur_price
            pnl     = cur_val - invested
            pnl_pct = (pnl / invested * 100) if invested else 0
            current_value += cur_val
        else:
            cur_val = invested  # assume no change
            pnl     = 0
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

    total_pnl     = current_value - total_invested
    total_pnl_pct = (total_pnl / total_invested * 100) if total_invested else 0

    # Convert sector_map to percentages
    sector_allocation = {}
    if current_value > 0:
        for sec, val in sector_map.items():
            sector_allocation[sec] = round(val / current_value * 100, 1)

    return {
        "total_invested":    round(total_invested, 2),
        "current_value":     round(current_value, 2),
        "total_pnl":         round(total_pnl, 2),
        "total_pnl_pct":     round(total_pnl_pct, 2),
        "holdings_with_stats": holdings_with_stats,
        "sector_allocation": sector_allocation,
    }
