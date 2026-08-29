# api/routers/ai.py
"""
Slow endpoints — every one makes an LLM round trip.

Kept apart from the fast routes so a frontend can render real numbers
immediately and fill these in afterwards, rather than blocking the whole
page on an LLM call the way the Streamlit app does.

Every route degrades rather than failing: if no key is configured, or the
provider rate-limits, the response carries `ai_enabled: false` / an
`error` field and the client renders its unavailable state. AI commentary
is the garnish here — the numbers are the product.
"""

from __future__ import annotations
import json
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field

from core.config import get_settings
from api.deps import cached_stock, cached_quote, cached_news_for_llm, cached_wikipedia
from services.comparison import cagr_from_fin
from services.derived_metrics import compute_derived_metrics, compute_ev_ebitda
from services.formatters import fmt_crore, fmt_de
from services.llm_client import get_client, ask_llm_fallback
from services.prompts import build_chat_prompt
from modules.llm_utils import ask_llm_smart, parse_json_safe
from modules.sector_analysis import classify_sector, get_sector_prompt
from modules.moat_analysis import get_moat_analysis

router = APIRouter()
_s = get_settings()

_REV_KEYS = ["Total Revenue", "Revenue", "Total Revenues"]
_PROFIT_KEYS = ["Net Income", "Net Income Common Stockholders"]

_UNAVAILABLE = (
    "AI analysis is unavailable — no Groq API key is configured. "
    "Market data, health scores, and charts are unaffected."
)


def _llm(prompt: str, system: str = "", max_tokens: int = 1000, model: str | None = None) -> str:
    """Single entry point for LLM calls. Returns the friendly sentinel
    rather than raising when AI is unconfigured, so callers render their
    normal unavailable state instead of 500-ing."""
    if not _s.ai_enabled:
        return _UNAVAILABLE
    client = get_client(_s.groq_api_key)
    mdl = model or _s.llm_model_primary
    try:
        return ask_llm_smart(client, prompt, system, use_cache=True,
                             max_tokens=max_tokens, model=mdl)
    except Exception:
        return ask_llm_fallback(client, prompt, system, max_tokens, mdl)


def _business_context(name: str, fallback_desc: str) -> tuple[str, str]:
    """Prefer Wikipedia over yfinance's longBusinessSummary — the latter is
    often stale corporate boilerplate, while Wikipedia reliably names real
    segments and subsidiaries. Returns (context, source)."""
    try:
        return cached_wikipedia(name), "Wikipedia"
    except Exception:
        if fallback_desc:
            return fallback_desc, "company filings"
        return "", "sector classification only"


@router.get("/stock/{ticker}/moat")
def moat(ticker: str):
    """Competitive-moat assessment (sector rubric + optional LLM verdict)."""
    try:
        info, _, fin, bs, _ = cached_stock(ticker)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(502, f"Could not fetch data for {ticker}.")

    name = info.get("longName") or ticker
    sector, industry = info.get("sector") or "", info.get("industry") or ""
    desc = info.get("longBusinessSummary") or ""
    rev_cagr, _, _ = cagr_from_fin(fin, _REV_KEYS)
    mkt_cap = info.get("marketCap")

    result = get_moat_analysis(
        sector=sector, industry=industry, name=name, description=desc,
        roe_raw=info.get("returnOnEquity"),
        profit_margin_raw=info.get("profitMargins"),
        revenue_cagr=rev_cagr, de_raw=info.get("debtToEquity"),
        mkt_cap_cr=(mkt_cap / 1e7) if mkt_cap else None,
        ask_llm_fn=(lambda p: _llm(p)) if _s.ai_enabled else None,
    )
    return {"ticker": ticker, "ai_enabled": _s.ai_enabled, **(result or {})}


