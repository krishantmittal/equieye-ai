# modules/sector_analysis.py
"""
Sector Analysis — Core Integration Layer
=========================================
Public API consumed by app.py (signatures preserved exactly):

    classify_sector(sector, industry, name="", description="") -> str (slug)
    get_sector_prompt(sector, industry, name="", description="") -> str

`sector` / `industry` are yfinance's broad strings (e.g. sector=
"Financial Services", industry="Banks - Regional"). This module maps
them — together with company name / description when available — onto
one of our fine-grained internal sector slugs (e.g. "banking") and
hands back either the slug or an LLM-context prompt fragment.

All sector-specific knowledge (metrics, scoring, moats, red flags,
valuation framework) lives in modules/sectors/<slug>.py. Adding a new
sector never requires touching this file.
"""

from __future__ import annotations
from modules.sectors import SECTOR_REGISTRY, get_sector_config
from modules.sectors.detector import detect_sector


def classify_sector(sector: str = "", industry: str = "", name: str = "", description: str = "") -> str:
    """
    Classifies a company into a fine-grained internal sector slug.

    Parameters
    ----------
    sector : str       — yfinance info["sector"], e.g. "Financial Services"
    industry : str      — yfinance info["industry"], e.g. "Banks - Regional"
    name : str, optional — company display name, improves precision
    description : str, optional — business description / Wikipedia extract

    Returns
    -------
    str — sector slug, always a valid key in SECTOR_REGISTRY (falls back
          to "generic" when nothing matches).
    """
    slug = detect_sector(
        company_name=name or "",
        industry=industry or "",
        sector=sector or "",
        description=description or "",
    )
    return slug if slug in SECTOR_REGISTRY else "generic"


def get_sector_prompt(sector: str = "", industry: str = "", name: str = "", description: str = "") -> str:
    """
    Returns the LLM context block to inject into any prompt analysing
    this company, so generated commentary respects sector-specific
    framing (e.g. don't apply P/E logic to a bank; don't apply D/E
    scrutiny to an asset-light IT company).

    Internally classifies first, then returns that sector's declared
    `llm_context` plus a short header naming the sector for clarity.
    """
    slug = classify_sector(sector, industry, name, description)
    cfg = get_sector_config(slug)
    return f"SECTOR: {cfg['display_name']}\n{cfg['llm_context']}"


def get_sector_display_name(slug: str) -> str:
    return get_sector_config(slug)["display_name"]


def list_available_sectors() -> list[str]:
    """Returns all registered sector slugs (useful for debugging/UI)."""
    return list(SECTOR_REGISTRY.keys())
