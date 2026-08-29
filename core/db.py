# core/db.py
"""
Database setup and ORM models for user-scoped data (watchlist, holdings).

Storage engine is chosen by DATABASE_URL:
  unset                     -> SQLite file at ./data/equieye.db (local dev)
  postgresql://...          -> Postgres (production)

SQLAlchemy is used rather than raw SQL specifically so that swap is a
config change. Note SQLite is NOT suitable for the deployed backend —
most PaaS filesystems are ephemeral, so a SQLite file is wiped on every
redeploy, which is the exact failure mode this feature exists to fix.

── Identity ──────────────────────────────────────────────────────────────
An Account is addressed by an opaque `account_key` the client stores and
sends as the X-Account-Key header. This gives working persistence with no
signup friction, and upgrades cleanly: adding real auth means attaching
auth_provider/auth_subject to the SAME account rows, so a user who signs
up later keeps everything they already saved instead of having their data
migrated (or lost).

The key is a 32-byte URL-safe token from `secrets` — it is a bearer
credential, so it must be unguessable, and anyone holding it can read and
write that account's data. That is an acceptable trade for anonymous
convenience but it is NOT a substitute for authentication: do not put
anything sensitive behind it, and move to real auth before storing
anything a user would be harmed by leaking.
"""

from __future__ import annotations
import os
import secrets
from datetime import datetime, timezone

from sqlalchemy import (
    create_engine, String, Float, DateTime, ForeignKey, UniqueConstraint, Index,
)
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker, Session,
)

from core.config import get_secret


def _database_url() -> str:
    url = get_secret("DATABASE_URL")
    if url:
        # Two separate normalisations, both required:
        #
        # 1. Several hosts (Heroku lineage, and some Neon/Supabase copy
        #    buttons) still hand out `postgres://`, which SQLAlchemy 2.x
        #    refuses to parse at all.
        #
        # 2. Bare `postgresql://` resolves to the psycopg2 driver, but this
        #    project installs psycopg 3 (see requirements-backend.txt), so
        #    it would fail at import with "No module named 'psycopg2'" —
        #    at engine construction, i.e. on boot, not on first query.
        #    Pinning the +psycopg suffix selects the driver actually
        #    installed. Verified: without this, a real Neon URL crashes the
        #    service on startup.
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+psycopg://", 1)
        return url
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(root, "data")
    os.makedirs(data_dir, exist_ok=True)
    return f"sqlite:///{os.path.join(data_dir, 'equieye.db')}"


DATABASE_URL = _database_url()
_IS_SQLITE = DATABASE_URL.startswith("sqlite")

engine = create_engine(
    DATABASE_URL,
    # SQLite's default guard rejects use from any thread but the creating
    # one. FastAPI runs sync endpoints in a threadpool, so that guard would
    # reject nearly every request. Safe here because each request gets its
    # own short-lived Session.
    connect_args={"check_same_thread": False} if _IS_SQLITE else {},
    pool_pre_ping=True,   # drop connections killed by an idle timeout
    future=True,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    account_key: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    watchlist: Mapped[list["WatchlistItem"]] = relationship(
        back_populates="account", cascade="all, delete-orphan")
    holdings: Mapped[list["Holding"]] = relationship(
        back_populates="account", cascade="all, delete-orphan")

    @staticmethod
    def new_key() -> str:
        return secrets.token_urlsafe(32)


class WatchlistItem(Base):
    __tablename__ = "watchlist_items"
    # One row per (account, ticker): adding a stock already on the list is
    # an idempotent no-op, not a duplicate row.
    __table_args__ = (
        UniqueConstraint("account_id", "ticker", name="uq_watchlist_account_ticker"),
        Index("ix_watchlist_account", "account_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"))
    ticker: Mapped[str] = mapped_column(String(32))
    name: Mapped[str] = mapped_column(String(256), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    account: Mapped[Account] = relationship(back_populates="watchlist")


class Holding(Base):
    __tablename__ = "holdings"
    __table_args__ = (
        UniqueConstraint("account_id", "ticker", name="uq_holding_account_ticker"),
        Index("ix_holding_account", "account_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"))
    ticker: Mapped[str] = mapped_column(String(32))
    name: Mapped[str] = mapped_column(String(256), default="")
    # Float, not Decimal: these are user-entered quantities and cost basis
    # for a research tool's P&L display, not ledger entries. If EquiEye
    # ever books real transactions this must become Numeric — float
    # rounding is not acceptable for money that has to reconcile.
    qty: Mapped[float] = mapped_column(Float)
    buy_price: Mapped[float] = mapped_column(Float)
    sector: Mapped[str] = mapped_column(String(128), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)

    account: Mapped[Account] = relationship(back_populates="holdings")


def init_db() -> None:
    """Create tables if absent.

    Fine for a single-service schema this small; a real migration tool
    (Alembic) becomes necessary as soon as a column has to change on a
    table that already holds production rows, since create_all only ever
    adds missing tables — it will not alter existing ones.
    """
    Base.metadata.create_all(engine)


def get_session() -> Session:
    return SessionLocal()
