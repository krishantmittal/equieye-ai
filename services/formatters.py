# services/formatters.py
"""
Pure display-value formatters. Extracted from app.py's fmt_crore() /
pct() / fmt_de() / get_pe_bands() verbatim — none of these ever had a
Streamlit dependency in the first place.
"""

from __future__ import annotations
import math

try:
    from modules.health_score import get_pe_bands as _get_pe_bands_module
except Exception:
    _get_pe_bands_module = None


def fmt_crore(val):
    if val is None:
        return "N/A"
    try:
        val = float(val)
    except (TypeError, ValueError):
        return "N/A"
    # After converting to float, check for NaN/Inf — covers float('nan'),
    # np.nan, and pandas NA (all become float NaN after float() conversion).
    if not math.isfinite(val):
        return "N/A"
    if val < 0:
        crore_neg = abs(val) / 1e7
        return f"-₹{crore_neg:,.0f} Cr"
    crore = val / 1e7
    if crore >= 1_00_000:
        return f"₹{crore/1_00_000:.2f} Lakh Cr"
    if crore >= 1000:
        return f"₹{crore/1000:.1f}K Cr"
    return f"₹{crore:.0f} Cr"


def pct(a, b):
    # Explicit None checks instead of truthiness — price of 0 is valid (though rare)
    if a is not None and b is not None and b != 0:
        return ((a - b) / abs(b)) * 100
    return None


def fmt_de(de_raw):
    """Format yfinance's percentage-form debtToEquity as an 'x' ratio.
    A raw value between 0 and 0.5 rounds to a flat '0.00x' at 2 decimals,
    which reads as literally zero debt rather than near-zero — shows 3
    decimals in that band instead so 'near debt-free' isn't misrepresented
    as 'debt-free'."""
    if de_raw is None:
        return "N/A"
    val = de_raw / 100
    if val == 0:
        return "0.00x"
    if abs(val) < 0.005:
        return f"{val:.3f}x"
    return f"{val:.2f}x"


def get_pe_bands(sector: str, industry: str, slug: str | None = None):
    """Sector-aware P/E bands. Delegates to modules.health_score's
    get_pe_bands (single source of truth) when available, falling back to
    generic bands so this still works standalone if modules/ is absent."""
    if _get_pe_bands_module is not None:
        return _get_pe_bands_module(sector, industry, slug=slug)
    _FALLBACK_BANDS = {
        "Technology": (20, 50), "Financial Services": (12, 30),
        "Healthcare": (25, 60), "Consumer Cyclical": (20, 45),
        "Consumer Defensive": (25, 50), "Energy": (10, 25),
        "Utilities": (12, 25), "Industrials": (18, 40),
        "Basic Materials": (12, 28), "Real Estate": (20, 40),
        "Communication Services": (18, 45),
    }
    return _FALLBACK_BANDS.get(sector, (15, 35))
