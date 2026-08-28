# api/routers/account.py
"""
Watchlist and portfolio — the durable, user-scoped endpoints.

Identity comes from the X-Account-Key header (see core/db.Account for why
an anonymous key rather than full auth, and how it upgrades). Every
response echoes the resolved key in `account_key` so a client that sent
none — or a stale one — can store the newly minted key and keep going.
"""

from __future__ import annotations
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Body
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from core.db import get_session, Account
from api.deps import cached_quote
from services import portfolio_store as store

router = APIRouter()


def db_session():
    db = get_session()
    try:
        yield db
    finally:
        db.close()


def resolve_account(
    db: Annotated[Session, Depends(db_session)],
    x_account_key: Annotated[str | None, Header()] = None,
) -> tuple[Session, Account]:
    return db, store.get_or_create_account(db, x_account_key)


AccountDep = Annotated[tuple[Session, Account], Depends(resolve_account)]


@router.post("/account")
def create_account(db: Annotated[Session, Depends(db_session)]):
    """Mint a fresh anonymous account. Clients normally don't need this —
    any endpoint mints one when the header is missing — but it's useful
    for provisioning a key up front."""
    acct = store.create_account(db)
    return {"account_key": acct.account_key,
            "created_at": acct.created_at.isoformat() if acct.created_at else None}


# ── Watchlist ─────────────────────────────────────────────────────────────
class WatchlistAdd(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=32)
    name: str = Field("", max_length=256)


@router.get("/watchlist")
def get_watchlist(ctx: AccountDep, live: bool = True):
    """The saved watchlist, with live quotes attached by default.

    A quote failure degrades that row to price:null rather than failing
    the request — yfinance is flaky enough that one bad ticker must not
    take down the whole list.
    """
    db, acct = ctx
    items = store.list_watchlist(db, acct)
    if live:
        for it in items:
            try:
                info = cached_quote(it["ticker"])
                price = info.get("currentPrice") or info.get("regularMarketPrice")
                prev = info.get("previousClose")
                it["price"] = price
                it["change_pct"] = (
                    ((price - prev) / abs(prev) * 100)
                    if price is not None and prev else None
                )
                it["market_cap"] = info.get("marketCap")
            except Exception:
                it["price"] = it["change_pct"] = it["market_cap"] = None
    return {"account_key": acct.account_key, "count": len(items), "items": items}


@router.post("/watchlist")
def add_watchlist(ctx: AccountDep, body: WatchlistAdd = Body(...)):
    db, acct = ctx
    added = store.add_to_watchlist(db, acct, body.ticker.strip(), body.name.strip())
    return {"account_key": acct.account_key, "ticker": body.ticker,
            "added": added, "already_present": not added}


@router.delete("/watchlist/{ticker}")
def delete_watchlist(ctx: AccountDep, ticker: str):
    db, acct = ctx
    removed = store.remove_from_watchlist(db, acct, ticker)
    if not removed:
        raise HTTPException(404, f"{ticker} is not on this watchlist.")
    return {"account_key": acct.account_key, "ticker": ticker, "removed": True}


# ── Portfolio ─────────────────────────────────────────────────────────────
class HoldingIn(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=32)
    name: str = Field("", max_length=256)
    # gt=0 rather than ge=0: a zero-quantity holding is meaningless and
    # would divide by zero in the P&L percentage.
    qty: float = Field(..., gt=0)
    buy_price: float = Field(..., gt=0)
    sector: str = Field("", max_length=128)


@router.get("/portfolio")
def get_portfolio(ctx: AccountDep):
    """Holdings with P&L, computed against live prices.

    Tickers whose quote fails are reported in `stale` and are valued at
    cost by compute_portfolio_stats — so the totals stay arithmetically
    sound while making it explicit which rows aren't actually live.
    """
    db, acct = ctx
    holdings = store.list_holdings(db, acct)

    prices: dict[str, float] = {}
    stale: list[str] = []
    for h in holdings:
        try:
            info = cached_quote(h["ticker"])
            p = info.get("currentPrice") or info.get("regularMarketPrice")
            if p is not None:
                prices[h["ticker"]] = p
            else:
                stale.append(h["ticker"])
        except Exception:
            stale.append(h["ticker"])

    stats = store.portfolio_stats(db, acct, prices)
    return {"account_key": acct.account_key, "count": len(holdings),
            "stale_tickers": stale, **stats}


@router.post("/portfolio")
def add_holding(ctx: AccountDep, body: HoldingIn = Body(...)):
    """Add or replace a holding (upsert on ticker)."""
    db, acct = ctx
    action = store.upsert_holding(
        db, acct, body.ticker.strip(), body.name.strip(),
        body.qty, body.buy_price, body.sector.strip(),
    )
    return {"account_key": acct.account_key, "ticker": body.ticker, "action": action}


@router.delete("/portfolio/{ticker}")
def delete_holding(ctx: AccountDep, ticker: str):
    db, acct = ctx
    removed = store.remove_holding(db, acct, ticker)
    if not removed:
        raise HTTPException(404, f"{ticker} is not in this portfolio.")
    return {"account_key": acct.account_key, "ticker": ticker, "removed": True}