@router.get("/stock/{ticker}/analysis")
def analysis(ticker: str):
    """Snapshot + bull/bear — the app's flagship LLM output.

    Returns structured JSON rather than prose so the frontend can lay the
    sections out itself. `parsed: false` means the model returned
    something unparseable; the numeric endpoints are unaffected, which is
    exactly why they live on separate routes.
    """
    if not _s.ai_enabled:
        return {"ticker": ticker, "ai_enabled": False, "parsed": False,
                "error": "no_api_key", "message": _UNAVAILABLE}

    try:
        info, _, fin, bs, _ = cached_stock(ticker)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(502, f"Could not fetch data for {ticker}.")

    name = info.get("longName") or ticker
    sector, industry = info.get("sector") or "", info.get("industry") or ""
    desc = info.get("longBusinessSummary") or ""
    mkt_cap = info.get("marketCap")

    derived = compute_derived_metrics(info, fin, bs)
    rev_cagr, _, rev_n = cagr_from_fin(fin, _REV_KEYS)
    pft_cagr, _, pft_n = cagr_from_fin(fin, _PROFIT_KEYS)
    business_context, context_source = _business_context(name, desc)

    news = cached_news_for_llm(ticker, name)
    heads = [a.get("title", "") for a in (news.get("relevant_articles") or [])[:3]]
    news_block = ("RECENT NEWS HEADLINES:\n" + "\n".join(f"- {h}" for h in heads)) if heads else ""

    pm = info.get("profitMargins")
    em = info.get("ebitdaMargins")
    roe = info.get("returnOnEquity")

    prompt = f"""You are a senior equity research analyst writing a company brief on {name} ({ticker}) for an Indian retail investor.
Sector: {sector} | Industry: {industry} | Classified: {classify_sector(sector, industry, name, desc)}

METRICS — copy verbatim, never invent:
  TTM Net Margin  = {f'{pm*100:.2f}%' if pm is not None else 'N/A'}
  TTM Revenue     = {fmt_crore(info.get('totalRevenue'))}
  EBITDA Margin   = {f'{em*100:.2f}%' if em is not None else 'N/A'}
  Market Cap      = {fmt_crore(mkt_cap)}
  P/E             = {f"{info.get('trailingPE'):.1f}x" if info.get('trailingPE') else 'N/A'}
  ROE             = {f'{roe*100:.1f}%' if roe is not None else 'N/A'}
  D/E             = {fmt_de(info.get('debtToEquity'))}
  Revenue CAGR    = {f'{rev_n}-yr CAGR: {rev_cagr:.1f}%' if rev_cagr is not None else 'N/A'}
  Profit CAGR     = {f'{pft_n}-yr CAGR: {pft_cagr:.1f}%' if pft_cagr is not None else 'N/A'}

COMPANY DESCRIPTION (from {context_source} — authoritative):
{business_context[:2000]}

{get_sector_prompt(sector, industry, name, desc)}
{news_block}

RULES:
- Cite at most 2 metrics per section; never fabricate a number — write N/A.
- A headline must be supported by the metric cited beneath it.
- Prefer a specific recent event from the headlines above for one bull and one bear slot when genuinely relevant.

Return ONLY valid JSON, no markdown or backticks:
{{
  "snapshot": {{
    "business": "What it does and how it earns. No metrics.",
    "position": "Market standing, including Market Cap and TTM Revenue.",
    "financials": "One sentence citing the two most relevant profitability/growth metrics.",
    "outlook": "One complete forward-looking sentence."
  }},
  "bull": [{{"headline": "2-4 words", "explanation": "One sentence grounded in a metric or a listed headline."}}],
  "bear": [{{"headline": "2-4 words", "explanation": "One sentence grounded in a metric or a listed headline."}}]
}}
Exactly 3 bull and 3 bear items."""

    raw = _llm(prompt, "You are a precise equity research analyst. Return only valid JSON.",
               max_tokens=2000)
    parsed = parse_json_safe(raw) or {}
    ok = bool(parsed.get("snapshot") or parsed.get("bull"))
    return {
        "ticker": ticker, "ai_enabled": True, "parsed": ok,
        "snapshot": parsed.get("snapshot") or {},
        "bull": parsed.get("bull") or [],
        "bear": parsed.get("bear") or [],
        "raw": None if ok else raw[:600],
    }


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    history: list[dict] = Field(default_factory=list, max_length=20)
    tickers: list[str] = Field(default_factory=list, max_length=2)


@router.post("/chat")
def chat(req: ChatRequest = Body(...)):
    """Conversational Q&A, optionally grounded in live data for up to two
    named tickers (matching the Streamlit app's two-company limit)."""
    if not _s.ai_enabled:
        return {"ai_enabled": False, "reply": _UNAVAILABLE}

    blocks = []
    for t in req.tickers[:2]:
        try:
            info = cached_quote(t)
            if not info:
                continue
            roe = info.get("returnOnEquity")
            blocks.append(
                f"{info.get('longName') or t} ({t}): "
                f"Price ₹{info.get('currentPrice') or info.get('regularMarketPrice')}, "
                f"MCap {fmt_crore(info.get('marketCap'))}, "
                f"P/E {info.get('trailingPE')}, "
                f"ROE {f'{roe*100:.1f}%' if roe is not None else 'N/A'}, "
                f"D/E {fmt_de(info.get('debtToEquity'))}, "
                f"Sector {info.get('sector')}"
            )
        except Exception:
            continue

    history_str = "\n".join(
        f"{m.get('role','user').upper()}: {m.get('content','')}"
        for m in req.history[-6:]
    )
    history_str = f"{history_str}\nUSER: {req.message}".strip()

    reply = _llm(build_chat_prompt("\n".join(blocks), history_str),
                 model=_s.llm_model_light)
    return {"ai_enabled": True, "reply": reply,
            "grounded_tickers": req.tickers[:2], "used_live_data": bool(blocks)}
