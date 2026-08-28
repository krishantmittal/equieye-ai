# services/portfolio_store.py
"""
Persistence for watchlist and holdings.

This is the durable replacement for modules/portfolio.py, which kept
everything in st.session_state — meaning a user's watchlist and holdings
were destroyed by a page refresh, a reconnect, or a Streamlit Cloud sleep
cycle. That made both features demos rather than features.

The P&L math is NOT duplicated here: compute_portfolio_stats lives in
services/portfolio_math.py and is imported unchanged, so the stored and
in-memory paths can never disagree. Only the storage changed.

No FastAPI imports — this layer is callable from the API, from Streamlit,
from a script, or from tests.
"""

from __future__ import annotations

from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from core.db import Account, WatchlistItem, Holding
from services.portfolio_math import compute_portfolio_stats


# ── Accounts ──────────────────────────────────────────────────────────────
def create_account(db: Session) -> Account:
    acct = Account(account_key=Account.new_key())
    db.add(acct)
    db.commit()
    db.refresh(acct)
    return acct


def get_account(db: Session, account_key: str) -> Account | None:
    if not account_key:
        return None
    return db.scalar(select(Account).where(Account.account_key == account_key))


def get_or_create_account(db: Session, account_key: str | None) -> Account:
    """Resolve a key to an account, minting a new one when the key is
    absent or unrecognised.

    An unknown key mints a fresh account rather than 404-ing: keys live in
    client storage, which users clear. Erroring would strand them with a
    dead key and no obvious way to recover; issuing a new account lets the
    client store it and carry on. The cost is that a cleared key means the
    old data is unreachable — which is inherent to anonymous accounts and
    the reason real auth is the eventual answer.
    """
    acct = get_account(db, account_key) if account_key else None
    if acct:
        return acct
    return create_account(db)


# ── Watchlist ─────────────────────────────────────────────────────────────
def list_watchlist(db: Session, account: Account) -> list[dict]:
    rows = db.scalars(
        select(WatchlistItem)
        .where(WatchlistItem.account_id == account.id)
        .order_by(WatchlistItem.created_at.desc())
    ).all()
    return [{"ticker": r.ticker, "name": r.name,
             "added_at": r.created_at.isoformat() if r.created_at else None}
            for r in rows]


def add_to_watchlist(db: Session, account: Account, ticker: str, name: str = "") -> bool:
    """Returns True if newly added, False if already present (idempotent —
    the UI toggles this, so a double-click must not create a duplicate)."""
    existing = db.scalar(
        select(WatchlistItem).where(
            WatchlistItem.account_id == account.id,
            WatchlistItem.ticker == ticker,
        )
    )
    if existing:
        if name and not existing.name:
            existing.name = name
            db.commit()
        return False
    db.add(WatchlistItem(account_id=account.id, ticker=ticker, name=name or ""))
    db.commit()
    return True


def remove_from_watchlist(db: Session, account: Account, ticker: str) -> bool:
    result = db.execute(
        delete(WatchlistItem).where(
            WatchlistItem.account_id == account.id,
            WatchlistItem.ticker == ticker,
        )
    )
    db.commit()
    return result.rowcount > 0


# ── Holdings ──────────────────────────────────────────────────────────────
def list_holdings(db: Session, account: Account) -> list[dict]:
    rows = db.scalars(
        select(Holding)
        .where(Holding.account_id == account.id)
        .order_by(Holding.created_at.asc())
    ).all()
    return [{"ticker": r.ticker, "name": r.name, "qty": r.qty,
             "buy_price": r.buy_price, "sector": r.sector}
            for r in rows]


def upsert_holding(db: Session, account: Account, ticker: str, name: str,
                   qty: float, buy_price: float, sector: str = "") -> str:
    """Insert or replace a holding. Returns "created" or "updated".

    Upsert rather than append, matching the original behaviour: one row
    per ticker per account. Adding a stock you already hold edits that
    position instead of creating a second, silently double-counted one.
    """
    existing = db.scalar(
        select(Holding).where(
            Holding.account_id == account.id,
            Holding.ticker == ticker,
        )
    )
    if existing:
        existing.qty = qty
        existing.buy_price = buy_price
        if name:
            existing.name = name
        if sector:
            existing.sector = sector
        db.commit()
        return "updated"
    db.add(Holding(account_id=account.id, ticker=ticker, name=name or "",
                   qty=qty, buy_price=buy_price, sector=sector or ""))
    db.commit()
    return "created"


def remove_holding(db: Session, account: Account, ticker: str) -> bool:
    result = db.execute(
        delete(Holding).where(
            Holding.account_id == account.id,
            Holding.ticker == ticker,
        )
    )
    db.commit()
    return result.rowcount > 0


def portfolio_stats(db: Session, account: Account,
                    live_prices: dict[str, float]) -> dict:
    """P&L and sector allocation. Delegates the arithmetic to the existing
    pure compute_portfolio_stats so the numbers cannot drift between the
    stored and in-memory implementations."""
    return compute_portfolio_stats(list_holdings(db, account), live_prices)
