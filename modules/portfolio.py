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


# compute_portfolio_stats now lives in services/portfolio_math.py so the
# FastAPI backend can use it without importing Streamlit (this module's
# session_state CRUD helpers above require it). Re-exported here so the
# Streamlit app's existing `from modules.portfolio import
# compute_portfolio_stats` keeps working unchanged.
from services.portfolio_math import compute_portfolio_stats  # noqa: E402,F401
