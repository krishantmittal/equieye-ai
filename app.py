import html as _html
import streamlit as st
import yfinance as yf
import requests
import json
import PyPDF2
import io
import os
import base64
import time
import sys
import pandas as pd
from groq import Groq
from PIL import Image

try:
    import plotly.graph_objects as _pgo
except ImportError:
    _pgo = None

# ── Module imports ────────────────────────────────────────────────────────────
# Add the project root to sys.path so 'modules' package is always importable
_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

try:
    from modules.health_score import compute_health_score
    from modules.red_flags import detect_flags
    from modules.sector_analysis import get_sector_prompt, classify_sector
    from modules.moat_analysis import get_moat_analysis
    from modules.risk_meter import compute_risk
    from modules.quality_signals import detect_cyclical, detect_turnaround, valuation_bucket
    from modules.news_sentiment import deduplicate_articles, enrich_articles, compute_overall_sentiment
    from modules.llm_utils import ask_llm_smart
    from modules.portfolio import init_portfolio, add_holding, remove_holding, update_holding, get_holdings, compute_portfolio_stats
    from modules.data_caveats import get_data_caveat
    _MODULES_LOADED = True
except Exception as _e:
    _MODULES_LOADED = False
    _MODULES_ERROR = str(_e)


# ── Text-safe status colours ──────────────────────────────────────────────
# These are for TEXT only. The vivid brand/status colours used for chart
# marks and fills (#22C55E, #F59E0B, #EF4444) fail WCAG as text: green
# measures 2.28:1 and amber 2.15:1 against white, well below the 4.5:1
# body-text minimum. The variants below all clear 4.5:1 against both the
# page (#F6F7F9) and card (#FFFFFF) surfaces. Chart marks deliberately
# keep the vivid values — a mark is not text.
TXT_GOOD  = "#15803D"   # 5.02:1 on white
TXT_WARN  = "#B45309"   # 5.02:1 on white
TXT_BAD   = "#B91C1C"   # 6.47:1 on white
TXT_MUTED = "#5B6673"   # 5.9:1  on white


# _is_quarterly_financials / _trim_to_last_discontinuity: pure pandas
# helpers, extracted verbatim to services/financial_utils.py (Phase 1
# service-layer extraction). Aliased back to their original names here so
# no call site below needs to change — this file runs as top-level
# Streamlit script code executed top-to-bottom, so the alias must still
# appear before any line that calls it.
from services.financial_utils import (
    is_quarterly_financials as _is_quarterly_financials,
    trim_to_last_discontinuity as _trim_to_last_discontinuity,
)


LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logo.png")

# Load as a PIL Image object rather than passing the raw path string —
# Streamlit's page_icon resolves file paths relative to the working
# directory in some setups, which can silently fail and fall back to a
# default icon. Loading the actual image object sidesteps that ambiguity.
try:
    _page_icon = Image.open(LOGO_PATH)
except Exception:
    _page_icon = "💹"  # fallback if the logo file genuinely can't be found

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="EquiEye AI",
    page_icon=_page_icon,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Hide Streamlit's own chrome ───────────────────────────────────────────────
# toolbarMode="minimal" in .streamlit/config.toml already empties the
# hamburger menu, but Streamlit also renders a few other first-party bits
# independently of that setting:
#   [data-testid="stHeader"]    → the header bar itself. Previously I only
#                                  hid its *contents* (menu/decoration below),
#                                  which left the header's own background
#                                  rendered as an empty black strip across the
#                                  top of the page — collapsing the whole
#                                  element with display:none removes that
#                                  reserved space entirely.
#   footer                      → the "Made with Streamlit" footer
#   #MainMenu                   → hamburger menu icon itself (belt-and-braces
#                                  with toolbarMode, in case config.toml isn't
#                                  picked up on a given host)
#   [data-testid="stDecoration"] → the thin rainbow bar Streamlit draws across
#                                  the very top of the app
#   [data-testid="stStatusWidget"] → the "Running..."/rerun status pill
# None of this touches the Fork/GitHub badge — that one lives outside the
# app's own DOM and is controlled purely by the linked repo being public
# vs. private on Community Cloud.
st.markdown("""
<style>
[data-testid="stHeader"] { display: none !important; height: 0 !important; }
header[data-testid="stHeader"] { display: none !important; }
.stAppHeader { display: none !important; height: 0 !important; }
div[data-testid="stApp"] > header,
.stApp > header,
header { display: none !important; height: 0 !important; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }
[data-testid="stStatusWidget"] { display: none; }
[data-testid="stToolbar"] { display: none !important; height: 0 !important; }
/* Streamlit has renamed these wrapper testids across versions
   (stAppViewBlockContainer -> stMainBlockContainer, stAppViewContainer ->
   stMain) — requirements.txt pins streamlit>=1.32.0 with no upper bound,
   so Community Cloud may install a newer release than whichever version
   the original selectors below were written against. Targeting every
   known alias together instead of guessing one. */
.block-container,
[data-testid="stAppViewBlockContainer"],
[data-testid="stMainBlockContainer"] {
    padding-top: 0 !important;
}
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    padding-top: 0 !important;
    margin-top: 0 !important;
}
</style>
""", unsafe_allow_html=True)


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* ═══════════════════════════════════════════════════════════════════════════
   DESIGN TOKENS
   Every colour, size, radius and shadow in this file resolves to a token
   below. Previously ~330 hex literals were scattered across the stylesheet
   and the inline HTML, which made consistency unenforceable and a theme
   change impossible. Change a value here and it propagates everywhere.

   MARK vs TEXT colours are deliberately separate. The vivid brand green
   (#22C55E) measures 2.28:1 against white — far below the 4.5:1 WCAG body
   text minimum — so it is used only for fills, borders and chart marks.
   Text uses the darker --*-text variants, all verified >= 4.5:1 against
   both the page and card surfaces. Same for amber (2.15:1 as text) and red.
   ═══════════════════════════════════════════════════════════════════════ */
:root {
    /* Surfaces — cards are WHITE on a lightly tinted page, so elevation
       comes from contrast + shadow rather than a flat grey fill. */
    --surface-page:    #F6F7F9;
    --surface-card:    #FFFFFF;
    --surface-sunken:  #F1F3F5;
    --surface-hover:   #F8FAFC;

    /* Borders */
    --border:          #E4E7EB;
    --border-strong:   #D3D8DE;

    /* Ink */
    --ink:             #0F172A;
    --ink-secondary:   #334155;
    --ink-muted:       #5B6673;   /* 5.9:1 on card — safe for body text */

    /* Brand / status — MARK (fills, borders, chart series) */
    --brand:           #22C55E;   /* marks/fills only */
    --brand-strong:    #16A34A;   /* mark accents */
    --brand-btn:       #15803D;   /* white text on this = 5.02:1 */
    --danger:          #EF4444;
    --warn:            #F59E0B;
    --info:            #3B82F6;

    /* Brand / status — TEXT (all >= 4.5:1 on card) */
    --brand-text:      #166534;   /* 7.13:1 white; clears 4.5 on tinted */
    --danger-text:     #B91C1C;
    --warn-text:       #92400E;   /* 7.09:1 white; clears 4.5 on tinted */
    --info-text:       #2563EB;

    /* Tinted fills for badges/pills */
    --brand-soft:      rgba(34,197,94,0.10);
    --brand-soft-bd:   rgba(34,197,94,0.28);
    --danger-soft:     rgba(239,68,68,0.10);
    --danger-soft-bd:  rgba(239,68,68,0.28);
    --warn-soft:       rgba(245,158,11,0.12);
    --warn-soft-bd:    rgba(245,158,11,0.30);
    --info-soft:       rgba(59,130,246,0.10);
    --info-soft-bd:    rgba(59,130,246,0.28);
    --neutral-soft:    rgba(100,116,139,0.10);
    --neutral-soft-bd: rgba(100,116,139,0.24);

    /* Type scale — 8 steps, no ad-hoc sizes */
    --fs-2xs:  10.5px;
    --fs-xs:   11.5px;
    --fs-sm:   12.5px;
    --fs-base: 14px;
    --fs-md:   15px;
    --fs-lg:   17px;
    --fs-xl:   21px;
    --fs-2xl:  28px;
    --fs-3xl:  38px;

    /* Spacing — 4px base */
    --sp-1: 4px;  --sp-2: 8px;  --sp-3: 12px; --sp-4: 16px;
    --sp-5: 20px; --sp-6: 24px; --sp-8: 32px; --sp-10: 40px;

    /* Radius */
    --r-sm: 8px; --r-md: 12px; --r-lg: 16px; --r-full: 999px;

    /* Elevation — layered, low-alpha; carries hierarchy without heaviness */
    --sh-sm: 0 1px 2px rgba(15,23,42,0.04);
    --sh-md: 0 1px 3px rgba(15,23,42,0.05), 0 4px 12px rgba(15,23,42,0.04);
    --sh-lg: 0 2px 6px rgba(15,23,42,0.06), 0 12px 28px rgba(15,23,42,0.06);

    --focus: 0 0 0 3px rgba(34,197,94,0.28);
}

/* NOTE — no dark mode yet, deliberately.
   .streamlit/config.toml pins base="light", so Streamlit's own widgets
   (radios, number inputs, st.warning, dataframes) render light regardless
   of what this stylesheet does. A prefers-color-scheme block here would
   therefore flip the custom cards to dark while native widgets stayed
   light — a broken mixed UI, worse than no dark mode. Adding it properly
   means theming the native widgets too; the tokens above are already
   structured so that only the :root values need re-pointing when that
   work happens. */

/* ═══════════════════════════════════════════════════════════════════════════
   BASE
   ═══════════════════════════════════════════════════════════════════════ */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    -webkit-font-smoothing: antialiased;
    font-feature-settings: 'tnum' 1;   /* tabular figures — money columns align */
}
.main  { background: var(--surface-page); color: var(--ink-secondary); }
.stApp { background: var(--surface-page); }

/* ═══════════════════════════════════════════════════════════════════════════
   HEADER / HERO
   ═══════════════════════════════════════════════════════════════════════ */
.hero-title {
    font-size: var(--fs-xl); font-weight: 700; color: var(--ink);
    letter-spacing: -0.4px; margin-bottom: 1px;
}
.hero-sub { font-size: var(--fs-sm); color: var(--ink-muted); }
.hero-accent {
    background: linear-gradient(90deg, var(--info), var(--brand));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.landing-banner {
    background:
        radial-gradient(120% 140% at 0% 0%, rgba(59,130,246,0.10) 0%, transparent 55%),
        radial-gradient(120% 140% at 100% 100%, rgba(34,197,94,0.10) 0%, transparent 55%),
        var(--surface-card);
    border: 1px solid var(--border);
    border-radius: var(--r-lg);
    padding: var(--sp-10) var(--sp-8);
    margin: var(--sp-2) 0 var(--sp-6) 0;
    box-shadow: var(--sh-md);
}
.landing-headline {
    font-size: var(--fs-2xl); font-weight: 700; color: var(--ink);
    line-height: 1.18; letter-spacing: -0.7px; margin-bottom: var(--sp-3);
}
.landing-subhead { font-size: var(--fs-md); color: var(--ink-muted); }

/* ═══════════════════════════════════════════════════════════════════════════
   FEATURE GRID / STAT STRIP
   ═══════════════════════════════════════════════════════════════════════ */
.feature-grid {
    display: grid; grid-template-columns: repeat(4, 1fr);
    gap: var(--sp-3); margin-bottom: var(--sp-6);
}
.feature-card {
    background: var(--surface-card); border: 1px solid var(--border);
    border-radius: var(--r-md); padding: var(--sp-5);
    box-shadow: var(--sh-sm);
    transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
}
.feature-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--sh-md);
    border-color: var(--border-strong);
}
.feature-icon {
    width: 38px; height: 38px; border-radius: var(--r-sm);
    display: flex; align-items: center; justify-content: center;
    font-size: var(--fs-lg); margin-bottom: var(--sp-3);
}
.feature-title {
    font-size: var(--fs-base); font-weight: 600;
    color: var(--ink); margin-bottom: var(--sp-1);
}
.feature-desc { font-size: var(--fs-sm); color: var(--ink-muted); line-height: 1.55; }

.stat-strip {
    display: grid; grid-template-columns: repeat(4, 1fr);
    gap: var(--sp-3); margin-bottom: var(--sp-6);
    border-top: 1px solid var(--border); padding-top: var(--sp-5);
}
.stat-item { text-align: left; }
.stat-num   { font-size: var(--fs-lg); font-weight: 700; color: var(--ink); letter-spacing: -0.3px; }
.stat-label { font-size: var(--fs-sm); color: var(--ink-muted); margin-top: 1px; }

@media (max-width: 900px) {
    .feature-grid { grid-template-columns: repeat(2, 1fr); }
    .stat-strip   { grid-template-columns: repeat(2, 1fr); }
    .landing-headline { font-size: var(--fs-xl); }
}

/* ═══════════════════════════════════════════════════════════════════════════
   METRIC CARDS  (the KPI row under a company name)
   ═══════════════════════════════════════════════════════════════════════ */
.metric-strip {
    display: grid; grid-template-columns: repeat(5, 1fr);
    gap: var(--sp-3); margin-bottom: var(--sp-2);
}
.metric-card {
    background: var(--surface-card); border: 1px solid var(--border);
    border-radius: var(--r-md); padding: var(--sp-4) var(--sp-5);
    min-width: 0;                      /* let long values shrink, not overflow */
    box-shadow: var(--sh-sm);
}
.metric-label {
    font-size: var(--fs-2xs); color: var(--ink-muted); margin-bottom: var(--sp-1);
    text-transform: uppercase; letter-spacing: 0.7px; font-weight: 600;
}
.metric-value {
    font-size: var(--fs-xl); font-weight: 650; color: var(--ink);
    letter-spacing: -0.5px;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.metric-sub { font-size: var(--fs-xs); margin-top: 2px; font-weight: 500; }

/* ═══════════════════════════════════════════════════════════════════════════
   SECTION CARDS
   ═══════════════════════════════════════════════════════════════════════ */
/* .section-card is a section HEADER, not a card — deliberately.

   Every call site is written as:
       st.markdown("<div class='section-card'><div class='section-title'>X</div>")
       ...content rendered by separate st.* calls...
       st.markdown("</div>")
   but Streamlit auto-closes unclosed tags within each st.markdown() call,
   so the wrapper closes immediately after the title and the content lands
   in sibling containers — the trailing </div> is orphaned (hence the
   empty-markdown-container rule further down). Verified in the DOM: all 14
   .section-card elements contain only their title.

   So this element can never wrap anything. Giving it a card background
   would render 14 empty boxes down the page; the previous grey-card-on-
   white styling merely camouflaged them. Treat it as a header band and let
   the real content below carry its own surfaces. */
.section-card {
    background: transparent; border: none; box-shadow: none;
    padding: 0; margin: var(--sp-6) 0 var(--sp-3) 0;
}
.section-title {
    font-size: var(--fs-sm); font-weight: 700; text-transform: uppercase;
    letter-spacing: 1.1px; color: var(--ink-secondary);
    display: flex; align-items: center; gap: var(--sp-2);
    padding-bottom: var(--sp-2);
    border-bottom: 1px solid var(--border);
}
.section-title::before {
    content: ''; width: 3px; height: 13px; border-radius: 2px;
    background: var(--brand); flex: none;
}

/* ═══════════════════════════════════════════════════════════════════════════
   DATA TABLES  (earnings insights / watchlist / portfolio)

   These are CSS grids rather than st.columns() on purpose: st.columns()
   auto-stacks every cell onto its own full-width row on mobile, which
   separates a company from its price and turns the table into a scrambled
   list of labels-then-values. One HTML grid per row keeps a row's cells
   together at any viewport width. Action buttons still have to be real
   Streamlit widgets, so they sit in a slim st.columns() beside the row.
   ═══════════════════════════════════════════════════════════════════════ */
.ei-table { width: 100%; }
.ei-row {
    display: grid; grid-template-columns: 0.7fr 1.7fr 1.7fr 0.8fr;
    align-items: center; column-gap: var(--sp-2);
    padding: var(--sp-2) 0; border-bottom: 1px solid var(--border);
}
.ei-row:last-child { border-bottom: none; }
.ei-row.ei-header { border-bottom: 1px solid var(--border-strong); padding-bottom: var(--sp-2); }
.ei-row.ei-header .ei-cell {
    font-size: var(--fs-2xs); color: var(--ink-muted);
    text-transform: uppercase; letter-spacing: 0.7px; font-weight: 600;
}
.ei-cell {
    font-size: var(--fs-base); color: var(--ink-secondary);
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.ei-cell.ei-year   { color: var(--ink-muted); font-weight: 500; }
.ei-cell.ei-margin { font-size: var(--fs-sm); }

.wl-row {
    display: grid; grid-template-columns: 2.2fr 1fr 1fr 1fr 0.8fr;
    align-items: center; column-gap: var(--sp-3); padding: var(--sp-2) 0;
    border-bottom: 1px solid var(--border);
}
.wl-row:last-child { border-bottom: none; }
.wl-row.wl-header { border-bottom: 1px solid var(--border-strong); padding-bottom: var(--sp-2); }
.wl-row.wl-header .wl-cell {
    font-size: var(--fs-2xs); color: var(--ink-muted);
    text-transform: uppercase; letter-spacing: 0.7px; font-weight: 600;
}
.wl-cell { font-size: var(--fs-base); color: var(--ink-secondary); overflow: hidden; text-overflow: ellipsis; }

.pt-row {
    display: grid; grid-template-columns: 2fr 0.7fr 1fr 1fr 1.3fr;
    align-items: center; column-gap: var(--sp-3); padding: var(--sp-2) 0;
    border-bottom: 1px solid var(--border);
}
.pt-row:last-child { border-bottom: none; }
.pt-row.pt-header { border-bottom: 1px solid var(--border-strong); padding-bottom: var(--sp-2); }
.pt-row.pt-header .pt-cell {
    font-size: var(--fs-2xs); color: var(--ink-muted);
    text-transform: uppercase; letter-spacing: 0.7px; font-weight: 600;
}
.pt-cell { font-size: var(--fs-base); color: var(--ink-secondary); overflow: hidden; text-overflow: ellipsis; }

.pt-edit-row {
    background: var(--surface-sunken); border: 1px solid var(--border);
    border-radius: var(--r-sm); padding: var(--sp-2) var(--sp-3);
    margin: var(--sp-1) 0 var(--sp-2) 0;
}

/* ═══════════════════════════════════════════════════════════════════════════
   TAGS / BADGES / PILLS
   Status is never colour-alone: each tag carries a text label (and the
   call sites add a ●/⚑ glyph), so these read correctly in greyscale and
   for colour-vision-deficient users.
   ═══════════════════════════════════════════════════════════════════════ */
.bull-tag, .bear-tag, .neutral-tag, .risk-tag {
    padding: var(--sp-1) var(--sp-3); border-radius: var(--r-sm);
    font-size: var(--fs-base); font-weight: 600; letter-spacing: 0.2px;
}
.bull-tag    { background: var(--brand-soft);   color: var(--brand-text);  border: 1px solid var(--brand-soft-bd); }
.bear-tag    { background: var(--danger-soft);  color: var(--danger-text); border: 1px solid var(--danger-soft-bd); }
.neutral-tag { background: var(--neutral-soft); color: var(--ink-secondary); border: 1px solid var(--neutral-soft-bd); }
.risk-tag    { background: var(--warn-soft);    color: var(--warn-text);   border: 1px solid var(--warn-soft-bd); }

.score-ring {
    font-size: var(--fs-3xl); font-weight: 700; color: var(--brand-text);
    text-align: center; padding: var(--sp-4) 0; letter-spacing: -1.2px;
}
.score-label { text-align: center; font-size: var(--fs-base); color: var(--ink-muted); }

.flag-item {
    display: flex; align-items: center; gap: var(--sp-2);
    padding: var(--sp-2) 0; border-bottom: 1px solid var(--border);
    font-size: var(--fs-base); color: var(--ink-secondary);
}
.flag-item:last-child { border-bottom: none; }

/* ═══════════════════════════════════════════════════════════════════════════
   CHAT
   ═══════════════════════════════════════════════════════════════════════ */
.chat-msg-user {
    background: var(--info-soft); border: 1px solid var(--info-soft-bd);
    border-radius: var(--r-md) var(--r-md) var(--sp-1) var(--r-md);
    padding: var(--sp-3) var(--sp-4); margin: var(--sp-2) 0;
    font-size: var(--fs-md); max-width: 80%; margin-left: auto;
    color: var(--ink); line-height: 1.6;
}
.chat-msg-ai {
    background: var(--surface-card); border: 1px solid var(--border);
    border-radius: var(--r-md) var(--r-md) var(--r-md) var(--sp-1);
    padding: var(--sp-3) var(--sp-4); margin: var(--sp-2) 0;
    font-size: var(--fs-md); max-width: 85%;
    color: var(--ink); line-height: 1.7; box-shadow: var(--sh-sm);
}

.disclaimer {
    font-size: var(--fs-sm); color: var(--ink-muted); text-align: center;
    padding: var(--sp-5) 0; border-top: 1px solid var(--border); margin-top: var(--sp-8);
}

/* Semantic text helpers — text-safe variants, not the vivid mark colours */
.green  { color: var(--brand-text); }
.red    { color: var(--danger-text); }
.yellow { color: var(--warn-text); }
.gray   { color: var(--ink-muted); }

/* ═══════════════════════════════════════════════════════════════════════════
   STREAMLIT WIDGET OVERRIDES
   ═══════════════════════════════════════════════════════════════════════ */
div[data-testid="stTextInput"] input {
    background: var(--surface-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r-sm) !important;
    color: var(--ink) !important;
    font-size: var(--fs-md) !important;
    padding: 11px var(--sp-4) !important;
    transition: border-color .15s ease, box-shadow .15s ease !important;
}
div[data-testid="stTextInput"] input::placeholder {
    color: var(--ink-muted) !important;
    opacity: 1 !important;
}
div[data-testid="stTextInput"] input:focus {
    border-color: var(--brand) !important;
    box-shadow: var(--focus) !important;
    outline: none !important;
}
div[data-testid="stButton"] button {
    background: var(--brand-btn) !important;
    color: #FFFFFF !important;                    /* 5.02:1 on --brand-btn */
    font-weight: 600 !important;
    border-radius: var(--r-sm) !important;
    border: none !important;
    padding: 9px var(--sp-5) !important;
    font-size: var(--fs-base) !important;
    box-shadow: var(--sh-sm) !important;
    transition: background .15s ease, transform .12s ease, box-shadow .15s ease !important;
}
div[data-testid="stButton"] button:hover {
    background: #166534 !important;
    transform: translateY(-1px) !important;
    box-shadow: var(--sh-md) !important;
}
div[data-testid="stButton"] button:focus-visible {
    box-shadow: var(--focus) !important;
    outline: none !important;
}

.stTabs [data-baseweb="tab"]   { font-size: var(--fs-base) !important; font-weight: 500 !important; }
/* The label sits in a nested element that can carry Streamlit's own muted
   grey and win over a colour set on the parent — cover it explicitly. */
.stTabs [data-baseweb="tab"] * { color: var(--ink-muted) !important; }
.stTabs [aria-selected="true"] * { color: var(--ink) !important; font-weight: 600 !important; }
.stTabs [aria-selected="true"]   { border-bottom-color: var(--brand) !important; }

div[data-testid="stMetricLabel"] p { color: var(--ink-muted) !important; font-size: var(--fs-sm) !important; }
div[data-testid="stMetricValue"]   { color: var(--ink) !important; }

/* ═══════════════════════════════════════════════════════════════════════════
   COMPARE STOCKS
   Series A = brand green, Series B = info blue. This categorical pair is
   validated: adjacent ΔE 30.8 (deuteranopia) / 32.7 (normal vision), well
   above the ΔE 8 target, so the two series stay distinguishable under
   colour-vision deficiency. Identity is never carried by colour alone —
   every row is direct-labelled and the full numeric table sits alongside.
   ═══════════════════════════════════════════════════════════════════════ */
.compare-grid   { display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 0; }
.compare-header { margin-bottom: var(--sp-4); }

.winner-card {
    background:
        radial-gradient(110% 160% at 0% 0%, rgba(34,197,94,0.10) 0%, transparent 60%),
        var(--surface-card);
    border: 1px solid var(--brand-soft-bd);
    border-radius: var(--r-lg);
    padding: var(--sp-6) var(--sp-8);
    margin-bottom: var(--sp-5);
    position: relative; overflow: hidden;
    box-shadow: var(--sh-md);
}
.winner-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, var(--brand), var(--info));
}
.winner-title {
    font-size: var(--fs-lg); font-weight: 700; color: var(--brand-text);
    letter-spacing: -0.2px; margin-bottom: var(--sp-2);
}
.score-pill {
    display: inline-block; padding: var(--sp-1) var(--sp-3);
    border-radius: var(--r-full); font-size: var(--fs-sm);
    font-weight: 700; margin-right: var(--sp-2);
}
.score-pill-a { background: var(--brand-soft); color: var(--brand-text); border: 1px solid var(--brand-soft-bd); }
.score-pill-b { background: var(--info-soft);  color: var(--info-text);  border: 1px solid var(--info-soft-bd); }

.val-badge {
    display: inline-block; padding: 2px var(--sp-2);
    border-radius: var(--r-full); font-size: var(--fs-2xs);
    font-weight: 600; letter-spacing: 0.3px;
}
.val-attractive { background: var(--brand-soft);  color: var(--brand-text);  border: 1px solid var(--brand-soft-bd); }
.val-fair       { background: var(--warn-soft);   color: var(--warn-text);   border: 1px solid var(--warn-soft-bd); }
.val-expensive  { background: var(--danger-soft); color: var(--danger-text); border: 1px solid var(--danger-soft-bd); }

/* Winner emphasis: weight + the 🏆 glyph at the call site carry the meaning,
   so this is not colour-alone. Dropped the old text-shadow glow — it blurred
   small figures without adding information. */
.cmp-winner-a { color: var(--brand-text) !important; font-weight: 650 !important; }
.cmp-winner-b { color: var(--info-text)  !important; font-weight: 650 !important; }
.cmp-tie      { color: var(--ink-muted)  !important; font-size: var(--fs-2xs) !important; font-weight: 500 !important; }
.cmp-section-head {
    font-size: var(--fs-2xs); font-weight: 700; text-transform: uppercase;
    letter-spacing: 1.1px; color: var(--ink-muted);
    padding: var(--sp-3) var(--sp-3) var(--sp-1) var(--sp-3);
    background: var(--surface-sunken);
    border-bottom: 1px solid var(--border);
    grid-column: 1 / -1;
}

/* st.markdown() renders each call in its own DOM wrapper, so a bare </div>
   written as a separate call is orphaned and can leave a 1px gap. Hide
   empty markdown containers so close tags stay invisible. */
div[data-testid="stMarkdownContainer"]:empty { display: none; }

/* Let a horizontal finger-drag on the price chart scrub the tooltip instead
   of the browser immediately hijacking it as a page scroll. */
div[data-testid="stVegaLiteChart"] { touch-action: pan-y; }

/* Respect reduced-motion preferences. */
@media (prefers-reduced-motion: reduce) {
    * { animation-duration: .01ms !important; transition-duration: .01ms !important; }
    .feature-card:hover, div[data-testid="stButton"] button:hover { transform: none !important; }
}

/* ═══════════════════════════════════════════════════════════════════════════
   MOBILE
   Streamlit's st.columns() auto-stacks on narrow screens, so most of the
   layout already adapts. The exceptions are the raw CSS grids above and
   the large fixed type sizes.
   ═══════════════════════════════════════════════════════════════════════ */
@media (max-width: 640px) {
    .hero-title      { font-size: var(--fs-lg) !important; }
    .hero-sub        { font-size: var(--fs-xs) !important; }
    .landing-banner  { padding: var(--sp-6) var(--sp-5) !important; }
    .landing-headline{ font-size: var(--fs-xl) !important; }
    .metric-strip    { grid-template-columns: repeat(2, 1fr) !important; gap: var(--sp-2) !important; }
    .metric-card     { padding: var(--sp-3) !important; }
    .metric-value    { font-size: var(--fs-lg) !important; }
    .score-ring      { font-size: var(--fs-2xl) !important; }
    .section-card    { padding: var(--sp-4) !important; }
    .ei-row  { grid-template-columns: 0.6fr 1.6fr 1.6fr 0.7fr !important; column-gap: var(--sp-1) !important; }
    .ei-cell { font-size: var(--fs-sm) !important; }
    .ei-row.ei-header .ei-cell { font-size: var(--fs-2xs) !important; }
    .wl-row  { grid-template-columns: 2fr 1fr 1fr 0.9fr 0.7fr !important; column-gap: 5px !important; }
    .wl-cell { font-size: var(--fs-sm) !important; }
    .wl-row.wl-header .wl-cell { font-size: var(--fs-2xs) !important; }
    .pt-row  { grid-template-columns: 1.8fr 0.6fr 0.9fr 0.9fr 1.1fr !important; column-gap: 5px !important; }
    .pt-cell { font-size: var(--fs-sm) !important; }
    .pt-row.pt-header .pt-cell { font-size: var(--fs-2xs) !important; }

    /* Keep metric + value-A together and let value-B compress, rather than
       a full 1-column stack which would separate a metric from its value. */
    .compare-grid { grid-template-columns: 1.3fr 1fr 1fr !important; font-size: var(--fs-sm) !important; }
    .winner-card  { padding: var(--sp-4) !important; }
    .feature-grid { grid-template-columns: 1fr 1fr !important; }
}
</style>
""", unsafe_allow_html=True)

# ── Secret access ────────────────────────────────────────────────────────────
def _secret(name: str, default=None):
    """Read a secret without ever raising.

    st.secrets raises StreamlitSecretNotFoundError when NO secrets source
    exists at all — and it raises from `.get()` too, not just subscripting,
    because any access triggers the underlying file load. Previously this
    file read st.secrets["GROQ_API_KEY"] directly at module level, so a
    single unconfigured secret took down the ENTIRE app at import time
    (blank "Error running app." with the real traceback hidden from
    non-owners on Streamlit Cloud) — including the price, financials,
    health score, red flag, and chart sections that need no API key at all.

    Degrading one feature is always preferable to losing the whole page,
    so every secret read goes through here and returns `default` on any
    failure. Callers must handle a None/empty value.
    """
    try:
        return st.secrets[name]
    except Exception:
        return default


# ── Groq client ──────────────────────────────────────────────────────────────
# services.llm_client.get_client() is the plain, Streamlit-free constructor
# (Phase 1 service-layer extraction) — st.secrets/st.cache_resource stay here.
from services.llm_client import get_client as _get_client_impl

@st.cache_resource
def get_client():
    """Returns None (rather than raising) when GROQ_API_KEY is unavailable,
    so the app still loads with AI sections disabled."""
    key = _secret("GROQ_API_KEY")
    if not key:
        return None
    try:
        return _get_client_impl(key)
    except Exception:
        return None

client = get_client()
AI_ENABLED = client is not None

# ── NSE company database + search/disambiguation ───────────────────────────
# services.nse_database has BRAND_ALIASES / load_nse_database() /
# search_nse_matches() — pure, no Streamlit dependency. Caching and the
# empty-database error message stay here as thin wrappers.
# Note: Tata Motors demerged in 2025 into TMPV.NS and TMCV.NS. Disambiguation
# is handled automatically by search_nse_matches via the NSE database — both
# tickers appear as separate entries, so typing "Tata Motors" correctly
# surfaces two distinct picks without any hardcoded special-casing here.
from services.nse_database import (
    BRAND_ALIASES,
    load_nse_database as _load_nse_database_impl,
    search_nse_matches as _search_nse_matches_impl,
)

@st.cache_data
def load_nse_database():
    return _load_nse_database_impl()

def search_nse_matches(query: str):
    database = load_nse_database()
    if not database:
        st.error("⚠ NSE company database could not be loaded (data/nse_equity_list.csv missing or empty). Company search is unavailable.")
        return []
    return _search_nse_matches_impl(query, database)

# ── News fetch + relevance filtering ────────────────────────────────────────
# services.news has NEWS_BRAND_ALIASES / fetch_relevant_news() — pure, no
# Streamlit dependency (the NewsAPI key is now an explicit parameter
# instead of being read from st.secrets inside the function). Caching and
# the st.secrets lookup stay here.
from services.news import fetch_relevant_news as _fetch_relevant_news_impl

@st.cache_data(ttl=900)  # 15 min — news doesn't need to be second-fresh, and this
                          # lets the same fetch serve both the AI-analysis prompt
                          # (called early) and the Latest News section (called
                          # later) without hitting NewsAPI twice per page load.
def fetch_relevant_news(ticker: str, name: str) -> dict:
    # _secret() never raises; the service layer already handles a None key
    # by returning {"error": "no_key"}, which callers render as "no news".
    return _fetch_relevant_news_impl(ticker, name, _secret("NEWS_API_KEY"))


@st.cache_data(ttl=3600)  # 1 hour — matches _cached_llm_call's TTL in llm_utils.py.
def fetch_news_for_llm_context(ticker: str, name: str) -> dict:
    """Same data as fetch_relevant_news(), but cached for a full hour instead
    of 15 minutes, and used ONLY to ground the combined-analysis LLM prompt
    (never for the user-facing Latest News section, which should stay on
    the 15-min refresh via fetch_relevant_news() directly).

    Why this exists: the combined prompt embeds the top-3 headlines so
    bull/bear can reference current events. The Groq response for that
    prompt is itself cached for 1 hour (_cached_llm_call in llm_utils.py),
    keyed on the exact prompt text. If the embedded headlines came from
    the 15-min-TTL fetch_relevant_news(), the prompt text — and therefore
    the cache key — would change roughly 4x more often than the response
    cache's own TTL, forcing a fresh Groq call almost every 15 minutes
    instead of every hour for a stock people keep coming back to. Wrapping
    the same underlying fetch in its own 1-hour cache means the headline
    snapshot fed into the LLM prompt only changes once an hour, so it
    stays aligned with (rather than fragmenting) the Groq response cache.
    """
    return fetch_relevant_news(ticker, name)

# fmt_crore / pct / get_pe_bands: pure formatters, extracted verbatim to
# services/formatters.py — no wrapper needed, none had a Streamlit dependency.
from services.formatters import fmt_crore, pct, get_pe_bands

# ask_llm / sanitize_llm_html: extracted to services/llm_client.py. The
# cached/smart path (ask_llm_smart, via modules/llm_utils.py) stays a thin
# branch here since it depends on _MODULES_LOADED — app.py's own flag for
# whether the whole modules/ package imported cleanly, not just llm_utils.
from services.llm_client import ask_llm_fallback as _ask_llm_fallback, sanitize_llm_html

def ask_llm(prompt: str, system: str = "", max_tokens: int = 1000, model: str = "openai/gpt-oss-120b") -> str:
    """
    Calls Groq's API with smart caching and retry logic.
    Uses ask_llm_smart from modules/llm_utils.py when available,
    falling back to direct call. Caches identical prompts for 1 hour
    to reduce Groq token consumption — critical for Compare Stocks,
    PDF Q&A, and Ask EquiEye which were hitting rate limits.

    max_tokens defaults to 1000 (unchanged from before) for every
    existing call site. Callers producing a larger JSON payload (e.g.
    the combined snapshot+bull+bear analysis) should pass a higher
    value explicitly — see the note at that call site for why this
    matters: a too-small budget silently truncates the JSON mid-string,
    which fails to parse and falls back to a much more generic retry
    prompt without ever surfacing an error to the person testing it.

    model defaults to "openai/gpt-oss-120b", the primary model
    (unchanged for every existing call site — was llama-3.3-70b-versatile
    until Groq retired that model). Pass model="openai/gpt-oss-20b" for
    lightweight, less quality-sensitive calls (sentiment tagging,
    one-sentence outlook retries, conversational Q&A) — that model draws
    from a separate free-tier daily quota, so routing those calls there
    takes real load off the primary model's quota without touching the
    core snapshot/bull/bear analysis.
    """
    # No usable Groq client (missing/invalid GROQ_API_KEY). Return the same
    # friendly sentinel the error paths below already produce, so every
    # existing call site renders its normal "AI unavailable" state instead
    # of raising and taking the page down.
    if client is None:
        return ("⚠ AI analysis is unavailable — no Groq API key is configured. "
                "The market data, financial health score, and charts on this page "
                "are unaffected.")

    if _MODULES_LOADED:
        return ask_llm_smart(client, prompt, system, use_cache=True, max_tokens=max_tokens, model=model)
    return _ask_llm_fallback(client, prompt, system, max_tokens, model)


# ── Wikipedia company context ─────────────────────────────────────────────────
# services.wikipedia.fetch_wikipedia_context() is the plain, uncached
# implementation (Phase 1 service-layer extraction) — the @st.cache_data
# decorator stays here.
from services.wikipedia import fetch_wikipedia_context as _fetch_wikipedia_context_impl

@st.cache_data(ttl=86400)  # cache for 24 hours — Wikipedia doesn't change daily
def fetch_wikipedia_context(company_name: str) -> str:
    return _fetch_wikipedia_context_impl(company_name)

# ── Fetch stock data ──────────────────────────────────────────────────────────
# services.market_data has the plain, uncached implementations (Phase 1
# service-layer extraction) — @st.cache_data(ttl=300) stays here on each
# thin wrapper, same TTL as before.
from services.market_data import (
    is_connectivity_error as _is_connectivity_error,
    fetch_stock as _fetch_stock_impl,
    fetch_quote as _fetch_quote_impl,
    fetch_price_history as _fetch_price_history_impl,
)


@st.cache_data(ttl=300)
def fetch_stock(ticker: str):
    return _fetch_stock_impl(ticker)


@st.cache_data(ttl=300)
def fetch_quote(ticker: str):
    return _fetch_quote_impl(ticker)


@st.cache_data(ttl=300)
def fetch_price_history(sym: str, period: str, interval: str):
    return _fetch_price_history_impl(sym, period, interval)


# ── Module-level helpers ──────────────────────────────────────────────────────
# fmt_de: pure formatter, extracted verbatim to services/formatters.py.
from services.formatters import fmt_de

def mcard(col, label, val, sub="", sub_color="#6B7280"):
    """Render a metric card into a Streamlit column. Defined at module level
    so it isn't wastefully re-created on every stock load."""
    col.markdown(f"""
    <div class='metric-card'>
        <div class='metric-label'>{label}</div>
        <div class='metric-value'>{val}</div>
        <div class='metric-sub' style='color:{sub_color};'>{sub}</div>
    </div>""", unsafe_allow_html=True)


def mcard_html(label, val, sub="", sub_color="#6B7280", val_color="#111827"):
    """Same card markup as mcard(), but returns a raw HTML string instead of
    writing into a Streamlit column. Used for the top metric strip so the
    5 cards live inside one CSS grid (see .metric-strip) instead of
    st.columns(), which auto-stacks to a single column on narrow/mobile
    screens and made the cards run into each other."""
    return f"""
    <div class='metric-card'>
        <div class='metric-label'>{label}</div>
        <div class='metric-value' style='color:{val_color};'>{val}</div>
        <div class='metric-sub' style='color:{sub_color};'>{sub}</div>
    </div>"""


# ── Module-level pure functions (hoisted out of render blocks) ────────────────
# _build_smart_verdict / _outlook_looks_truncated / the sector-prompt class
# maps: extracted verbatim to services/verdict.py and services/sector_prompts.py
# (Phase 1 service-layer extraction) — pure string/data logic, no Streamlit
# dependency. Aliased back to the original names so no call site below needs
# to change.
from services.verdict import build_smart_verdict as _build_smart_verdict, outlook_looks_truncated as _outlook_looks_truncated
from services.sector_prompts import SECTOR_CLASS_MAP as _SECTOR_CLASS_MAP, FIN_SLUG_CLASS_MAP as _FIN_SLUG_CLASS_MAP


# ── Landing hero (top bar + hero banner) ──────────────────────────────────
def get_logo_base64():
    try:
        with open(LOGO_PATH, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return None

logo_b64 = get_logo_base64()
logo_img = f"<img src='data:image/png;base64,{logo_b64}' style='height:56px; width:auto; margin-right:14px; border-radius:12px;' />" if logo_b64 else ""

st.markdown(f"""
<div style='display:flex; align-items:center; justify-content:space-between; padding: 0.4rem 0 0.8rem 0; flex-wrap:wrap; gap:12px;'>
  <div style='display:flex; align-items:center;'>
    {logo_img}
    <div>
      <div class='hero-title'>EquiEye <span class='hero-accent'>AI</span></div>
      <div class='hero-sub'>AI-powered stock research for Indian retail investors</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# Degraded-mode banner — shown once, at the top, when the Groq key is
# missing so it's immediately obvious WHY the AI sections are empty.
# Everything else on the page (live prices, financials, health score, red
# flags, risk meter, charts, comparison tables) works without any API key.
if not AI_ENABLED:
    st.warning(
        "**AI features are disabled** — no valid `GROQ_API_KEY` was found. "
        "Live market data, financial health scores, red flags, and charts all "
        "still work. To enable AI analysis, set `GROQ_API_KEY` in "
        "`.streamlit/secrets.toml` locally, or in **Settings → Secrets** on "
        "Streamlit Community Cloud.",
        icon="⚠️",
    )

# Navigation tabs — placed right after the header, before the hero banner,
# matching the reference layout (tabs sit above the banner+search area)
tab_main, tab_compare, tab_pdf, tab_chat, tab_watchlist, tab_portfolio = st.tabs([
    "Stock Research", "Compare Stocks", "Annual Report", "Ask EquiEye", "Watchlist", "Portfolio"
])

def detect_companies_in_question(question: str):
    """
    Detects companies mentioned in the question, returning a list of
    (symbol, display_name) for each DISTINCT company found — this lets
    Ask EquiEye handle "compare X and Y" by fetching live data for
    both, instead of just the first one or giving up.

    Groups candidate matches by the SPECIFIC phrase that matched
    (e.g. "bajaj finance" vs "bajaj auto" are different groups, even
    though both start with "bajaj"). Only a group name used ALONE
    with no distinguishing second word (e.g. just "Tata Motors" when
    two demerged entities share that exact same two-word name) is
    treated as genuinely ambiguous.

    Defined at module level so it isn't re-created on every chat render.
    """
    question_lower = question.lower()
    words = question_lower.replace("?", "").replace(",", "").split()
    database = load_nse_database()

    # Use module-level BRAND_ALIASES — single source of truth.
    # Build one unified list of (symbol, name, match_phrase) candidates
    # from tickers, brand aliases, and company-name phrases together.
    candidates = []

    for symbol, name in database:
        sym_root = symbol.replace(".NS", "").lower()
        if len(sym_root) >= 3 and sym_root in words:
            candidates.append((symbol, name, sym_root))

    for alias, sym in BRAND_ALIASES.items():
        if alias in words:
            for s, n in database:
                if s == sym:
                    candidates.append((s, n, alias))

    for symbol, name in database:
        name_words = [w for w in name.lower().replace(".", "").split()
                      if len(w) > 2 and w not in ("limited", "company", "the", "and")]
        if not name_words:
            continue
        if len(name_words) == 1 and name_words[0] in words:
            candidates.append((symbol, name, name_words[0]))
        elif len(name_words) >= 2 and name_words[0] in words and name_words[1] in words:
            candidates.append((symbol, name, f"{name_words[0]} {name_words[1]}"))

    if not candidates:
        return []

    seen_pairs = set()
    groups = {}
    for symbol, name, phrase in candidates:
        key = (symbol, phrase)
        if key in seen_pairs:
            continue
        seen_pairs.add(key)
        groups.setdefault(phrase, []).append((symbol, name))

    results = []
    ambiguous_groups = []
    seen_symbols = set()

    for phrase, hits in groups.items():
        unique_in_group = {h[0]: h[1] for h in hits}
        if len(unique_in_group) == 1:
            sym = list(unique_in_group.keys())[0]
            if sym not in seen_symbols:
                seen_symbols.add(sym)
                results.append((sym, unique_in_group[sym]))
        else:
            ambiguous_groups.extend(unique_in_group.values())

    if results:
        return results[:3]
    if ambiguous_groups:
        return [("AMBIGUOUS", ambiguous_groups)]
    return []


# build_combined_prompt / build_compare_prompt / build_pdf_summary_prompt /
# build_pdf_qa_prompt / build_chat_prompt: extracted verbatim to
# services/prompts.py (Phase 1 service-layer extraction) — verified
# byte-identical output against the original inline f-strings for every
# conditional branch. Imported here, before tab_main, since
# build_combined_prompt is used inside it.
from services.prompts import (
    build_combined_prompt,
    build_compare_prompt,
    build_pdf_summary_prompt,
    build_pdf_qa_prompt,
    build_chat_prompt,
)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 1: STOCK RESEARCH
# ─────────────────────────────────────────────────────────────────────────────
with tab_main:
    st.markdown("""
    <div class='landing-banner' style='padding-bottom:1.6rem;'>
      <div class='landing-banner-text'>
        <div class='landing-headline'>Smarter research.<br>Stronger <span class='hero-accent'>investments</span>.</div>
        <div class='landing-subhead' style='margin-bottom:1.4rem;'>Get AI-powered insights on any Indian stock in seconds.</div>
      </div>
    """, unsafe_allow_html=True)

    with st.form(key="search_form"):
        col_input, col_btn = st.columns([4, 1])
        with col_input:
            stock_input = st.text_input("", placeholder="Enter company name or ticker (e.g. Tata Motors, RELIANCE, ZOMATO.NS)", label_visibility="collapsed")
        with col_btn:
            analyse_btn = st.form_submit_button("Analyse →")

    st.markdown("</div>", unsafe_allow_html=True)  # closes landing-banner

    # Session state for the resolved ticker and pending search results
    if "resolved_ticker_override" not in st.session_state:
        st.session_state.resolved_ticker_override = None
    if "search_matches" not in st.session_state:
        st.session_state.search_matches = None
    if "last_search_term" not in st.session_state:
        st.session_state.last_search_term = ""

    if analyse_btn and stock_input:
        st.session_state.resolved_ticker_override = None
        st.session_state.last_search_term = stock_input  # persist for error message on rerun
        with st.spinner(f"Searching for '{stock_input}'..."):
            matches = search_nse_matches(stock_input)
        st.session_state.search_matches = matches

    # Always show a picker when there are search results pending —
    # rendered right here, immediately below the search bar
    if st.session_state.search_matches is not None:
        matches = st.session_state.search_matches
        if len(matches) == 0:
            _search_label = st.session_state.get("last_search_term") or "your query"
            st.error(f"No NSE-listed company found matching '{_search_label}'. Try the exact ticker (e.g. RELIANCE.NS).")
        elif len(matches) == 1:
            st.session_state.resolved_ticker_override = matches[0][0]
            st.session_state.search_matches = None
        else:
            _label = st.session_state.get("last_search_term") or "your query"
            st.markdown(f"<p style='color:#5B6673; font-size:13px; margin-bottom:10px;'>Found {len(matches)} matches for '{_label}' — which one did you mean?</p>", unsafe_allow_html=True)
            pick_cols = st.columns(min(3, len(matches)))
            for i, (sym, lname) in enumerate(matches):
                with pick_cols[i % 3]:
                    label = f"{lname}\n({sym})" if lname != sym else sym
                    if st.button(label, key=f"pick_{i}_{sym}"):
                        st.session_state.resolved_ticker_override = sym
                        st.session_state.search_matches = None
                        st.rerun()

            # Manual override — in case search missed the company you wanted
            with st.expander("Don't see your company? Enter the exact NSE ticker"):
                manual_col1, manual_col2 = st.columns([3, 1])
                with manual_col1:
                    manual_ticker = st.text_input("e.g. HDFCBANK.NS", key="manual_ticker_input", label_visibility="collapsed")
                with manual_col2:
                    if st.button("Use this", key="manual_ticker_btn") and manual_ticker:
                        mt = manual_ticker.strip().upper()
                        if not mt.endswith(".NS") and "." not in mt:
                            mt += ".NS"
                        st.session_state.resolved_ticker_override = mt
                        st.session_state.search_matches = None
                        st.rerun()
    else:
        # No active search — show the landing page feature cards and stats
        # These hide once the user searches to keep focus on the results
        ticker_selected = st.session_state.get("resolved_ticker_override")
        if not ticker_selected:
            st.markdown("""
            <div class='feature-grid'>
              <div class='feature-card'>
                <div class='feature-icon' style='background:#1E3A8A;'>📊</div>
                <div class='feature-title'>Fundamental Analysis</div>
                <div class='feature-desc'>AI-powered analysis of financials, ratios, growth, and profitability.</div>
              </div>
              <div class='feature-card'>
                <div class='feature-icon' style='background:#14532D;'>📰</div>
                <div class='feature-title'>News Intelligence</div>
                <div class='feature-desc'>Real-time news analysis and sentiment insights that move the market.</div>
              </div>
              <div class='feature-card'>
                <div class='feature-icon' style='background:#581C87;'>📄</div>
                <div class='feature-title'>Annual Report AI</div>
                <div class='feature-desc'>Upload annual reports and ask questions. Get answers backed by data.</div>
              </div>
              <div class='feature-card'>
                <div class='feature-icon' style='background:#7C2D12;'>🧠</div>
                <div class='feature-title'>Ask EquiEye</div>
                <div class='feature-desc'>Your AI investment assistant. Ask anything about stocks, markets, and investing.</div>
              </div>
            </div>
            <div class='stat-strip'>
              <div class='stat-item'><div class='stat-num'>2,374+</div><div class='stat-label'>Indian Stocks Covered</div></div>
              <div class='stat-item'><div class='stat-num'>Real-time</div><div class='stat-label'>Market Data</div></div>
              <div class='stat-item'><div class='stat-num'>AI Powered</div><div class='stat-label'>LLM + Financial Models</div></div>
              <div class='stat-item'><div class='stat-num'>Secure & Private</div><div class='stat-label'>Your data is never stored</div></div>
            </div>
            """, unsafe_allow_html=True)

    ticker = st.session_state.resolved_ticker_override

    if ticker:
        # Initialise ALL return values before the try block so they're always
        # defined even if fetch_stock raises — avoids UnboundLocalError on the
        # `if fin is not None` checks further down the page.
        info, hist, fin, bs, cf = {}, None, None, None, None
        _network_issue = False
        with st.spinner(f"Fetching data for {ticker}..."):
            try:
                info, hist, fin, bs, cf = fetch_stock(ticker)
            except Exception as _fetch_exc:
                if _is_connectivity_error(_fetch_exc):
                    _network_issue = True
                # info stays {} and the rest stay None; handled below

        # Final safety net — if even the picked ticker has no live data, try one more search
        if not info.get("currentPrice") and not info.get("regularMarketPrice"):
            with st.spinner("Verifying ticker..."):
                fallback_matches = search_nse_matches(ticker.replace(".NS", ""))
            for sym, lname in fallback_matches:
                if sym != ticker:
                    try:
                        alt_info, alt_hist, alt_fin, alt_bs, alt_cf = fetch_stock(sym)
                        if alt_info.get("currentPrice") or alt_info.get("regularMarketPrice"):
                            info, hist, fin, bs, cf = alt_info, alt_hist, alt_fin, alt_bs, alt_cf
                            ticker = sym
                            st.info(f"Note: resolved to **{sym}** ({lname}) — the original ticker didn't return live data.")
                            break
                    except Exception as _fallback_exc:
                        if _is_connectivity_error(_fallback_exc):
                            _network_issue = True
                        continue

        if not info.get("currentPrice") and not info.get("regularMarketPrice"):
            _input_label = st.session_state.get("last_search_term") or ticker
            if _network_issue:
                st.error(
                    f"Could not fetch live data for '{_input_label}' — no internet connection detected. "
                    f"EquiEye AI needs an active connection to fetch live prices, financials, and news. "
                    f"Please check your connection and try again."
                )
            else:
                st.error(f"Could not fetch live data for '{_input_label}'. This may be due to a recent listing change, demerger, or temporary Yahoo Finance issue. Try the exact NSE ticker (e.g. RELIANCE.NS).")
            st.stop()

        name = info.get("longName", ticker)
        price = info.get("currentPrice") or info.get("regularMarketPrice")
        prev_close = info.get("previousClose")
        mkt_cap = info.get("marketCap")
        pe = info.get("trailingPE")
        roe = info.get("returnOnEquity")
        de = info.get("debtToEquity")
        # totalRevenue used in the AI prompt via fmt_crore(rev) — keep it.
        rev = info.get("totalRevenue")
        profit_margin = info.get("profitMargins")
        sector = info.get("sector", "")
        industry = info.get("industry", "")
        description = info.get("longBusinessSummary", "")

        price_chg = pct(price, prev_close)

        # ── Price strip ──────────────────────────────────────────────────────
        wl_header_col, wl_btn_col = st.columns([6, 1])
        with wl_header_col:
            st.markdown(f"<h2 style='color:#111827; font-size:1.8rem; margin:1.2rem 0 0.6rem;'>{name} <span style='color:#5B6673; font-size:1.2rem;'>({ticker})</span></h2>", unsafe_allow_html=True)
        with wl_btn_col:
            if "watchlist" not in st.session_state:
                st.session_state.watchlist = []
            already_watched = any(s == ticker for s, _ in st.session_state.watchlist)
            if already_watched:
                st.markdown("<div style='margin-top:1.2rem;'></div>", unsafe_allow_html=True)
                if st.button("⭐ Watching", key="wl_toggle", help="Remove from watchlist"):
                    st.session_state.watchlist = [(s, n) for s, n in st.session_state.watchlist if s != ticker]
                    st.rerun()
            else:
                st.markdown("<div style='margin-top:1.2rem;'></div>", unsafe_allow_html=True)
                if st.button("☆ Watchlist", key="wl_toggle", help="Add to watchlist"):
                    st.session_state.watchlist.append((ticker, name))
                    st.success(f"Added {name} to watchlist!")
                    st.rerun()

        chg_color = TXT_GOOD if (price_chg and price_chg > 0) else TXT_MUTED if not price_chg or price_chg == 0 else TXT_BAD
        chg_str = f"{price_chg:+.2f}%" if price_chg is not None else ""
        # Built as one HTML string inside a CSS grid (.metric-strip) rather
        # than st.columns(5) — Streamlit's columns auto-stack to a single
        # full-width column below ~640px with no guaranteed gap, which is
        # what caused the cards to run into each other on phone. The grid
        # keeps a fixed gap and drops to 2-per-row on narrow screens instead.
        _metrics_html = "".join([
            mcard_html("Price", f"₹{price:,.1f}" if price else "N/A", chg_str, chg_color),
            mcard_html("Market Cap", fmt_crore(mkt_cap)),
            # Use explicit `is not None` for pe/roe/de so a genuine value of 0
            # (e.g. zero debt, or a company that just turned profitable) displays
            # correctly instead of being swallowed by a falsy check.
            mcard_html("P/E Ratio", f"{pe:.1f}x" if pe is not None else "N/A"),
            mcard_html("ROE", f"{roe*100:.1f}%" if roe is not None else "N/A"),
            # yfinance returns debtToEquity in percentage form for NSE stocks
            # (e.g. 14.826 means a D/E ratio of 0.15). Divide by 100 for display.
            mcard_html("Debt/Equity", fmt_de(de)),
        ])
        st.markdown(f"<div class='metric-strip'>{_metrics_html}</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Investment holding company bypass ───────────────────────────────
        # Pure holdcos (JSW Holdings, Bajaj Holdings, etc.) don't operate a
        # business themselves — they just hold equity stakes in other listed
        # companies and pass through dividend income. Running them through
        # the normal sector-detection → health-score → red-flag pipeline
        # was producing actively wrong output: sector detection had no good
        # slug for this (falls through to an LLM guess like "banking"),
        # dividend-income "revenue" false-triggered the Red Flag Detector's
        # revenue-decline check, margins looked absurd (70-95%+, no COGS
        # against dividend income), and the AI business description was
        # observed hallucinating the parent GROUP's operating businesses
        # (steel/energy/cement/etc. for JSW Holdings) as the holdco's own.
        # Rather than force these through frameworks built for operating
        # companies, show an honest notice and stop here. This deliberately
        # does NOT attempt NAV/discount-to-holdings valuation — that's a
        # real, separate feature, not built as part of this bypass.
        from modules.sectors.holding_companies import get_holding_company_match, compute_nav_discount
        _holdco = get_holding_company_match(name)
        if _holdco:
            if _holdco.get("hybrid_operating"):
                st.warning(
                    f"**{name} is a hybrid: a real operating business plus a large holding "
                    f"structure.** It runs {_holdco.get('operating_business', 'its own operating business')}, "
                    f"but a substantial share of its market value also comes from equity stakes "
                    f"it holds in {_holdco['holds_stakes_in']} — companies that are separately "
                    f"listed and already get their own full analysis (health score, moat, AI "
                    f"summary) on their own tickers in this app.\n\n"
                    f"Blending the standalone chemicals business with pass-through stake value "
                    f"into one health-score/AI summary here would double-count those subsidiaries "
                    f"and risk a confused, hard-to-parse write-up — so the full analysis pipeline "
                    f"is skipped for this ticker. Look up the subsidiaries directly for their own "
                    f"full analysis, or see the stakes-only NAV comparison below."
                )
            else:
                st.warning(
                    f"**{name} is an investment holding company, not an operating business.** "
                    f"It primarily holds equity stakes in {_holdco['holds_stakes_in']} and earns "
                    f"dividend/interest income from those stakes, rather than running its own "
                    f"operating business.\n\n"
                    f"Standard health-score, red-flag, and margin analysis (built for operating "
                    f"companies) don't meaningfully apply here — dividend income is lumpy by "
                    f"nature and can look like fake growth/decline swings, and margins can look "
                    f"unrealistically high since there's no cost of goods against dividend income.\n\n"
                    f"The sections below (Financial Health, Risk Meter, Red Flags, AI-written "
                    f"business summary) are skipped rather than shown with misleading numbers."
                )

            # NAV vs. market-cap discount — only computable for holdcos with
            # curated stake data (see modules/sectors/holding_companies.py).
            # fetch_quote() shares fetch_stock()'s 5-min cache/retry behaviour
            # but skips financials/history/balance-sheet/cashflow, which this
            # only needs one `info` field from — full fetch_stock() would
            # fire 3 wasted extra yfinance requests per stake.
            def _fetch_mcap(ticker: str):
                try:
                    return fetch_quote(ticker).get("marketCap")
                except Exception:
                    return None

            _nav = compute_nav_discount(_holdco, mkt_cap, _fetch_mcap)
            if _nav:
                disc = _nav["discount_pct"]
                disc_label = (
                    f"trading at a **{disc:.1f}% discount to NAV**" if disc is not None and disc >= 0
                    else f"trading at a **{abs(disc):.1f}% premium to NAV**" if disc is not None
                    else "NAV comparison unavailable"
                )
                st.markdown("### Net Asset Value (NAV) vs. Market Cap")
                if _holdco.get("hybrid_operating"):
                    st.markdown(
                        f"**{name}**'s three listed subsidiary stakes alone are worth "
                        f"{fmt_crore(_nav['nav'])}, against a total company market cap of "
                        f"{fmt_crore(_nav['holdco_market_cap'])}. This is NOT a discount/premium "
                        f"figure — the gap includes the market's own valuation of the standalone "
                        f"chemicals business (not just holdco-structure discounting), so treat it "
                        f"as directional context, not a NAV mispricing signal."
                    )
                else:
                    st.markdown(
                        f"**{name}** is {disc_label} — "
                        f"NAV {fmt_crore(_nav['nav'])} vs. market cap {fmt_crore(_nav['holdco_market_cap'])}."
                    )
                for s in _nav["stake_details"]:
                    st.markdown(
                        f"- **{s['name']}** ({s['ticker']}): {s['ownership_pct']:.2f}% stake worth "
                        f"{fmt_crore(s['stake_value'])} (subsidiary market cap {fmt_crore(s['market_cap'])})"
                    )
                if _nav["unresolved_stakes"]:
                    st.caption(
                        f"Couldn't fetch a live price for: {', '.join(_nav['unresolved_stakes'])} — "
                        f"NAV above excludes these and is understated accordingly."
                    )
                if _holdco.get("hybrid_operating"):
                    st.caption(
                        f"⚠️ {_holdco.get('nav_note', '')} See modules/sectors/holding_companies.py "
                        f"for stake sourcing and confidence notes."
                    )
                else:
                    st.caption(
                        f"⚠️ {_holdco.get('nav_note', '')} NAV is a floor based on curated stakes only, "
                        f"not the complete holding portfolio — see modules/sectors/holding_companies.py "
                        f"for what's included/excluded and why. Indian holding companies structurally "
                        f"trade at persistent discounts to NAV (commonly 30-70%); a wide discount alone "
                        f"isn't automatically a buy signal — it reflects the market's long-standing "
                        f"discounting of holdco structures (governance/liquidity/tax-on-unlock concerns), "
                        f"not necessarily mispricing."
                    )
            else:
                st.info(
                    f"NAV vs. market-cap comparison isn't available yet for {name} — "
                    f"stake-by-stake data hasn't been curated for this holdco. "
                    f"{_holdco.get('nav_note', '')}"
                )
            st.stop()

        # ── Parallel fetch: Wikipedia + CAGR prep (non-LLM work done first) ──
        # Wikipedia is cached 24h so it's usually instant on repeat visits.
        # We still kick it off here before building the prompt so we have the
        # context ready; the actual LLM calls are parallelised below.
        try:
            wiki_context = fetch_wikipedia_context(name)
        except Exception:
            wiki_context = ""

        if wiki_context:
            business_context = wiki_context
            context_source = "Wikipedia"
        elif description and len(description.strip()) > 100:
            business_context = description[:1500]
            context_source = "company filing"
        else:
            business_context = (
                "No business description available. Base the \"business\" field ONLY on the "
                "Sector classification given below (e.g. \"an Engineering R&D / product engineering "
                "services company\" if classified as Engineering R&D, \"an enterprise IT services "
                "company\" if classified as IT Services) — do not invent specific clients, products, "
                "revenue mix, or other facts beyond what the classification implies."
            )
            context_source = "sector classification only"

        # ── Compute CAGR from financials ──────────────────────────────────────
        rev_cagr = None
        profit_cagr = None
        profit_growth_pct = None
        revenue_growth_pct = None  # YoY revenue growth — used by health score fallback
        rev_cagr_years = None      # number of years spanned by rev_cagr
        profit_cagr_years = None   # number of years spanned by profit_cagr
        rev_had_break = False      # True if a corporate-action discontinuity was trimmed off
        profit_had_break = False

        # `fin` may silently be quarterly_financials instead of annual (see
        # fetch_stock's fallback). Treating quarter-spaced columns as if
        # they were year-spaced would: (a) badly distort the CAGR exponent
        # — e.g. 4 quarters (~1 year of real elapsed time) mislabeled and
        # computed as "3-yr CAGR", flattening the true growth rate — and
        # (b) turn "YoY" growth into an accidental quarter-over-quarter
        # comparison. Both feed the Growth pillar directly (the same one
        # just retuned for it_services), so a silent quarterly fallback
        # here would undermine that calibration. Detected once (via the
        # shared, stub-period-robust classifier) and reused below by the
        # derived balance-sheet metrics block and the Revenue/Net Profit
        # Trend chart pills too — all three CAGR code paths must agree on
        # this classification, or they silently contradict each other.
        _fin_is_quarterly = _is_quarterly_financials(fin)

        try:
            if fin is not None and not fin.empty and not _fin_is_quarterly:
                # Revenue CAGR + YoY
                for rev_key in ["Total Revenue", "Revenue", "Total Revenues"]:
                    if rev_key in fin.index:
                        rev_series = fin.loc[rev_key].dropna().sort_index()
                        # Corporate-action guard (demerger/spinoff/major M&A
                        # stitching a differently-sized entity's history onto
                        # one ticker — see _trim_to_last_discontinuity) —
                        # without this, a company like TMCV.NS (post-Tata
                        # Motors demerger) computes a fabricated "-56% CAGR"
                        # from comparing the old combined group's revenue to
                        # the new standalone CV-only entity's revenue.
                        rev_series, rev_had_break = _trim_to_last_discontinuity(rev_series)
                        if len(rev_series) >= 2:
                            oldest = rev_series.iloc[0]
                            newest = rev_series.iloc[-1]
                            n_years = max(len(rev_series) - 1, 1)
                            rev_cagr_years = n_years   # ← store for display label
                            if oldest > 0:
                                rev_cagr = ((newest / oldest) ** (1 / n_years) - 1) * 100
                            # YoY for health score fallback (mirrors profit_growth_pct pattern)
                            prev_rev = rev_series.iloc[-2]
                            if prev_rev is not None and prev_rev != 0:
                                revenue_growth_pct = ((newest - prev_rev) / abs(prev_rev)) * 100
                        break
                # Profit CAGR
                for p_key in ["Net Income", "Net Income Common Stockholders", "Net Income From Continuing Operations"]:
                    if p_key in fin.index:
                        p_series = fin.loc[p_key].dropna().sort_index()
                        p_series, profit_had_break = _trim_to_last_discontinuity(p_series)
                        if len(p_series) >= 2:
                            oldest_p = p_series.iloc[0]
                            newest_p = p_series.iloc[-1]
                            n_years_p = max(len(p_series) - 1, 1)
                            profit_cagr_years = n_years_p   # ← store for display label
                            # CAGR requires both ends positive (log undefined for negatives)
                            if oldest_p > 0 and newest_p > 0:
                                profit_cagr = ((newest_p / oldest_p) ** (1 / n_years_p) - 1) * 100
                            # YoY: always compute when base is non-zero, even for
                            # turnaround companies (negative→positive base year).
                            # Used in snap_metrics as profit_cagr_display fallback
                            # and in health score growth sub-score.
                            prev_p = p_series.iloc[-2]
                            if prev_p is not None and prev_p != 0:
                                profit_growth_pct = ((newest_p - prev_p) / abs(prev_p)) * 100
                        break
            elif fin is not None and not fin.empty and _fin_is_quarterly:
                # Quarterly fallback: no genuine multi-year span to CAGR, so
                # leave rev_cagr/profit_cagr as None (honest "no data") rather
                # than mislabel N quarters as N years. Still compute a true
                # YoY by comparing against the same quarter a year ago (4
                # quarters back) when enough history is present — comparing
                # adjacent quarters instead would silently be QoQ, not YoY.
                for rev_key in ["Total Revenue", "Revenue", "Total Revenues"]:
                    if rev_key in fin.index:
                        rev_series = fin.loc[rev_key].dropna().sort_index()
                        rev_series, rev_had_break = _trim_to_last_discontinuity(rev_series)
                        if len(rev_series) >= 5:
                            newest = rev_series.iloc[-1]
                            year_ago = rev_series.iloc[-5]
                            if year_ago is not None and year_ago != 0:
                                revenue_growth_pct = ((newest - year_ago) / abs(year_ago)) * 100
                        elif len(rev_series) >= 2:
                            # Discontinuity trimmed us below a 4-quarter span
                            # for true YoY — fall back to comparing the two
                            # most recent (adjacent) quarters rather than
                            # showing nothing, but this is QoQ, not YoY, so
                            # don't label it as YoY growth downstream.
                            pass
                        break
                for p_key in ["Net Income", "Net Income Common Stockholders", "Net Income From Continuing Operations"]:
                    if p_key in fin.index:
                        p_series = fin.loc[p_key].dropna().sort_index()
                        p_series, profit_had_break = _trim_to_last_discontinuity(p_series)
                        if len(p_series) >= 5:
                            newest_p = p_series.iloc[-1]
                            year_ago_p = p_series.iloc[-5]
                            if year_ago_p is not None and year_ago_p != 0:
                                profit_growth_pct = ((newest_p - year_ago_p) / abs(year_ago_p)) * 100
                        break
        except Exception:
            pass

        # ── Derived balance-sheet/income-statement metrics ──────────────────
        # These feed sector red_flags rules (metals_mining/telecom's
        # net_debt_ebitda, renewable_energy's interest_coverage) and
        # scoring buckets that were previously always "missing_data" —
        # yfinance's `info` dict doesn't expose them directly, but they're
        # derivable from the same `bs`/`fin` statement dataframes already
        # loaded for the CAGR calc above. Best-effort: any missing line
        # item (naming varies by ticker/statement vintage) just leaves the
        # metric as None rather than breaking the page.
        def _latest_stmt_value(df, candidate_keys):
            if df is None or df.empty:
                return None
            for key in candidate_keys:
                if key in df.index:
                    series = df.loc[key].dropna().sort_index()
                    if len(series) >= 1:
                        return series.iloc[-1]
            return None

        net_debt_ebitda_val = None
        interest_coverage_val = None
        receivable_days_val = None
        inventory_months_val = None
        try:
            # `_fin_is_quarterly` / `_annualize` computed once above, before
            # the CAGR block — reused here for the same reason.
            _annualize = 4 if _fin_is_quarterly else 1

            total_debt_val = _latest_stmt_value(bs, ["Total Debt"])
            cash_val = _latest_stmt_value(bs, [
                "Cash And Cash Equivalents",
                "Cash Cash Equivalents And Short Term Investments",
                "Cash",
            ])
            ebitda_val = info.get("ebitda")
            if total_debt_val is not None and ebitda_val:
                net_debt_val = total_debt_val - (cash_val or 0)
                net_debt_ebitda_val = net_debt_val / ebitda_val

            ebit_val = _latest_stmt_value(fin, ["EBIT", "Operating Income"])
            interest_exp_val = _latest_stmt_value(fin, [
                "Interest Expense", "Interest Expense Non Operating",
            ])
            if ebit_val is not None and interest_exp_val:
                interest_coverage_val = ebit_val / abs(interest_exp_val)

            receivables_val = _latest_stmt_value(bs, [
                "Receivables", "Accounts Receivable", "Net Receivables",
            ])
            revenue_latest_val = _latest_stmt_value(fin, [
                "Total Revenue", "Revenue", "Total Revenues",
            ])
            if revenue_latest_val is not None:
                revenue_latest_val *= _annualize
            else:
                # info["totalRevenue"] is already TTM/annual — safe as-is,
                # no annualization needed.
                revenue_latest_val = info.get("totalRevenue")
            if receivables_val is not None and revenue_latest_val:
                receivable_days_val = (receivables_val / revenue_latest_val) * 365

            inventory_val = _latest_stmt_value(bs, ["Inventory"])
            cogs_val = _latest_stmt_value(fin, [
                "Cost Of Revenue", "Reconciled Cost Of Revenue",
            ])
            if cogs_val is not None:
                cogs_val *= _annualize
            if inventory_val is not None and cogs_val:
                inventory_months_val = (inventory_val / cogs_val) * 12
        except Exception:
            pass

        # ── Recent news context (for grounding bull/bear in real events) ───────
        # Reuses the same cached fetch_relevant_news() the Latest News section
        # calls later — @st.cache_data means this costs a real NewsAPI request
        # only once per (ticker, name) within the 15-min TTL; the later call
        # is a cache hit, not a second network round trip.
        # Deliberately best-effort: any failure (no key, rate limit, network
        # error) must never block the main analysis — it just means bull/bear
        # falls back to metrics-only reasoning, exactly as it did before this.
        _news_context_block = ""
        try:
            _news_result_early = fetch_news_for_llm_context(ticker, name)
            if not _news_result_early.get("error"):
                _headline_lines = []
                for _art in _news_result_early.get("relevant_articles", [])[:3]:
                    _title = (_art.get("title") or "").strip()
                    _date = (_art.get("publishedAt") or "")[:10]
                    if _title:
                        _headline_lines.append(f"- ({_date}) {_title}" if _date else f"- {_title}")
                if _headline_lines:
                    _news_context_block = (
                        "RECENT NEWS HEADLINES (context only — these are FOR YOUR AWARENESS, "
                        "not designated metric variables):\n" + "\n".join(_headline_lines) + "\n"
                        "If — and only if — one of these is genuinely relevant to a bull or bear "
                        "point, you may reference its general theme in your own words. NEVER copy "
                        "a headline's wording verbatim (paraphrase completely). NEVER invent "
                        "specifics (numbers, dates, causes) beyond what the headline itself states — "
                        "a headline is a topic pointer, not a data source to extrapolate from. If none "
                        "of these are relevant, ignore this section entirely and reason from the "
                        "metrics above as usual."
                    )
        except Exception:
            _news_context_block = ""

        # ── Sector slug (granular) — computed once, used for both the LLM
        # sector hint below AND the numeric-metric exclusions further down.
        # Deliberately more precise than the raw yfinance `sector` field:
        # yfinance lumps banks, NBFCs, insurers, and fintechs all under one
        # "Financial Services" bucket, but they need different treatment
        # (e.g. fintech genuinely has a real EBITDA margin; a bank doesn't).
        _fin_slug = ""
        if _MODULES_LOADED:
            try:
                from modules.sector_analysis import classify_sector as _cls_early
                _fin_slug = _cls_early(sector, industry, name, business_context)
            except Exception:
                _fin_slug = ""

        # ── Sector context ────────────────────────────────────────────────────
        # NOTE: this used to pass only the FIRST SENTENCE of llm_context
        # (via .split(".")[0]) to "keep the prompt compact". That silently
        # discarded the substantive part of every sector module's
        # intelligence — e.g. for defense_aerospace, everything about
        # single-customer concentration, government-budget-driven demand,
        # the licensing/security-clearance moat, and execution-delay risk
        # was cut before the LLM ever saw it, leaving only the generic
        # opening clause. That's why bull/bear/snapshot output for sectors
        # like defense read as generic Industrials-style boilerplate
        # instead of using the rich, sector-specific content that already
        # exists in modules/sectors/*.py. The token cost of the full
        # paragraph (~150-250 words) is trivial against Groq's context
        # window and unrelated to the earlier *output*-token truncation
        # issue (that was fixed separately via max_tokens=1700 below).
        sector_prompt_addition = ""
        _cfg_display_name = ""
        _sector_cfg_full = None
        if _MODULES_LOADED and _fin_slug:
            try:
                from modules.sectors import get_sector_config
                _cfg = get_sector_config(_fin_slug)
                _sector_cfg_full = _cfg
                sector_prompt_addition = f"SECTOR INTELLIGENCE: {_cfg['llm_context']}"
                _cfg_display_name = _cfg.get("display_name", "")
            except Exception:
                pass

        # ── Combined AI analysis ──────────────────────────────────────────────
        # D/E is meaningless for a deposit-funded bank, and for NBFC/insurance
        # balance sheets it's structurally different from a normal corporate's
        # (borrowings fund the lending book / policy reserves by design) — so
        # it isn't a useful "leverage" signal for any of these three. Fintech
        # is excluded from this gate: it's a real corporate-style metric there.
        _no_conventional_bs = _fin_slug in ("banking", "nbfc", "insurance")
        de_display = "N/A" if _no_conventional_bs else (
            f"{de/100:.2f}" if de is not None else "N/A"
        )
        roe_display = f"{roe*100:.1f}%" if roe is not None else "N/A"
        pm_display = f"{profit_margin*100:.2f}%" if profit_margin is not None else "N/A"
        pe_display = f"{pe:.1f}" if pe is not None else "N/A"
        # CAGR display strings — always include the number of years so "CAGR"
        # is never paired with a single-year or ambiguous timeframe.
        # Format: "{X}-yr CAGR: {Y}%" so the LLM and UI are unambiguous.
        _discontinuity_note = (
            " (data reset — an implausible single-year swing was detected; "
            "possible causes include a demerger/spinoff/major restructuring, "
            "a one-off item, or a cyclical loss-to-profit turnaround/low-base "
            "effect (e.g. post-pandemic demand recovery); CAGR window "
            "shortened to exclude the pre-break period)"
        )
        if rev_cagr is not None and rev_cagr_years is not None:
            rev_cagr_display = f"{rev_cagr_years}-yr CAGR: {rev_cagr:.1f}%"
            if rev_had_break:
                rev_cagr_display += _discontinuity_note
        else:
            rev_cagr_display = "N/A" + (_discontinuity_note if rev_had_break else "")

        # For turnaround companies (loss→profit), profit_cagr is undefined but
        # YoY growth is real and large.  Surface it as "YoY +X%" in the prompt
        # so the LLM doesn't treat a newly profitable company as having no growth.
        if profit_cagr is not None and profit_cagr_years is not None:
            profit_cagr_display = f"{profit_cagr_years}-yr CAGR: {profit_cagr:.1f}%"
            if profit_had_break:
                profit_cagr_display += _discontinuity_note
        elif profit_growth_pct is not None:
            profit_cagr_display = f"N/A (YoY {profit_growth_pct:+.1f}%)"
        else:
            profit_cagr_display = "N/A" + (_discontinuity_note if profit_had_break else "")

        # ── Extra metrics for snapshot enrichment ────────────────────────────
        # Banks/NBFCs/insurers don't have a meaningful EBITDA or FCF figure in
        # the conventional sense (see health_score.py: "Banks NEVER use D/E,
        # EBITDA Margin, or FCF" — the same holds for NBFC/insurance balance
        # sheets). yfinance often still returns 0 (not None) for these fields
        # on Indian banks, which previously slipped through as a fake "0.00%"
        # data point the LLM then cited as real evidence (e.g. a bogus "margin
        # compression" bear point for ICICI Bank). Force these to None for
        # banking/nbfc/insurance only — fintech is deliberately excluded since
        # its own sector module (fintech.py) scores real EBITDA margin data.
        _pb_val     = info.get("priceToBook")
        _cur_ratio  = info.get("currentRatio")
        _beta       = info.get("beta")
        _ebitda_m   = None if _no_conventional_bs else info.get("ebitdaMargins")
        _fcf        = None if _no_conventional_bs else info.get("freeCashflow")
        _ocf        = info.get("operatingCashflow")

        # ── Fix 3: Dividend Yield sanity guard ───────────────────────────────
        # yfinance's `dividendYield` field is unreliable for Indian stocks:
        # it can return the total annual payout in rupees instead of the
        # decimal yield, or confuse payout ratio with yield, producing values
        # like 1.73 (173%) for Britannia whose real yield is ~1.5-2%.
        # Strategy:
        #   1. Always prefer computing from scratch: (DPS / price) if available.
        #   2. If DPS is missing, fall back to the raw field BUT clamp to 30%
        #      max — no equity dividend yield legitimately exceeds that.
        #   3. If the clamped value still looks like a payout ratio (> 1.0 raw,
        #      i.e. > 100%), discard it entirely and show N/A.
        _dps   = info.get("lastDividendValue") or info.get("dividendRate")
        _raw_yield = info.get("dividendYield")
        if _dps and price:
            try:
                _computed_yield = float(_dps) / float(price)
                # Sanity: must be between 0 and 30%
                _div_yield = _computed_yield if 0 < _computed_yield <= 0.30 else None
            except Exception:
                _div_yield = None
        elif _raw_yield is not None:
            try:
                _ry = float(_raw_yield)
                # Raw values > 0.30 (30%) are almost certainly mis-scaled
                _div_yield = _ry if 0 < _ry <= 0.30 else None
            except Exception:
                _div_yield = None
        else:
            _div_yield = None

        def _sfmt(v, mult=1, suffix="", digits=1):
            """Safe format — returns N/A for None/NaN."""
            import math
            if v is None:
                return "N/A"
            try:
                fv = float(v) * mult
                if not math.isfinite(fv):
                    return "N/A"
                return f"{fv:.{digits}f}{suffix}"
            except Exception:
                return "N/A"

        # ── Named metric variables — single source of truth for the prompt ──────
        # Every value is formatted exactly once here.  The LLM receives named
        # variables and is instructed to copy them verbatim, preventing any
        # rounding or truncation divergence between sections.
        _ttm_net_margin   = pm_display                                         # e.g. "13.23%"
        _ttm_revenue      = fmt_crore(rev)                                     # e.g. "₹19.2K Cr"
        _ttm_ebitda_m     = _sfmt(_ebitda_m, mult=100, suffix="%", digits=2)  # e.g. "18.45%"
        _mkt_cap          = fmt_crore(mkt_cap)                                 # e.g. "₹1.26 Lakh Cr"
        _pe_display       = f"{pe_display}x" if pe_display != "N/A" else "N/A"
        _pb_display       = _sfmt(_pb_val, digits=2) + "x"
        _roe_display      = roe_display                                        # e.g. "53.3%"
        # ROA — the primary profitability yardstick for banks/NBFCs (asset
        # turnover matters more than margin when the "product" is a loan
        # book). Already scored internally by health_score.py; this exposes
        # the same real yfinance figure to the LLM so bull/bear points about
        # "Return Ratios" can cite ROA alongside ROE instead of ROE alone.
        _roa_val          = info.get("returnOnAssets")
        _roa_display      = _sfmt(_roa_val, mult=100, suffix="%", digits=2)
        _de_display       = de_display + "x"                                   # e.g. "0.27x"
        _cur_ratio_disp   = _sfmt(_cur_ratio, digits=2)
        _div_yield_disp   = _sfmt(_div_yield, mult=100, suffix="%", digits=2)
        _beta_disp        = _sfmt(_beta, digits=2)
        _fcf_disp         = fmt_crore(_fcf)
        _rev_cagr_disp_lbl  = rev_cagr_display   # already "{N}-yr CAGR: {X.X}%"
        _prof_cagr_disp_lbl = profit_cagr_display # already "{N}-yr CAGR: {X.X}%"

        snap_metrics = (
            f"[TTM METRICS] P/E={_pe_display} | P/B={_pb_display} | "
            f"ROE={_roe_display} | ROA={_roa_display} | ROCE=N/A | "
            f"D/E={_de_display} | Current Ratio={_cur_ratio_disp} | "
            f"TTM Net Margin={_ttm_net_margin} | TTM EBITDA Margin={_ttm_ebitda_m} | "
            f"Market Cap={_mkt_cap} | TTM Revenue={_ttm_revenue} | "
            f"FCF={_fcf_disp} | "
            f"Dividend Yield={_div_yield_disp} | "
            f"Beta={_beta_disp}"
            f"\n[HISTORICAL FY METRICS — from annual financials, NOT TTM] "
            f"Revenue CAGR={_rev_cagr_disp_lbl} | Profit CAGR={_prof_cagr_disp_lbl}"
        )

        # ── Sector class guardrail (static dict defined at module level) ────────
        # Prefer the granular slug override (banking/nbfc/insurance) when we
        # have one — it's more precise than the coarse yfinance sector label
        # and prevents bank-only guidance (CASA, NIM) from leaking onto
        # insurance/NBFC companies, or vice versa.
        if _fin_slug in _FIN_SLUG_CLASS_MAP:
            _sec_class_label, _sec_class_rule = _FIN_SLUG_CLASS_MAP[_fin_slug]
        elif _sector_cfg_full is not None:
            # A dedicated sector module exists (defense_aerospace, fmcg,
            # media, cement, etc.) but wasn't one of the ~5 hardcoded
            # entries above — previously this fell through to the generic
            # default below and lost all of that module's real economics.
            # Ground the guardrail in the module's own bull_case/bear_case
            # theme lists so bull/bear headlines reflect what actually
            # drives THIS sector (e.g. government budget allocation and
            # customer concentration for defense) instead of generic
            # "Competition"/"Economic Downturn" filler.
            # Capped at top-4 (not top-5) — the LLM only ever outputs 3 bull
            # and 3 bear headlines, so 5 themes was already more choice than
            # needed; 4 still leaves one spare option for a better-fitting
            # theme while trimming prompt size uniformly across every
            # sector (part of a broader pass to reduce prompt bloat without
            # losing distinct guidance — see sector module docstrings for
            # the per-sector llm_context tightening that accompanied this).
            _bull_themes = "; ".join(_sector_cfg_full.get("bull_case", [])[:4])
            _bear_themes = "; ".join(_sector_cfg_full.get("bear_case", [])[:4])
            _sec_class_label = _sector_cfg_full.get("display_name", sector or "UNCLASSIFIED").upper()
            _sec_class_rule = (
                f"{_sector_cfg_full['llm_context']} "
                f"BULL HEADLINES should draw their theme from (paraphrase in your own words, don't copy "
                f"verbatim, and still ground the explanation in a designated metric where one applies): "
                f"{_bull_themes}. "
                f"BEAR HEADLINES should draw their theme from (same rule — paraphrase, don't copy verbatim): "
                f"{_bear_themes}. Do NOT default to generic 'Competition From Global Players' or 'Economic "
                f"Downturn' framing when a more specific, sector-grounded risk from the list above applies "
                f"— this sector's demand and risk drivers are structurally different from a normal cyclical "
                f"industrial business."
            )
        else:
            _sec_class_label, _sec_class_rule = _SECTOR_CLASS_MAP.get(
                sector,
                (sector or "UNCLASSIFIED", "use sector-specific risks grounded in the company description above.")
            )

        # ── Financials snapshot example — sector-branched ────────────────────
        # Uses literal {{roa}}/{{roe}}/{{ttm_net_margin}}/{{ttm_ebitda_margin}}/
        # {{rev_cagr}} tokens (double-braced so they survive this f-string as
        # designated variables for the LLM to copy verbatim — see METRIC
        # USAGE RULES above, same mechanism as every other {{token}} in this
        # prompt).
        # Falls back to the Net Margin/Revenue CAGR syntax even for a
        # bank/NBFC if BOTH roa and roe are unavailable from yfinance for
        # this specific ticker (happens on smaller-cap/less-covered stocks —
        # e.g. AU Small Finance Bank had neither populated) — otherwise the
        # card would literally read "Return on Assets of N/A and Return on
        # Equity of N/A" while real net-margin data sat unused right there.
        _roa_or_roe_available = (_roa_val is not None) or (roe is not None)

        # Net margin exceeding EBITDA margin is not achievable through
        # normal operations — EBITDA margin is always >= net margin once
        # D&A, interest, and tax are subtracted. When it happens anyway,
        # that's a reliable signal of a non-operating or exceptional gain
        # inflating reported net income (e.g. a demerger-related fair-value
        # or disposal gain — see TMPV.NS, where TTM Net Margin read ~24%
        # against a much smaller EBITDA margin). Distinct from the
        # discontinuity guard above: that catches a fabricated *trend*
        # across a corporate-action break; this catches a single period's
        # net income itself being contaminated by a one-off item.
        _net_margin_pct = profit_margin * 100 if profit_margin is not None else None
        _ebitda_margin_pct_raw = _ebitda_m * 100 if _ebitda_m is not None else None
        _net_margin_exceeds_ebitda = (
            _net_margin_pct is not None and _ebitda_margin_pct_raw is not None
            and _net_margin_pct > _ebitda_margin_pct_raw + 0.5   # small buffer for rounding noise
        )
        # Absolute sanity ceiling, independent of EBITDA data availability.
        # No normal operating business sustains >100% net margin — net
        # profit exceeding revenue itself is only mathematically possible
        # via a non-operating gain (asset sale, settlement, licensing
        # windfall, etc.). This catches what the EBITDA-comparison check
        # above misses entirely: when EBITDA margin data isn't available
        # at all (common on smaller/thinly-covered tickers), or when the
        # one-off item is booked in a way that inflates EBITDA too (so net
        # margin isn't "worse than" EBITDA margin, yet both are still
        # absurd) — see SPARC.NS, TTM Net Margin 3967% on ~₹39 Cr TTM
        # revenue, where EBITDA margin data was unavailable and the
        # EBITDA-comparison check alone silently found nothing wrong.
        _net_margin_impossible = _net_margin_pct is not None and _net_margin_pct > 100
        _net_margin_anomalous = _net_margin_exceeds_ebitda or _net_margin_impossible

        if _fin_slug in ("banking", "nbfc") and _roa_or_roe_available:
            _fin_display_syntax = (
                "The company's financial health is underscored by its Return on Assets of {roa} "
                "and Return on Equity of {roe}, reflecting [qualitative insight]."
            )
        elif _net_margin_anomalous and _ebitda_margin_pct_raw is not None:
            _fin_display_syntax = (
                "The company's financial health is underscored by its TTM EBITDA Margin of {ttm_ebitda_margin} "
                "and a {rev_cagr} — note reported net margin is far above a sustainable operating level, "
                "which points to a non-operating or exceptional gain rather than core operating profitability, "
                "so EBITDA margin is the more reliable read here."
            )
        elif _net_margin_anomalous:
            # EBITDA margin itself isn't available to cite as a replacement
            # — fall back to a generic caveat without a specific
            # alternative number, rather than silently reverting to the
            # unreliable net margin as if nothing were wrong.
            _fin_display_syntax = (
                "The company's reported TTM Net Margin of {ttm_net_margin} is not a reliable measure of core "
                "operating profitability — a margin this extreme relative to revenue almost certainly reflects "
                "a non-operating or exceptional gain (e.g. an asset sale, settlement, or licensing windfall) "
                "rather than the underlying business. [one-line qualitative insight about the business itself, "
                "not the margin]."
            )
        else:
            _fin_display_syntax = (
                "The company's financial health is underscored by its TTM Net Margin of {ttm_net_margin} "
                "and a {rev_cagr}, reflecting [qualitative insight]."
            )

        # combined_prompt: extracted verbatim to services/prompts.py's
        # build_combined_prompt() — verified byte-identical output against
        # the original inline f-string across 4 branch combinations
        # (normal/anomalous net margin, with/without EBITDA, banking vs
        # generic financials syntax). The upstream logic that computed
        # every argument below (_sec_class_label, _sec_class_rule,
        # _fin_display_syntax, _net_margin_anomalous, etc.) is unchanged.
        combined_prompt = build_combined_prompt(
            name, ticker, sector, _cfg_display_name, industry, _sec_class_label, _sec_class_rule,
            _ttm_net_margin, _ttm_revenue, _ttm_ebitda_m, _mkt_cap, _pe_display, _pb_display,
            _roe_display, _roa_display, _de_display, _cur_ratio_disp, _div_yield_disp, _beta_disp, _fcf_disp,
            _net_margin_anomalous, _ebitda_margin_pct_raw,
            _rev_cagr_disp_lbl, _prof_cagr_disp_lbl,
            context_source, business_context, sector_prompt_addition, _news_context_block,
            _fin_display_syntax,
        )
        # ── LLM calls: snapshot/bull/bear, then moat ──────────────────────────
        # These used to run concurrently via a ThreadPoolExecutor. Groq's
        # rate limit (especially on free/lower tiers) is often bound by
        # requests-per-minute rather than tokens, and firing 2 requests at
        # the exact same instant for every fresh stock lookup burns through
        # that RPM budget twice as fast as it needs to. Running them
        # sequentially costs a bit of latency (the two calls no longer
        # overlap) but roughly halves how many simultaneous requests hit
        # Groq at once, which is the more common thing to actually run out
        # of. The 30-min session cache above still means neither call
        # re-fires at all for a ticker the user already has cached results
        # for.
        _moat_cache_key     = f"moat_{ticker}"
        _combined_cache_key = f"combined_{ticker}"

        # If the user has switched to a different ticker since the last run,
        # clear any stale cached results from the previous ticker so they
        # don't bleed into the new company's analysis.
        _last_ticker = st.session_state.get("_last_analysed_ticker")
        if _last_ticker and _last_ticker != ticker:
            st.session_state.pop(f"moat_{_last_ticker}", None)
            st.session_state.pop(f"combined_{_last_ticker}", None)
            st.session_state.pop(f"moat_{_last_ticker}_ts", None)
            st.session_state.pop(f"combined_{_last_ticker}_ts", None)
        st.session_state["_last_analysed_ticker"] = ticker

        # TTL-based cache: 24 hours, matching the underlying LLM cache layer.
        # This is a per-browser-session cache (st.session_state), so a long
        # TTL just means someone who leaves a tab open (or reopens it later
        # the same day) doesn't re-trigger a Groq call for data that hasn't
        # gone stale. yfinance price data displayed elsewhere on the page is
        # unaffected — this only governs the LLM-generated analysis blocks.
        _CACHE_TTL = 24 * 60 * 60  # seconds
        _now = time.time()

        def _cache_valid(key):
            ts = st.session_state.get(f"{key}_ts")
            return ts is not None and (_now - ts) < _CACHE_TTL

        _moat_cached     = st.session_state.get(_moat_cache_key)     if _cache_valid(_moat_cache_key)     else None
        _combined_cached = st.session_state.get(_combined_cache_key) if _cache_valid(_combined_cache_key) else None

        def _run_combined():
            # 1000 tokens (the ask_llm default) was already tight for 4 snapshot
            # fields + earnings_summary + 3 bull + 3 bear items; the news-grounded
            # headline option (added so bull/bear can cite a real recent event)
            # makes at least one explanation longer, which was pushing some
            # generations past 1000 tokens — the JSON got cut off mid-string,
            # failed to parse, and silently fell back to the much more generic
            # retry prompt below without ever surfacing an error. 1700 gave
            # headroom for that. Bumped again to 2200 after adding the fuller
            # per-sector guardrail content (full llm_context + bull/bear theme
            # lists + the sector-relative-leverage rule) — richer grounding
            # tends to produce longer, more specific explanations, so the
            # token ceiling needs to grow with the prompt's specificity, not
            # just its length.
            return ask_llm(
                combined_prompt,
                "Return only valid JSON. No markdown. No backticks. No explanation. No code fences. Start with { and end with }.",
                max_tokens=2200,
            )

        def _run_moat():
            if _moat_cached is not None:
                return _moat_cached  # use cached result — skip the LLM call
            try:
                try:
                    result = get_moat_analysis(
                        sector, industry,
                        roe_raw=roe, de_raw=de, revenue_cagr=rev_cagr,
                        name=name, ticker=ticker,
                        profit_margin_raw=profit_margin,
                        pe=pe,
                        mkt_cap_cr=(mkt_cap / 1e7) if mkt_cap else None,
                        ask_llm_fn=ask_llm,
                        description=business_context,
                    )
                except TypeError:
                    result = get_moat_analysis(
                        sector, industry,
                        roe_raw=roe, de_raw=de, revenue_cagr=rev_cagr,
                    )
                return result
            except Exception:
                return None

        with st.spinner(f"Analysing {name}..."):
            if _combined_cached is not None:
                # Both results already cached — no LLM calls needed
                combined_raw = _combined_cached
                _moat_result = _moat_cached
            elif _MODULES_LOADED and _moat_cached is None:
                # Run snapshot LLM, then moat LLM, one after another
                combined_raw  = _run_combined()
                _moat_result  = _run_moat()
                if _moat_result is not None:
                    st.session_state[_moat_cache_key]        = _moat_result
                    st.session_state[f"{_moat_cache_key}_ts"] = _now
                st.session_state[_combined_cache_key]        = combined_raw
                st.session_state[f"{_combined_cache_key}_ts"] = _now
            else:
                combined_raw = _run_combined()
                _moat_result = _moat_cached
                st.session_state[_combined_cache_key]        = combined_raw
                st.session_state[f"{_combined_cache_key}_ts"] = _now

        # Parse combined result — attempt to strip markdown fences if present,
        # then try to isolate the JSON object even if there's surrounding text.
        # On failure, retry the LLM call once before showing an error.
        def _repair_truncated_json(s: str) -> str:
            """Best-effort repair for the specific, common failure mode where
            the LLM's JSON got cut off mid-generation because it hit
            max_tokens before finishing — NOT a general JSON fixer for
            arbitrarily malformed output. Closes an unterminated string (if
            generation stopped mid-value) and then closes any unbalanced
            { / [ left open, in the correct nesting order. If the response
            was truncated cleanly at a field boundary this recovers a valid,
            if slightly shorter, object (e.g. 2 bear points instead of 3)
            rather than discarding the whole response and showing the user
            an error banner for what was actually mostly-good output.
            """
            in_string, escaped = False, False
            for ch in s:
                if escaped:
                    escaped = False
                elif ch == "\\":
                    escaped = True
                elif ch == '"':
                    in_string = not in_string
            if in_string:
                s += '"'

            stack: list[str] = []
            in_string, escaped = False, False
            closers = {"{": "}", "[": "]"}
            for ch in s:
                if escaped:
                    escaped = False
                    continue
                if ch == "\\":
                    escaped = True
                    continue
                if ch == '"':
                    in_string = not in_string
                    continue
                if in_string:
                    continue
                if ch in "{[":
                    stack.append(ch)
                elif ch in "}]" and stack:
                    stack.pop()
            while stack:
                s += closers[stack.pop()]
            return s

        def _parse_combined_json(raw_text: str) -> dict:
            import re
            raw = raw_text.strip()
            # Strip markdown code fences (```json ... ``` or ``` ... ```)
            # Use regex so we match exactly one opening/closing fence without
            # accidentally eating content characters via lstrip.
            raw = re.sub(r'^```(?:json)?\s*', '', raw)
            raw = re.sub(r'\s*```$', '', raw)
            raw = raw.strip()
            # Isolate the outermost JSON object in case of leading/trailing text
            start = raw.find("{")
            end = raw.rfind("}") + 1
            if start != -1 and end > start:
                raw = raw[start:end]
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                # Most likely cause: generation was cut off before reaching
                # a closing brace (see _repair_truncated_json above) — try
                # to salvage it before giving up and showing the user an
                # error for what may be mostly-complete, good content.
                return json.loads(_repair_truncated_json(raw))

        combined_data = {}
        parse_error = None
        try:
            combined_data = _parse_combined_json(combined_raw)
        except Exception as e1:
            parse_error = str(e1)
            # Retry once with a stricter prompt
            with st.spinner("Retrying analysis..."):
                _retry_fin_instruction = (
                    f"'The company's financial health is underscored by its Return on Assets of {_roa_display} "
                    f"and Return on Equity of {_roe_display}, reflecting [qualitative insight].'"
                ) if (_fin_slug in ("banking", "nbfc") and _roa_or_roe_available) else (
                    f"'The company's financial health is underscored by its TTM EBITDA Margin of {_ttm_ebitda_m} "
                    f"and a {_rev_cagr_disp_lbl} — note reported net margin is far above a sustainable operating "
                    f"level, which points to a non-operating or exceptional gain rather than core operating "
                    f"profitability, so EBITDA margin is the more reliable read here.'"
                ) if (_net_margin_anomalous and _ebitda_margin_pct_raw is not None) else (
                    f"'The company's reported TTM Net Margin of {_ttm_net_margin} is not a reliable measure of "
                    f"core operating profitability — a margin this extreme relative to revenue almost certainly "
                    f"reflects a non-operating or exceptional gain rather than the underlying business. "
                    f"[one-line qualitative insight about the business itself, not the margin].'"
                ) if _net_margin_anomalous else (
                    f"'The company's financial health is underscored by its TTM Net Margin of {_ttm_net_margin} "
                    f"and a {_rev_cagr_disp_lbl}, reflecting [qualitative insight].'"
                )
                retry_prompt = (
                    f"Return ONLY a valid JSON object for {name} ({ticker}), sector: {sector}. "
                    f"Use these EXACT metric strings verbatim — do not round or reformat them: "
                    f"TTM Net Margin={_ttm_net_margin} | TTM Revenue={_ttm_revenue} | "
                    f"Market Cap={_mkt_cap} | ROE={_roe_display} | ROA={_roa_display} | P/E={_pe_display} | "
                    f"D/E={_de_display} | Revenue CAGR={_rev_cagr_disp_lbl} | Profit CAGR={_prof_cagr_disp_lbl}. "
                    f"For the 'financials' field use this exact structure: "
                    f"{_retry_fin_instruction} "
                    "Keys required: "
                    "snapshot (object with keys: business, position, financials, outlook — each a single sentence), "
                    "earnings_summary (string, 2 sentences using Revenue CAGR and Profit CAGR verbatim, no other metrics), "
                    "bull (array of 3 objects with headline and explanation — cite 1 fresh metric per explanation), "
                    "bear (array of 3 objects with headline and explanation — sector-appropriate risks only, "
                    f"NEVER contradict metrics: do NOT say high debt if D/E is {_de_display}). "
                    "No markdown. No backticks. Start with { end with }."
                )
                retry_raw = ask_llm(retry_prompt, "Return only valid JSON. Start with { and end with }. Nothing else.", max_tokens=1800)
            try:
                combined_data = _parse_combined_json(retry_raw)
                parse_error = None
            except Exception:
                pass  # parse_error stays set

        if parse_error and not combined_data:
            st.warning("⚠ AI analysis could not be parsed. The financial metrics above are accurate — only the AI commentary sections are affected. Try reloading.")

        # ── Post-parse contradiction filter ───────────────────────────────────
        if combined_data.get("bear"):
            _de_ratio = (de / 100) if de is not None else None
            _pe_low, _pe_high = get_pe_bands(sector, industry, slug=classify_sector(sector, industry, name, business_context)) if sector else (None, None)
            _filtered_bear = []
            for _bp in combined_data["bear"]:
                _expl = (_bp.get("headline", "") + " " + _bp.get("explanation", "")).lower()
                _skip = False
                # High debt contradiction
                if _de_ratio is not None and _de_ratio < 0.3:
                    if any(w in _expl for w in ["high debt", "heavily indebted", "debt burden", "debt level", "high leverage", "overleveraged"]):
                        _skip = True
                # Weak profitability contradiction
                if profit_margin is not None and profit_margin > 0.12:
                    if any(w in _expl for w in ["weak margin", "low margin", "poor profitability", "thin margin"]):
                        _skip = True
                # Weak ROE contradiction
                if roe is not None and roe > 0.15:
                    if any(w in _expl for w in ["weak roe", "low roe", "poor return on equity"]):
                        _skip = True
                # Expensive valuation contradiction — block if PE is genuinely below sector low
                if pe is not None and pe > 0 and _pe_low is not None and pe < _pe_low:
                    if any(w in _expl for w in ["expensive", "overvalued", "rich valuation", "stretched valuation", "high valuation"]):
                        _skip = True
                if not _skip:
                    _filtered_bear.append(_bp)
            combined_data["bear"] = _filtered_bear

        # ── Symmetric bull-case contradiction filter ────────────────────────
        # Mirrors the bear-case filter above, but for the opposite direction:
        # the bear filter blocks calling a genuinely-cheap stock "expensive";
        # this blocks calling a stock that is NOT genuinely cheap
        # "undervalued"/"attractive". Without this, a P/E sitting in the
        # sector's "fair" band (e.g. HAL at 32.6x against a 25x/40x
        # attractive/fair boundary for defense_aerospace) could still get an
        # LLM-written bull point saying the P/E "suggests the stock may be
        # undervalued" — directly contradicting the separately-computed
        # Value badge sitting right below it on the same page (which
        # correctly read "Fairly Valued" / 4.7/10 for the same number).
        if combined_data.get("bull"):
            _pe_low_b, _ = get_pe_bands(sector, industry, slug=classify_sector(sector, industry, name, business_context)) if sector else (None, None)
            _filtered_bull = []
            for _bp in combined_data["bull"]:
                _expl = (_bp.get("headline", "") + " " + _bp.get("explanation", "")).lower()
                _skip = False
                # Undervaluation contradiction — block unless PE is genuinely
                # inside the sector's "attractive" band (pe < _pe_low_b).
                if pe is not None and pe > 0 and _pe_low_b is not None and pe >= _pe_low_b:
                    if any(w in _expl for w in ["undervalued", "under-valued", "attractively valued",
                                                  "attractive valuation", "cheap valuation", "bargain",
                                                  "may be undervalued", "looks cheap"]):
                        _skip = True
                if not _skip:
                    _filtered_bull.append(_bp)
            combined_data["bull"] = _filtered_bull

        # ── Debt/leverage contradiction filter ───────────────────────────────
        # This is the deterministic backstop for the exact bug reported on
        # InterGlobe Aviation: the LLM still occasionally writes a bull
        # point calling elevated D/E "manageable"/"reasonable"/"low" straight
        # off the raw metric in the prompt, even with the SECTOR
        # CONTRADICTION CHECK / leverage-is-sector-relative instructions
        # above — those are strong hints, not a hard guarantee with an LLM.
        # Rather than just dropping the point (which can leave <3 bullets),
        # REWRITE it in place using the sector module's OWN "high severity"
        # de_ratio red-flag threshold as the source of truth — so this stays
        # correct automatically as any sector's threshold is tuned, instead
        # of hardcoding one number that's wrong for every sector but one.
        if combined_data.get("bull") and de is not None:
            from modules.sectors import get_sector_config as _get_sector_config_debt
            _slug_for_debt = classify_sector(sector, industry, name, business_context)
            _cfg_for_debt = _get_sector_config_debt(_slug_for_debt)
            _de_high_threshold = None
            for _rf in _cfg_for_debt.get("red_flags", []):
                _cond = _rf.get("condition", "")
                if _cond.startswith("de_ratio >") and _rf.get("severity") == "high":
                    try:
                        _de_high_threshold = float(_cond.split(">", 1)[1].strip())
                    except Exception:
                        pass
            _de_x = de / 100.0
            _debt_positive_phrases = [
                "manageable debt", "manageable leverage", "reasonable debt",
                "reasonable leverage", "low debt", "low leverage",
                "healthy leverage", "healthy debt", "clean balance sheet",
                "strong balance sheet", "conservative leverage",
                "well managed debt", "well-managed debt", "debt management",
                "comfortable leverage", "comfortable debt",
            ]
            if _de_high_threshold is not None and _de_x > _de_high_threshold:
                _lease_note = (
                    "High reported leverage is largely driven by lease accounting under Ind AS 116, "
                    "given the sector's aircraft-lease-heavy balance sheets — but liquidity, operating "
                    "cash flow, and interest coverage should be checked before treating it as manageable."
                    if _slug_for_debt == "airlines" else
                    "Leverage here is above the sector's own high-severity threshold and should not be "
                    "read as a strength — check liquidity and cash flow trends instead."
                )
                _rebuilt_bull = []
                for _bp in combined_data["bull"]:
                    _expl = (_bp.get("headline", "") + " " + _bp.get("explanation", "")).lower()
                    if any(w in _expl for w in _debt_positive_phrases):
                        _bp = dict(_bp)
                        _bp["headline"] = (
                            "Leverage — Lease-Driven, Not a Strength" if _slug_for_debt == "airlines"
                            else "Leverage Above Sector Threshold"
                        )
                        _bp["explanation"] = (
                            f"Reported D/E of {_de_x:.2f}x is above the sector's own high-severity "
                            f"threshold of {_de_high_threshold:.1f}x, which the Red Flag Detector already "
                            f"flags separately — it should not also be read as a strength here. {_lease_note}"
                        )
                    _rebuilt_bull.append(_bp)
                combined_data["bull"] = _rebuilt_bull

        # ── Turnaround / cyclical detection (Phase 1 analyst signals) ────
        # Computed here, before both the Quality/Value badges and the Risk
        # Meter that read it below. (Previously this was computed further
        # down the script, after the badges block that already referenced
        # it — a NameError on every render. Fixed by hoisting it here.)
        turnaround_info = None
        is_cyclical = False
        if _MODULES_LOADED:
            try:
                _sector_slug_for_signals = classify_sector(sector, industry, name, business_context)
                is_cyclical = detect_cyclical(_sector_slug_for_signals, industry)
                turnaround_info = detect_turnaround(fin, bs, revenue_cagr=rev_cagr)
            except Exception:
                pass

        # ── Financial Health Score + Risk Meter (side by side) ─────────
        _health_col, _risk_col = st.columns(2)
        with _health_col:
            st.markdown("<div class='section-card' style='height:100%;'><div class='section-title'>Financial Health</div>", unsafe_allow_html=True)

            # Use new weighted scoring engine if modules loaded, else fallback
            if _MODULES_LOADED:
                pb_val = info.get("priceToBook")
                current_ratio_val = info.get("currentRatio")

                # EV/EBITDA fallback — yfinance's `enterpriseToEbitda` field
                # comes back None for a number of NSE large caps (RELIANCE.NS
                # among them). When that happens, _score_valuation's
                # conglomerate blended-band check (get_blended_ev_ebitda_band)
                # never fires — even though it exists specifically for
                # companies like Reliance — and valuation silently falls back
                # to a generic single-sector P/E band instead (e.g. a plain
                # "Energy" 10-25x band, which unfairly judges Jio/Retail/Media
                # segments against a pure oil & gas bar). Compute EV/EBITDA
                # manually from the same balance-sheet figures already pulled
                # above (total_debt_val, cash_val, ebitda_val) whenever the
                # direct yfinance field is missing, so the blended path still
                # gets a chance to run.
                _ev_ebitda_direct = info.get("enterpriseToEbitda")
                _ev_ebitda_fallback = None
                if (_ev_ebitda_direct is None and mkt_cap is not None
                        and total_debt_val is not None and ebitda_val):
                    _ev = mkt_cap + total_debt_val - (cash_val or 0)
                    if _ev > 0:
                        _ev_ebitda_fallback = round(_ev / ebitda_val, 2)
                _ev_ebitda_final = _ev_ebitda_direct if _ev_ebitda_direct is not None else _ev_ebitda_fallback

                health = compute_health_score(
                    pe=pe, pb=pb_val, roe_raw=roe, de_raw=de,
                    profit_margin_raw=profit_margin,
                    revenue_cagr=rev_cagr, profit_cagr=profit_cagr,
                    current_ratio=current_ratio_val,
                    sector=sector, industry=industry,
                    name=name, description=description,
                    extra_metrics={
                        "fcf": info.get("freeCashflow"),
                        "ocf": info.get("operatingCashflow"),
                        "revenue": info.get("totalRevenue"),
                        "roa": info.get("returnOnAssets"),
                        "pb_ratio": pb_val,
                        "ev_ebitda": _ev_ebitda_final,
                        "price_to_sales": info.get("priceToSalesTrailing12Months"),
                        # Derived from bs/fin statement dataframes above —
                        # previously always missing_data for every sector
                        # rule that referenced them (e.g. metals_mining/
                        # telecom's net_debt_ebitda, renewable_energy's
                        # interest_coverage).
                        "net_debt_ebitda": net_debt_ebitda_val,
                        "interest_coverage": interest_coverage_val,
                        "receivable_days": receivable_days_val,
                        "inventory_months": inventory_months_val,
                    }
                )
                # Ignore health["score"] — it is computed inside the module on
                # a separate data path and can diverge from the sub-scores that
                # are actually displayed in the breakdown bars.  Recompute the
                # score here from the same sub_scores_map so the ring is always
                # the weighted average of exactly what the user sees on screen.
                verdict = health["explanation"]
                score_color = health["color"]
                sub_scores_map = health["sub_scores"]
                _sector_weights = health.get("_weights", {})

                # Build WEIGHTS dynamically from sector-specific pillars —
                # no longer hardcoded to the old 4-pillar generic model.
                WEIGHTS = [
                    (pillar, sub_scores_map.get(pillar), w)
                    for pillar, w in _sector_weights.items()
                ]
                _avail = [(s, w) for _, s, w in WEIGHTS if s is not None]
                _total_w = sum(w for _, w in _avail)
                score = round(sum(s * w for s, w in _avail) / _total_w, 1) if _total_w else health["score"]
                score_color = TXT_GOOD if score >= 7 else TXT_WARN if score >= 5 else TXT_BAD
                # Valuation badge — negative PE means loss-making on trailing basis;
                # showing "Undervalued" for a negative PE would be misleading.
                pe_low, pe_high = get_pe_bands(sector, industry, slug=classify_sector(sector, industry, name, business_context))
                pe_known = pe is not None and pe > 0
                if pe_known:
                    if pe < pe_low:
                        badge, badge_col = "Undervalued", TXT_GOOD
                    elif pe <= pe_high:
                        badge, badge_col = "Fairly Valued", TXT_WARN
                    else:
                        badge, badge_col = "Overvalued", TXT_BAD
                elif pe is not None and pe <= 0:
                    badge, badge_col = "Loss-Making", TXT_BAD
                else:
                    badge, badge_col = "Unknown", TXT_MUTED
                # get_pe_bands() only reads the "pe_ratio" band from a sector's
                # config. Banking/NBFC/Insurance configs define "price_to_book"
                # bands instead (P/B is the correct valuation metric for them),
                # so get_pe_bands() silently falls back to a generic PE band and
                # scores PE=18.7x as "Fairly Valued" even when the sector-aware
                # Valuation pillar (computed on P/B below) says the stock is
                # actually rich. Override the badge with that pillar's verdict
                # whenever the sector's own valuation pillar produced a score,
                # so the headline badge always agrees with the pillar the app
                # is actually weighting into the composite score.
                _val_pillar_score = sub_scores_map.get("Valuation")
                if _val_pillar_score is not None:
                    if _val_pillar_score >= 7:
                        badge, badge_col = "Undervalued", TXT_GOOD
                    elif _val_pillar_score >= 3:
                        badge, badge_col = "Fairly Valued", TXT_WARN
                    else:
                        badge, badge_col = "Overvalued", TXT_BAD
                badge_icon = {"Undervalued": "🟢", "Fairly Valued": "🟡", "Overvalued": "🔴", "Loss-Making": "🔴", "Unknown": "⚪"}[badge]
            else:
                # Legacy fallback when modules not loaded
                pe_low, pe_high = get_pe_bands(sector, industry, slug=classify_sector(sector, industry, name, business_context))
                pe_known = pe is not None and pe > 0  # guard: negative PE = loss-making
                if pe_known:
                    valuation_score = 9.0 if pe < pe_low else 6.0 if pe <= pe_high else 1.0
                    badge = "Undervalued" if pe < pe_low else "Fairly Valued" if pe <= pe_high else "Overvalued"
                elif pe is not None and pe <= 0:
                    valuation_score = 2.0   # loss-making trailing period → low valuation score
                    badge = "Loss-Making"
                else:
                    valuation_score = None
                    badge = "Unknown"

                badge_icon = {"Undervalued": "🟢", "Fairly Valued": "🟡", "Overvalued": "🔴", "Loss-Making": "🔴", "Unknown": "⚪"}[badge]
                badge_col  = {"Undervalued": "#22C55E", "Fairly Valued": "#F59E0B", "Overvalued": "#EF4444", "Loss-Making": "#EF4444", "Unknown": "#6B7280"}[badge]

                roe_pct    = roe * 100 if roe is not None else None
                margin_pct = profit_margin * 100 if profit_margin is not None else None

                def _band_score(value, bands):
                    for threshold, s in bands:
                        if value >= threshold:
                            return s
                    return bands[-1][1]

                roe_score = _band_score(roe_pct, [(20, 9.0), (12, 7.0), (6, 5.0), (0, 3.0), (-999, 1.0)]) if roe_pct is not None else None
                margin_score = _band_score(margin_pct, [(15, 9.0), (8, 7.0), (3, 5.0), (0, 3.0), (-999, 1.0)]) if margin_pct is not None else None
                if roe_score is not None and margin_score is not None:
                    profitability_score = round((roe_score + margin_score) / 2, 1)
                elif roe_score is not None:
                    profitability_score = roe_score
                elif margin_score is not None:
                    profitability_score = margin_score
                else:
                    profitability_score = None

                growth_score = _band_score(revenue_growth_pct, [(15, 9.0), (5, 7.0), (0, 5.0), (-10, 3.0), (-999, 1.0)]) if revenue_growth_pct is not None else None

                if de is not None:
                    de_ratio_fb = de / 100
                    # Fix 4: Financial Services (NBFCs, banks) have structurally
                    # high D/E as a feature of their business model — they borrow
                    # to lend.  Use relaxed thresholds so HDFC Bank / Bajaj Finance
                    # don't score as "Distressed" for having D/E of 5–8x.
                    _is_financial = sector in ("Financial Services", "Banks", "Insurance")
                    if _is_financial:
                        balance_sheet_score = (
                            9.0 if de_ratio_fb < 8.0 else
                            7.0 if de_ratio_fb < 12.0 else
                            5.0 if de_ratio_fb < 18.0 else
                            3.0
                        )
                    else:
                        balance_sheet_score = (
                            9.0 if de_ratio_fb < 0.3 else
                            7.0 if de_ratio_fb < 0.6 else
                            5.0 if de_ratio_fb < 1.0 else
                            3.0 if de_ratio_fb < 2.0 else
                            1.0
                        )
                else:
                    balance_sheet_score = None

                WEIGHTS = [
                    ("Valuation", valuation_score, 30),
                    ("Profitability", profitability_score, 25),
                    ("Growth", growth_score, 25),
                    ("Balance Sheet", balance_sheet_score, 20),
                ]
                available = [(label, s, w) for label, s, w in WEIGHTS if s is not None]
                total_weight = sum(w for _, _, w in available)
                score = round(sum(s * w for _, s, w in available) / total_weight, 1) if total_weight else 5.0

                if score >= 8.5:
                    verdict = "Excellent fundamentals across all dimensions."
                elif score >= 7:
                    verdict = "Strong financial health — solid across most metrics."
                elif score >= 5:
                    verdict = "Average — mixed signals, monitor key metrics."
                elif score >= 3:
                    verdict = "Weak fundamentals — significant concerns."
                else:
                    verdict = "Distressed — poor health across most dimensions."
                score_color = TXT_GOOD if score >= 7 else TXT_WARN if score >= 5 else TXT_BAD

            # ── Sub-score-aware verdict (module-level _build_smart_verdict) ──
            verdict = _build_smart_verdict(score, WEIGHTS)

            # ── Quality vs Value split ──────────────────────────────────────
            # The blended score conflates "how good is the business" with
            # "how expensive is the stock" — a high-ROE, low-debt compounder
            # trading at a rich multiple (e.g. Britannia) can land in the same
            # 5-6/10 band as a genuinely mediocre business. Split them out so
            # both signals are visible instead of cancelling each other out.
            _value_entry = next(
                ((s, w) for label, s, w in WEIGHTS if label == "Valuation" and s is not None),
                None,
            )
            value_score = _value_entry[0] if _value_entry else None

            _quality_entries = [(s, w) for label, s, w in WEIGHTS if label != "Valuation" and s is not None]
            _quality_total_w = sum(w for _, w in _quality_entries)
            quality_score = round(sum(s * w for s, w in _quality_entries) / _quality_total_w, 1) if _quality_total_w else None

            # Turnaround penalty — per the analyst spec, a loss→profit swing
            # or debt-driven recovery shouldn't be scored the same as durable,
            # multi-year compounding. Quality (not Valuation) takes the hit.
            if turnaround_info and quality_score is not None:
                quality_score = round(max(0, quality_score - 2.0), 1)

            quality_color = TXT_MUTED if quality_score is None else (
                TXT_GOOD if quality_score >= 7 else TXT_WARN if quality_score >= 5 else TXT_BAD
            )
            value_label, value_color = valuation_bucket(value_score) if _MODULES_LOADED else (
                ("Unknown", TXT_MUTED) if value_score is None else
                ("Cheap", TXT_GOOD) if value_score >= 7 else
                ("Fair", TXT_WARN) if value_score >= 3 else ("Rich", TXT_BAD)
            )

            # ── Render score ring, verdict, badge, breakdown ──────────────────
            st.markdown(f"""
            <div style='text-align:center; margin-bottom:0.5rem;'>
              <div class='score-ring' style='color:{score_color};'>{score}<span style='font-size:1.2rem; color:#5B6673;'>/10</span></div>
              <div class='score-label' style='font-size:13px; color:#5B6673; margin-top:4px;'>{verdict}</div>
              <div style='margin-top:8px; display:inline-block; background:#F5F6F8; border:1px solid {badge_col}; border-radius:20px; padding:4px 14px; font-size:13px; font-weight:600; color:{badge_col};'>{badge_icon} {badge}</div>
              <div style='margin-top:10px; display:flex; justify-content:center; gap:8px;'>
                <div style='background:#F5F6F8; border:1px solid {quality_color}; border-radius:10px; padding:6px 14px; min-width:100px;'>
                  <div style='font-size:10px; color:#5B6673; text-transform:uppercase; letter-spacing:0.5px;'>Quality</div>
                  <div style='font-size:15px; font-weight:700; color:{quality_color};'>{quality_score if quality_score is not None else "N/A"}{"/10" if quality_score is not None else ""}</div>
                </div>
                <div style='background:#F5F6F8; border:1px solid {value_color}; border-radius:10px; padding:6px 14px; min-width:100px;'>
                  <div style='font-size:10px; color:#5B6673; text-transform:uppercase; letter-spacing:0.5px;'>Value</div>
                  <div style='font-size:15px; font-weight:700; color:{value_color};'>{value_label}{f" ({value_score}/10)" if value_score is not None else ""}</div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            # ── Data completeness disclosure ────────────────────────────────
            # Sectors like banking put heavy weight on pillars (Asset Quality,
            # Capital Adequacy) that yfinance often can't populate. Make that
            # gap visible instead of letting a 4.7/10 look like a full-weight
            # verdict when it's actually only using a subset of the intended
            # pillars. Framed as a neutral data-availability note rather than
            # a warning — the score itself is already re-normalized against
            # only the available pillars (see quality_score calc above), so
            # it isn't "wrong" or "incomplete" in a way that should alarm a
            # user; it's just transparent about what went into it. This logic
            # is sector-agnostic: `_missing_pillars` is whatever WEIGHTS
            # entries came back None for the current stock, so the same
            # wording works for a bank missing Asset Quality, an insurer
            # missing Embedded Value, a conglomerate missing a segment, etc.
            _total_intended_w = sum(w for _, _, w in WEIGHTS)
            _available_w = sum(w for _, s, w in WEIGHTS if s is not None)
            _missing_pillars = [label for label, s, _ in WEIGHTS if s is None]
            if _total_intended_w > 0 and _available_w < _total_intended_w:
                _coverage_pct = round(_available_w / _total_intended_w * 100)
                _missing_str = " & ".join(_missing_pillars) if len(_missing_pillars) <= 2 \
                    else ", ".join(_missing_pillars[:-1]) + f", & {_missing_pillars[-1]}"
                st.markdown(f"""
                <div style='background:#F5F6F8; border:1px solid #D9E2E8; border-radius:8px;
                            padding:8px 12px; margin-top:10px; font-size:11.5px; color:#2E5A78;'>
                  ℹ️ Some {_missing_str} metrics weren't available from the current data source.
                  This score reflects the {_coverage_pct}% of factors we could verify.
                </div>
                """, unsafe_allow_html=True)

            # ── Proxy-pillar disclosure ──────────────────────────────────────
            # Some pillars (Embedded Value for insurance, Execution for
            # renewable/capital goods) require specialized data the source
            # never actually provides, so they silently fall back to a
            # generic stand-in (ROE, revenue growth) under their original
            # label. Disclose this the same way missing pillars are
            # disclosed — otherwise a relabeled generic metric looks
            # identical to real sector-specific analysis.
            _proxy_pillars = health.get("proxy_pillars") or []
            _proxy_explanations = health.get("proxy_explanations") or {}
            for _pp in _proxy_pillars:
                st.markdown(f"""
                <div style='background:#F5F6F8; border:1px solid #D9E2E8; border-radius:8px;
                            padding:8px 12px; margin-top:8px; font-size:11.5px; color:#2E5A78;'>
                  ℹ️ <b>{_pp}</b> uses a related available metric as a stand-in — {_proxy_explanations.get(_pp, "")}
                </div>
                """, unsafe_allow_html=True)

            # ── Known data caveat disclosure ──────────────────────────────────
            # A handful of companies are mid-corporate-action (demerger,
            # major divestiture, fiscal-year realignment) in a way that makes
            # trailing YoY comparisons genuinely non-comparable for a period —
            # not detectable from the numbers alone, so scoring can't catch
            # this automatically. See modules/data_caveats.py.
            _data_caveat = get_data_caveat(name) if _MODULES_LOADED else None
            if _data_caveat:
                st.markdown(f"""
                <div style='background:#F5F6F8; border:1px solid #B45309; border-radius:8px;
                            padding:8px 12px; margin-top:8px; font-size:11.5px; color:#92400E;'>
                  ⚠️ <b>Data caveat:</b> {_data_caveat}
                </div>
                """, unsafe_allow_html=True)

            # ── Turnaround Company disclosure ───────────────────────────────
            if turnaround_info:
                _reasons_html = "".join(f"<div style='padding:2px 0;'>• {r}</div>" for r in turnaround_info["reasons"])
                st.markdown(f"""
                <div style='background:#F5F6F8; border:1px solid #7C3AED; border-radius:8px;
                            padding:10px 12px; margin-top:10px; font-size:11.5px; color:#6D28D9;'>
                  <div style='font-weight:700; margin-bottom:4px;'>🔄 Turnaround Company</div>
                  {_reasons_html}
                  <div style='margin-top:4px; color:#5B6673;'>Recent growth is influenced by recovery from a depressed base rather than long-term compounding. Growth sustainability should be monitored — Quality score adjusted down accordingly.</div>
                </div>
                """, unsafe_allow_html=True)

            # ── Cyclical Sector note ─────────────────────────────────────────
            if is_cyclical:
                st.markdown("""
                <div style='background:#F5F6F8; border:1px solid #D8DBE0; border-radius:8px;
                            padding:8px 12px; margin-top:10px; font-size:11.5px; color:#5B6673;'>
                  🔁 Cyclical sector — earnings and margins here typically swing with commodity/capex cycles. Weigh recent strong years against the full cycle, not in isolation.
                </div>
                """, unsafe_allow_html=True)
            breakdown_html = "<div style='margin-top:12px;'>"
            for label, s, weight in WEIGHTS:
                if s is None:
                    breakdown_html += f"""
                    <div style='margin-bottom:10px;'>
                      <div style='display:flex; justify-content:space-between; font-size:12px; margin-bottom:3px;'>
                        <span style='color:#5B6673;'>{label} <span style='color:var(--ink-muted);'>(no data)</span></span>
                        <span style='color:#5B6673; font-weight:600;'>N/A</span>
                      </div>
                      <div style='background:#E2E4E9; border-radius:4px; height:5px;'></div>
                    </div>"""
                    continue
                s_color = TXT_GOOD if s >= 7 else TXT_WARN if s >= 5 else TXT_BAD
                bar_pct = int(s * 10)
                breakdown_html += f"""
                <div style='margin-bottom:10px;'>
                  <div style='display:flex; justify-content:space-between; font-size:12px; margin-bottom:3px;'>
                    <span style='color:#5B6673;'>{label} <span style='color:var(--ink-muted);'>({weight}% wt)</span></span>
                    <span style='color:{s_color}; font-weight:600;'>{s}/10</span>
                  </div>
                  <div style='background:#E2E4E9; border-radius:4px; height:5px;'>
                    <div style='background:{s_color}; width:{bar_pct}%; height:5px; border-radius:4px;'></div>
                  </div>
                </div>"""
            breakdown_html += "</div>"
            st.markdown(breakdown_html, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)


        # ── Risk Meter (right column, paired with Health Score) ─────────
        # Define cash flow vars here — used by both Risk Meter and Red Flags
        free_cf = info.get("freeCashflow")
        operating_cf = info.get("operatingCashflow")
        # Computed here (rather than down at the Red Flag Detector section
        # where it used to live) so the Risk Meter call below can use it too.
        ebitda_margin = info.get("ebitdaMargins")
        ebitda_m_pct = ebitda_margin * 100 if ebitda_margin is not None else None

        with _risk_col:
            if _MODULES_LOADED:
                st.markdown("<div class='section-card' style='height:100%;'><div class='section-title'>🎯 Risk Meter</div>", unsafe_allow_html=True)
            try:
                # de_raw=de passes yfinance's debtToEquity value which is in
                # percentage form (e.g. 14.826 = D/E ratio of 0.15). The
                # modules/risk_meter.py compute_risk() function is expected to
                # divide de_raw by 100 internally before using it as a ratio.
                # If risk levels appear inflated, verify that contract in risk_meter.py.
                #
                # ebitda_margin_pct / revenue_growth_pct / profit_growth_pct /
                # current_ratio / extra_metrics are passed through so the same
                # sector-specific red_flags rules that already fire correctly
                # in the Red Flag Detector (detect_flags() below) can also
                # fire here — previously compute_risk() only ever saw
                # pe/de_ratio/beta/profit_margin, so any rule keyed on
                # ebitda_margin, revenue_growth, current_ratio, net_debt_ebitda,
                # interest_coverage, receivable_days, or inventory_months could
                # never trigger inside the Risk Meter.
                risk = compute_risk(
                    pe=pe, de_raw=de, beta=info.get("beta"),
                    free_cf=free_cf, operating_cf=operating_cf,
                    profit_margin_raw=profit_margin, sector=sector, industry=industry,
                    name=name, description=business_context,
                    ebitda_margin_pct=ebitda_m_pct,
                    revenue_growth_pct=revenue_growth_pct,
                    profit_growth_pct=profit_growth_pct,
                    current_ratio=current_ratio_val,
                    extra_metrics={
                        "net_debt_ebitda": net_debt_ebitda_val,
                        "interest_coverage": interest_coverage_val,
                        "receivable_days": receivable_days_val,
                        "inventory_months": inventory_months_val,
                    },
                )
                # A turnaround company recovering from distress should never
                # read as "Low Risk" — growth sustainability is still unproven.
                if turnaround_info and risk["level"] < 2:
                    risk = {**risk, "level": 2, "label": "Moderate Risk", "icon": "🟡", "color": "#F59E0B"}
                level_pct = {1: 25, 2: 50, 3: 75, 4: 100}[risk["level"]]
                st.markdown(f"""
                <div style='text-align:center; margin-bottom:0.8rem;'>
                  <span style='font-size:2rem;'>{risk["icon"]}</span>
                  <div style='font-size:1.1rem; font-weight:700; color:{risk["color"]}; margin-top:4px;'>{risk["label"]}</div>
                  <div style='background:#E2E4E9; border-radius:6px; height:8px; margin:10px 0;'>
                    <div style='background:{risk["color"]}; width:{level_pct}%; height:8px; border-radius:6px;'></div>
                  </div>
                  <div style='font-size:11px; color:#5B6673;'>Base: {risk["sector_base"]} (sector)</div>
                </div>
                <p style='font-size:11.5px; color:#5B6673; line-height:1.5; margin-bottom:0.6rem; font-style:italic;'>{risk.get("sector_context","")}</p>
                """, unsafe_allow_html=True)
                for f in risk["factors"][:5]:
                    st.markdown(f"<div style='font-size:12px; color:#5B6673; padding:3px 0; border-bottom:1px solid #E5E7EB;'>• {f}</div>", unsafe_allow_html=True)
            except Exception:
                st.info("Risk assessment unavailable.")
            st.markdown("</div>", unsafe_allow_html=True)


        # ── Restructuring/one-off-item caveat banner ─────────────────────────
        # Combines every signal collected above that indicates this
        # company's reported financials are distorted by something other
        # than core business performance: the net-margin sanity check
        # (contaminated net income/ROE — either net margin exceeding EBITDA
        # margin, or an absolute net margin >100% that's impossible from
        # core operations alone) and the CAGR discontinuity guard
        # (contaminated multi-year revenue/profit trend, e.g. a demerger
        # stitching two different-sized entities' histories together).
        # These two checks catch different root causes — a demerger is one
        # possible cause, but so is a one-off asset sale, litigation
        # settlement, or licensing windfall (see SPARC.NS, TTM Net Margin
        # 3967% with no demerger involved) — so the banner doesn't assume
        # which one applies. Surfaced as one explicit, visible warning
        # rather than leaving the person to infer it from a handful of
        # individually-caveated numbers scattered across different cards.
        if _net_margin_anomalous or rev_had_break or profit_had_break:
            _ebitda_alt_note = (
                " TTM EBITDA Margin is a more reliable profitability read."
                if _ebitda_margin_pct_raw is not None else
                " EBITDA margin data isn't available either — treat reported profitability with caution and "
                "focus on revenue and cash flow trends instead."
            )
            st.warning(
                "⚠️ Financials affected by a one-off item, corporate action, or cyclical swing. This "
                "company's reported profitability and/or growth figures (Net Margin, ROE, revenue/profit "
                "CAGR) appear distorted by something other than steady-state core operating performance — "
                "e.g. a demerger, spinoff, asset sale, litigation settlement, licensing windfall, or a "
                "cyclical loss-to-profit turnaround/low-base effect (such as post-pandemic demand recovery "
                "for a travel or aviation business). Interpret ROE, EPS, and profit trends "
                "cautiously." + _ebitda_alt_note
            )

        # ── Company snapshot ─────────────────────────────────────────────────
        st.markdown("<div class='section-card'><div class='section-title'>Company Snapshot</div>", unsafe_allow_html=True)

        raw_snap = combined_data.get("snapshot", {})

        if isinstance(raw_snap, dict):
            # ── Outlook truncation sanitizer (uses module-level helpers) ──────
            _outlook_raw = raw_snap.get("outlook", "")

            if _outlook_looks_truncated(_outlook_raw):
                # This whole block re-executes on EVERY Streamlit rerun for
                # this page — not just on a fresh "Analyse" click, but on
                # every widget interaction (the 1D/1M/3M/6M/1Y/3Y price
                # toggle, expanding any section, etc.), since Streamlit
                # re-runs the full script top-to-bottom each time. Unlike
                # the snapshot/moat calls above, this retry had NO cache
                # guard, so a stock whose outlook sentence happens to be
                # under 12 words (a false positive — plenty of complete
                # sentences are shorter than that) or matches a truncation
                # pattern by coincidence would fire a fresh, uncached Groq
                # call on every single click while that page was open —
                # a very plausible source of hitting API rate limits much
                # faster than the actual number of stocks looked up would
                # suggest. Cache the outcome (success OR failure) per
                # ticker so it fires at most once per _CACHE_TTL window.
                _outlook_retry_cache_key = f"outlook_retry_{ticker}"
                if _cache_valid(_outlook_retry_cache_key):
                    _cached_outlook = st.session_state.get(_outlook_retry_cache_key)
                    if _cached_outlook:
                        raw_snap = dict(raw_snap)
                        raw_snap["outlook"] = _cached_outlook
                else:
                    _outlook_retry_prompt = (
                        f"Write ONE complete forward-looking sentence for {name} ({ticker}) in the {sector} sector. "
                        f"It must describe the single most important opportunity or risk for the next 12-24 months. "
                        f"Be specific and sector-grounded. "
                        f"CRITICAL: Write the full sentence — never truncate a noun phrase. "
                        f"For example, write 'private label competition', never just 'label competition'. "
                        f"Return only the sentence, no JSON, no preamble."
                    )
                    try:
                        _outlook_retry = ask_llm(_outlook_retry_prompt, "Return only a single complete sentence.", model="openai/gpt-oss-20b")
                        _outlook_retry = _outlook_retry.strip().strip('"').strip("'")
                        if _outlook_retry and not _outlook_looks_truncated(_outlook_retry):
                            raw_snap = dict(raw_snap)
                            raw_snap["outlook"] = _outlook_retry
                            st.session_state[_outlook_retry_cache_key] = _outlook_retry
                        else:
                            # Cache the "no good replacement" outcome too —
                            # otherwise a stock that keeps failing this
                            # retry (e.g. it's a false-positive trigger and
                            # every retry also happens to look short) would
                            # hit the API on every rerun forever.
                            st.session_state[_outlook_retry_cache_key] = ""
                    except Exception:
                        st.session_state[_outlook_retry_cache_key] = ""
                    st.session_state[f"{_outlook_retry_cache_key}_ts"] = _now

            # Structured snapshot — render as four labeled tiles
            # "Financials" tile explicitly carries a TTM badge so users
            # immediately know the margin/revenue figures are trailing twelve
            # months, not the most recent standalone fiscal year.
            _TTM_BADGE = (
                "<span style='font-size:9px; font-weight:700; background:#DCFCE7; "
                "color:#15803D; border-radius:4px; padding:1px 5px; "
                "vertical-align:middle; margin-left:5px; letter-spacing:0.4px;'>TTM</span>"
            )
            # (label, text, accent_mark, accent_text)
            # accent_mark paints the 3px left border — a MARK, so it keeps the
            # vivid hue. accent_text paints the label, so it needs a variant
            # that clears 4.5:1; the vivid values measure as low as 1.95:1.
            _snap_fields = [
                ("Business",                raw_snap.get("business",   ""),  "#3B82F6", "#2563EB"),
                ("Position",                raw_snap.get("position",   ""),  "#22C55E", TXT_GOOD),
                (f"Financials{_TTM_BADGE}", raw_snap.get("financials", ""),  "#F59E0B", TXT_WARN),
                ("Outlook",                 raw_snap.get("outlook",    ""),  "#A78BFA", "#6D28D9"),
            ]
            # Two tiles per row
            for row_start in range(0, len(_snap_fields), 2):
                tile_cols = st.columns(2)
                for col_idx, (label, text, accent, accent_text) in enumerate(_snap_fields[row_start:row_start+2]):
                    safe_text = sanitize_llm_html(text) if text else "<span style='color:var(--ink-muted);'>—</span>"
                    with tile_cols[col_idx]:
                        st.markdown(f"""
                        <div style='background:var(--surface-card); border:1px solid var(--border);
                                    border-left:3px solid {accent};
                                    border-radius:var(--r-md); padding:14px 16px; height:100%; min-height:80px;
                                    margin-bottom:10px; box-shadow:var(--sh-sm);'>
                          <div style='font-size:var(--fs-2xs); font-weight:700; color:{accent_text}; text-transform:uppercase;
                                      letter-spacing:0.8px; margin-bottom:6px;'>{label}</div>
                          <div style='font-size:var(--fs-md); color:var(--ink-secondary); line-height:1.7;'>{safe_text}</div>
                        </div>
                        """, unsafe_allow_html=True)
                st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        else:
            # Fallback: old flat string (backward compat with cached/retry responses)
            snap = sanitize_llm_html(str(raw_snap)) if raw_snap else "Summary unavailable."
            st.markdown(f"<p style='font-size:16px; line-height:1.85; color:#374151;'>{snap}</p>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # ── Bull / Bear case ─────────────────────────────────────────────────
        def _titlecase_headline(text: str) -> str:
            """Capitalize the first letter of each word in short 2-4 word
            headlines (the LLM occasionally lowercases the first word, e.g.
            'listed Subsidiary'). Doesn't touch words that already contain
            interior capitals/acronyms (e.g. 'P/E', 'ROE') to avoid mangling
            them, and never forces the rest of a word to lowercase."""
            words = text.split(" ")
            fixed = []
            for w in words:
                if w and w[0].islower():
                    w = w[0].upper() + w[1:]
                fixed.append(w)
            return " ".join(fixed)

        bull_col, bear_col = st.columns(2)

        with bull_col:
            st.markdown("<div class='section-card'><div class='section-title'><span class='bull-tag'>● Bull Case</span></div>", unsafe_allow_html=True)
            bull_points = combined_data.get("bull", [])
            if bull_points:
                bull_html = ""
                for point in bull_points:
                    headline = sanitize_llm_html(_titlecase_headline(point.get('headline', '')))
                    explanation = sanitize_llm_html(point.get('explanation', ''))
                    bull_html += f"<p style='margin:0 0 12px 0;'><b style='color:#15803D;'>{headline}</b><br>{explanation}</p>"
                st.markdown(f"<div style='font-size:16px; line-height:1.7; color:#374151;'>{bull_html}</div>", unsafe_allow_html=True)
            else:
                st.info("Bull case unavailable.")
            st.markdown("</div>", unsafe_allow_html=True)

        with bear_col:
            st.markdown("<div class='section-card'><div class='section-title'><span class='bear-tag'>● Bear Case</span></div>", unsafe_allow_html=True)
            bear_points = combined_data.get("bear", [])
            if bear_points:
                bear_html = ""
                for point in bear_points:
                    headline = sanitize_llm_html(_titlecase_headline(point.get('headline', '')))
                    explanation = sanitize_llm_html(point.get('explanation', ''))
                    bear_html += f"<p style='margin:0 0 12px 0;'><b style='color:#B91C1C;'>{headline}</b><br>{explanation}</p>"
                st.markdown(f"<div style='font-size:16px; line-height:1.7; color:#374151;'>{bear_html}</div>", unsafe_allow_html=True)
            else:
                st.info("Bear case unavailable.")
            st.markdown("</div>", unsafe_allow_html=True)

        # ── Red Flag Detector ────────────────────────────────────────────────
        st.markdown("<div class='section-card'><div class='section-title'><span class='risk-tag'>⚑ Red Flag Detector</span></div>", unsafe_allow_html=True)

        # The 4 flags are fixed and fully computed in Python below — no longer
        # sourced from the LLM at all. (Previously this list came from
        # combined_data.get("red_flags", []), which meant the whole section
        # ── Red Flag Detector (Enhanced) ─────────────────────────────────────
        # free_cf and operating_cf already defined above (before Risk Meter)
        if _MODULES_LOADED:
            # ebitda_margin / ebitda_m_pct now computed earlier, above the
            # Risk Meter block, so compute_risk() can use it too.
            detected_flags = detect_flags(
                pe=pe, roe_raw=roe, de_raw=de, profit_margin_raw=profit_margin,
                free_cf=free_cf, operating_cf=operating_cf, rev=rev,
                revenue_growth_pct=revenue_growth_pct, profit_growth_pct=profit_growth_pct,
                ebitda_margin_pct=ebitda_m_pct, sector=sector, industry=industry,
                current_ratio=current_ratio_val,
                extra_metrics={
                    "net_debt_ebitda": net_debt_ebitda_val,
                    "interest_coverage": interest_coverage_val,
                    "receivable_days": receivable_days_val,
                    "inventory_months": inventory_months_val,
                },
            )

            if detected_flags:
                flag_cols = st.columns(2)
                for i, flag in enumerate(detected_flags[:6]):  # show max 6 flags
                    with flag_cols[i % 2]:
                        st.markdown(f"""
                        <div style='background:#F3F4F6; border:1px solid #E2E4E9; border-radius:10px; padding:10px 14px; margin-bottom:10px;'>
                          <div style='font-size:13px; font-weight:600; color:{flag["color"]}; margin-bottom:4px;'>{flag["icon"]} {flag["title"]}</div>
                          <div style='font-size:12px; color:#5B6673;'>{flag["detail"]}</div>
                          <div style='margin-top:4px;'><span style='font-size:10px; background:#F5F6F8; border:1px solid #E2E4E9; border-radius:4px; padding:1px 6px; color:{flag["color"]};'>{flag["severity"].upper()} SEVERITY</span></div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style='background:#F3F4F6; border:1px solid #E2E4E9; border-radius:10px; padding:12px 16px;'>
                  <span style='color:#15803D; font-size:14px;'>🟢 No major red flags detected based on available metrics.</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            # Legacy 4-flag fallback
            ICON_COLOR = {
                "good":    ("🟢", "#22C55E"),
                "warn":    ("🟡", "#F59E0B"),
                "bad":     ("🔴", "#EF4444"),
                "unknown": ("⚪", "#6B7280"),
            }

            def _debt_flag():
                if de is None:
                    return "unknown", "Debt Data Unavailable", "Debt/Equity data unavailable."
                de_ratio = de / 100
                if de_ratio > 1.0:
                    return "bad", "High Debt", f"D/E is {de_ratio:.2f}x (above 1.0 is high)"
                elif de_ratio > 0.5:
                    return "warn", "Moderate Debt", f"D/E is {de_ratio:.2f}x"
                return "good", "Low Debt", f"D/E is {de_ratio:.2f}x"

            def _margin_flag():
                if profit_margin is None:
                    return "unknown", "Margin Unavailable", "Profit margin unavailable."
                m = profit_margin * 100
                if m < 5:
                    return "bad", "Low Margin", f"Net margin {m:.1f}%"
                elif m < 10:
                    return "warn", "Average Margin", f"Net margin {m:.1f}%"
                return "good", "Healthy Margin", f"Net margin {m:.1f}%"

            def _cf_flag():
                cf = free_cf if free_cf is not None else operating_cf
                if cf is None:
                    return "unknown", "Cash Flow N/A", "No cash flow data."
                lbl = "FCF" if free_cf is not None else "OCF"
                cf_str = f"{lbl} ₹{cf/1e7:,.0f} Cr"
                if cf >= 0:
                    return "good", "Positive Cash Flow", cf_str
                return "bad", "Negative Cash Flow", cf_str

            def _val_flag():
                if pe is None:
                    return "unknown", "Valuation Unavailable", "P/E unavailable."
                pe_low, pe_high = get_pe_bands(sector, industry, slug=classify_sector(sector, industry, name, business_context))
                if pe > pe_high:
                    return "bad", "Overvaluation Risk", f"P/E {pe:.1f}x > sector ceiling {pe_high:.0f}x"
                if pe < pe_low:
                    return "good", "Attractive Valuation", f"P/E {pe:.1f}x"
                return "warn", "Fair Valuation", f"P/E {pe:.1f}x"

            for flag_fn in [_debt_flag, _margin_flag, _cf_flag, _val_flag]:
                level, title, reason = flag_fn()
                icon, color = ICON_COLOR[level]
                st.markdown(f"""
                <div style='background:#F3F4F6; border:1px solid #E2E4E9; border-radius:10px; padding:10px 14px; margin-bottom:8px;'>
                  <div style='font-size:13px; font-weight:600; color:{color}; margin-bottom:4px;'>{icon} {title}</div>
                  <div style='font-size:12px; color:#5B6673;'>{reason}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)


        # ── Revenue Trend ────────────────────────────────────────────────
        _deferred_pft_fig = None
        _deferred_pft_pills = []
        _deferred_pft_fallback_df = None
        _pft_pill_had_break = False

        st.markdown("<div class='section-card'><div class='section-title'>Revenue Trend</div>", unsafe_allow_html=True)
        if fin is not None and not fin.empty:
            try:
                rev_row = None
                for rev_key in ["Total Revenue", "Revenue", "Total Revenues"]:
                    if rev_key in fin.index:
                        rev_row = fin.loc[rev_key]
                        break
                profit_row = None
                for profit_key in ["Net Income", "Net Income Common Stockholders", "Net Income From Continuing Operations", "Net Income Including Noncontrolling Interests", "Normalized Income"]:
                    if profit_key in fin.index:
                        profit_row = fin.loc[profit_key]
                        break
                if rev_row is not None:
                    today = pd.Timestamp.now(tz=rev_row.index.tz) if rev_row.index.tz else pd.Timestamp.now()

                    # ── Fix 1: Sort ascending (oldest→newest) so bars read
                    # left-to-right as growth, not decline.
                    # ── Fix 2: Drop NaN rows AND future/partial years together
                    # before building chart arrays so no '₹nan' label can appear.
                    rev_row_clean = rev_row.dropna().sort_index(ascending=True)
                    rev_row_clean = rev_row_clean[rev_row_clean.index <= today]

                    partial_flags = []  # kept for the caption warning below
                    for d in rev_row.index:
                        partial_flags.append(d > today)

                    complete_rev = rev_row_clean
                    # revenue_growth_pct was already computed in the CAGR block
                    # above using the canonical series.  Do NOT recompute here.

                    labels_sorted = [f"FY{str(d.year)[-2:]}" for d in complete_rev.index]
                    rev_vals_cr   = (complete_rev / 1e7).tolist()

                    # Align profit row to the same cleaned dates; values missing
                    # for those dates become NaN and are replaced with 0 for
                    # display so the bar still renders without a nan label.
                    if profit_row is not None:
                        profit_clean = profit_row.reindex(complete_rev.index)
                        pft_vals_cr  = [
                            float(v) / 1e7 if pd.notna(v) else 0.0
                            for v in profit_clean.values
                        ]
                    else:
                        pft_vals_cr = None

                    # ── CAGR pill computation (uses complete_rev) ────────────
                    # _rev_cagr_n / _pft_cagr_n must be computed HERE before
                    # the Fix-9 sync block reads them below.
                    _rev_cagr_disp, _pft_cagr_disp = None, None
                    _rev_yoy_disp, _pft_yoy_disp = None, None
                    _rev_cagr_n, _pft_cagr_n = None, None
                    _rev_pill_had_break, _pft_pill_had_break = False, False
                    # `_fin_is_quarterly` was already computed above (shared,
                    # median-gap classifier) — reused here so this pill can't
                    # disagree with the Financial Health / Earnings Insights
                    # numbers on whether `fin` is actually annual or
                    # quarterly data. Previously this block had no such
                    # guard at all, so it would confidently show a "3-yr
                    # CAGR" pill even when the main block had correctly
                    # concluded there wasn't enough genuine annual data and
                    # left Growth as N/A — same underlying data, two
                    # contradictory answers.
                    if not _fin_is_quarterly:
                        try:
                            # Corporate-action guard — same as the main CAGR block
                            # above (see _trim_to_last_discontinuity docstring).
                            # Trim only the series used for CAGR/YoY math here;
                            # `complete_rev`/`rev_vals_cr` driving the bar chart
                            # itself are left untouched so the chart still shows
                            # the full history, discontinuity and all — the pill
                            # number just needs to stop lying about what it means.
                            rev_s, _rev_pill_had_break = _trim_to_last_discontinuity(complete_rev)
                            if len(rev_s) >= 2:
                                n = max(len(rev_s) - 1, 1)
                                _rev_cagr_n = n
                                if rev_s.iloc[0] > 0:
                                    _rev_cagr_disp = ((rev_s.iloc[-1] / rev_s.iloc[0]) ** (1 / n) - 1) * 100
                                if rev_s.iloc[-2] and rev_s.iloc[-2] != 0:
                                    _rev_yoy_disp = (rev_s.iloc[-1] - rev_s.iloc[-2]) / abs(rev_s.iloc[-2]) * 100
                        except Exception:
                            pass
                        if profit_row is not None:
                            try:
                                pft_s_full = profit_row.reindex(complete_rev.index).dropna()
                                pft_s, _pft_pill_had_break = _trim_to_last_discontinuity(pft_s_full)
                                if len(pft_s) >= 2:
                                    n = max(len(pft_s) - 1, 1)
                                    _pft_cagr_n = n
                                    if pft_s.iloc[0] > 0 and pft_s.iloc[-1] > 0:
                                        _pft_cagr_disp = ((pft_s.iloc[-1] / pft_s.iloc[0]) ** (1 / n) - 1) * 100
                                    if pft_s.iloc[-2] and pft_s.iloc[-2] != 0:
                                        _pft_yoy_disp = (pft_s.iloc[-1] - pft_s.iloc[-2]) / abs(pft_s.iloc[-2]) * 100
                            except Exception:
                                pass

                    # ── Fix 9: Sync prompt CAGR year counts to chart counts ──
                    # Now safe to read _rev_cagr_n / _pft_cagr_n — computed above.
                    if _rev_cagr_n is not None:
                        rev_cagr_years = _rev_cagr_n
                    if _pft_cagr_n is not None:
                        profit_cagr_years = _pft_cagr_n
                    if rev_cagr is not None and rev_cagr_years is not None:
                        rev_cagr_display = f"{rev_cagr_years}-yr CAGR: {rev_cagr:.1f}%"
                    if profit_cagr is not None and profit_cagr_years is not None:
                        profit_cagr_display = f"{profit_cagr_years}-yr CAGR: {profit_cagr:.1f}%"
                    elif profit_growth_pct is not None and profit_cagr is None:
                        profit_cagr_display = f"N/A (YoY {profit_growth_pct:+.1f}%)"
                    _rev_cagr_disp_lbl  = rev_cagr_display
                    _prof_cagr_disp_lbl = profit_cagr_display

                    if _pgo is not None:
                        # ── Chart 1: Revenue ────────────────────────────────
                        fig_rev = _pgo.Figure()
                        fig_rev.add_trace(_pgo.Bar(
                            x=labels_sorted,
                            y=rev_vals_cr,
                            name="Revenue",
                            marker_color="#22C55E",
                            opacity=0.85,
                            text=[f"₹{v:,.0f}" if v is not None and not (isinstance(v, float) and (v != v)) else "" for v in rev_vals_cr],
                            textposition="outside",
                            textfont=dict(size=10, color="#6B7280"),
                        ))
                        fig_rev.update_layout(
                            paper_bgcolor="#F5F6F8",
                            plot_bgcolor="#F3F4F6",
                            font=dict(family="Inter", color="#374151", size=11),
                            height=240,
                            showlegend=False,
                            margin=dict(l=10, r=10, t=28, b=28),
                            xaxis=dict(
                                gridcolor="#E2E4E9", linecolor="#E2E4E9",
                                tickfont=dict(size=11, color="#6B7280"),
                            ),
                            yaxis=dict(
                                title=dict(text="₹ Cr", font=dict(size=10, color=TXT_MUTED)),
                                gridcolor="#E2E4E9", linecolor="#E2E4E9",
                                tickfont=dict(size=10, color=TXT_MUTED),
                                tickformat=",.0f",
                            ),
                        )

                        # Revenue CAGR pill above chart
                        rev_pill_parts = []
                        if _rev_cagr_disp is not None:
                            c = TXT_GOOD if _rev_cagr_disp >= 0 else TXT_BAD
                            _yr_label = f"{_rev_cagr_n}-yr " if _rev_cagr_n else ""
                            rev_pill_parts.append(f"<span style='background:#ECFDF3; color:{c}; border:1px solid {c}40; border-radius:12px; padding:3px 10px; font-size:12px; font-weight:600;'>{_yr_label}CAGR {_rev_cagr_disp:+.1f}%</span>")
                        if _rev_yoy_disp is not None:
                            c = TXT_GOOD if _rev_yoy_disp >= 0 else TXT_BAD
                            rev_pill_parts.append(f"<span style='background:#F3F4F6; color:{c}; border:1px solid {c}40; border-radius:12px; padding:3px 10px; font-size:12px;'>YoY {_rev_yoy_disp:+.1f}%</span>")
                        if rev_pill_parts:
                            st.markdown(
                                "<div style='display:flex; gap:8px; margin-bottom:6px;'>"
                                + " ".join(rev_pill_parts)
                                + "</div>",
                                unsafe_allow_html=True
                            )
                        if _rev_pill_had_break:
                            st.markdown(
                                "<p style='font-size:16px; color:#111827; margin-top:4px; line-height:1.7;'>"
                                "⚠️ CAGR window shortened — an implausible single-year "
                                "swing was detected in the chart above (possible causes: a "
                                "demerger/spinoff/restructuring, a one-off item, or a cyclical "
                                "loss-to-profit turnaround/low-base effect), so the pill only "
                                "spans the period after that break.</p>",
                                unsafe_allow_html=True,
                            )
                        st.plotly_chart(fig_rev, use_container_width=True, config={"displayModeBar": True, "displaylogo": False, "modeBarButtonsToRemove": ["lasso2d", "select2d"]})

                        # ── Chart 2: Net Profit — deferred outside col_chart ─
                        # Build fig_pft and pill data now while pft_vals_cr and
                        # labels_sorted are still in scope, but do NOT call
                        # st.plotly_chart here.  Rendering inside col_chart would
                        # stack both charts vertically in the narrow left column
                        # next to the health-score card.  Instead we store the
                        # figure and render it full-width after col_health closes.
                        _deferred_pft_fig = None
                        _deferred_pft_pills = []
                        _deferred_pft_fallback_df = None
                        if pft_vals_cr is not None:
                            bar_colors = ["#3B82F6" if v >= 0 else "#EF4444" for v in pft_vals_cr]
                            fig_pft = _pgo.Figure()
                            fig_pft.add_trace(_pgo.Bar(
                                x=labels_sorted,
                                y=pft_vals_cr,
                                name="Net Profit",
                                marker_color=bar_colors,
                                opacity=0.85,
                                text=[f"₹{v:,.0f}" if v is not None and not (isinstance(v, float) and (v != v)) else "" for v in pft_vals_cr],
                                textposition="outside",
                                textfont=dict(size=10, color="#6B7280"),
                            ))
                            fig_pft.update_layout(
                                paper_bgcolor="#F5F6F8",
                                plot_bgcolor="#F3F4F6",
                                font=dict(family="Inter", color="#374151", size=11),
                                height=240,
                                showlegend=False,
                                margin=dict(l=10, r=10, t=28, b=28),
                                xaxis=dict(
                                    gridcolor="#E2E4E9", linecolor="#E2E4E9",
                                    tickfont=dict(size=11, color="#6B7280"),
                                ),
                                yaxis=dict(
                                    title=dict(text="₹ Cr", font=dict(size=10, color="#3B82F6")),
                                    gridcolor="#E2E4E9", linecolor="#E2E4E9",
                                    tickfont=dict(size=10, color="#3B82F6"),
                                    tickformat=",.0f",
                                    zeroline=True,
                                    zerolinecolor="#EF4444",
                                    zerolinewidth=1,
                                ),
                            )
                            _deferred_pft_fig = fig_pft
                            if _pft_cagr_disp is not None:
                                c = "#2563EB" if _pft_cagr_disp >= 0 else TXT_BAD
                                _yr_label = f"{_pft_cagr_n}-yr " if _pft_cagr_n else ""
                                _deferred_pft_pills.append(f"<span style='background:#EEF2FF; color:{c}; border:1px solid {c}40; border-radius:12px; padding:3px 10px; font-size:12px; font-weight:600;'>{_yr_label}CAGR {_pft_cagr_disp:+.1f}%</span>")
                            if _pft_yoy_disp is not None:
                                c = TXT_GOOD if _pft_yoy_disp >= 0 else TXT_BAD
                                _deferred_pft_pills.append(f"<span style='background:#F3F4F6; color:{c}; border:1px solid {c}40; border-radius:12px; padding:3px 10px; font-size:12px;'>YoY {_pft_yoy_disp:+.1f}%</span>")

                    else:
                        # Fallback: st.bar_chart if plotly not installed.
                        # Revenue renders now inside col_chart; Net Profit is
                        # stored as a DataFrame and rendered after col_health.
                        st.markdown("**Revenue (₹ Cr)**")
                        rev_df = pd.DataFrame({"Revenue (₹ Cr)": rev_vals_cr}, index=labels_sorted)
                        st.bar_chart(rev_df, color="#22C55E")
                        _deferred_pft_fig = None
                        _deferred_pft_pills = []
                        _deferred_pft_fallback_df = None
                        if pft_vals_cr is not None:
                            _deferred_pft_fallback_df = pd.DataFrame(
                                {"Net Profit (₹ Cr)": pft_vals_cr}, index=labels_sorted
                            )

                    if any(partial_flags):
                        # fy_labels now refers to the cleaned chart labels; rebuild
                        # raw labels from the original index for the caption only.
                        raw_fy_labels = [f"FY{str(d.year)[-2:]}" for d in rev_row.index]
                        partial_years = ", ".join(lbl for lbl, p in zip(raw_fy_labels, partial_flags) if p)
                        st.caption(f"⚠ {partial_years} fiscal year end date is in the future — figures may be partial/estimated.")
                else:
                    st.info("Revenue data unavailable for this ticker.")
            except Exception:
                st.info("Chart data unavailable for this ticker.")
        else:
            st.info("Financial data unavailable.")
        st.markdown("</div>", unsafe_allow_html=True)

        # ── Net Profit Trend (deferred: rendered full-width after the col_chart/col_health split)
        # The figure was built inside col_chart so that pft_vals_cr / labels_sorted
        # were still in scope, but we deliberately did NOT call st.plotly_chart there
        # because doing so stacks both charts vertically inside the narrow left column.
        if _deferred_pft_fig is not None:
            st.markdown("<div class='section-card'><div class='section-title'>Net Profit Trend</div>", unsafe_allow_html=True)
            if _deferred_pft_pills:
                st.markdown(
                    "<div style='display:flex; gap:8px; margin-bottom:6px;'>"
                    + " ".join(_deferred_pft_pills)
                    + "</div>",
                    unsafe_allow_html=True,
                )
            if _pft_pill_had_break:
                st.markdown(
                    "<p style='font-size:16px; color:#111827; margin-top:4px; line-height:1.7;'>"
                    "⚠️ CAGR window shortened — an implausible single-year "
                    "swing was detected (possible causes: a demerger/spinoff/"
                    "restructuring, a one-off item, or a cyclical loss-to-profit "
                    "turnaround/low-base effect), so the pill only spans the "
                    "period after that break.</p>",
                    unsafe_allow_html=True,
                )
            st.plotly_chart(_deferred_pft_fig, use_container_width=True, config={"displayModeBar": True, "displaylogo": False, "modeBarButtonsToRemove": ["lasso2d", "select2d"]})
            st.markdown("</div>", unsafe_allow_html=True)
        elif _deferred_pft_fallback_df is not None:
            st.markdown("<div class='section-card'><div class='section-title'>Net Profit Trend</div>", unsafe_allow_html=True)
            st.bar_chart(_deferred_pft_fallback_df, color="#3B82F6")
            st.markdown("</div>", unsafe_allow_html=True)

        # ── Earnings Insights ────────────────────────────────────────────────
        if fin is not None and not fin.empty:
            try:
                st.markdown("<div class='section-card'><div class='section-title'>📈 Earnings Insights</div>", unsafe_allow_html=True)
                # Revenue and profit trend table
                rev_row_ei, profit_row_ei = None, None
                for rk in ["Total Revenue", "Revenue"]:
                    if rk in fin.index:
                        rev_row_ei = fin.loc[rk].dropna().sort_index(ascending=False)
                        break
                for pk in ["Net Income", "Net Income Common Stockholders"]:
                    if pk in fin.index:
                        profit_row_ei = fin.loc[pk].dropna().sort_index(ascending=False)
                        break

                if rev_row_ei is not None and len(rev_row_ei) >= 2:
                    ei_col1, ei_col2 = st.columns([2, 1])
                    with ei_col1:
                        # Built as one HTML string laid out with CSS grid
                        # (.ei-table / .ei-row) instead of nested st.columns.
                        # st.columns() auto-stacks each nested column onto its
                        # own line below ~640px width with no way to keep it
                        # in a row, which broke this into one field per line
                        # on phone. A CSS grid keeps Year/Revenue/Net Profit/
                        # Margin on the same row at any screen width, only
                        # shrinking font-size on small screens instead.
                        rev_vals = list(rev_row_ei.items())
                        pft_vals = list(profit_row_ei.items()) if profit_row_ei is not None else []

                        _ei_rows_html = []
                        for i, (dt, rv) in enumerate(rev_vals):
                            if i >= 4:
                                break
                            yr = f"FY{str(dt.year)[-2:]}"
                            rev_cr = rv / 1e7
                            pft_val = profit_row_ei.get(dt) if profit_row_ei is not None else None
                            pft_cr  = float(pft_val) / 1e7 if pft_val is not None and pd.notna(pft_val) else None

                            # Revenue YoY
                            if i < len(rev_vals) - 1:
                                prev_rv = rev_vals[i + 1][1]
                                rev_yoy = ((rv - prev_rv) / abs(prev_rv)) * 100 if prev_rv else 0
                                rev_yoy_color = TXT_GOOD if rev_yoy >= 0 else TXT_BAD
                                rev_yoy_html = f"<span style='color:{rev_yoy_color}; font-size:11px;'>({rev_yoy:+.1f}%)</span>"
                            else:
                                rev_yoy_html = ""

                            # Net Profit YoY — same logic, uses profit_row_ei ordered list
                            pft_yoy_html = ""
                            if pft_cr is not None and i < len(pft_vals) - 1:
                                prev_pft_val = pft_vals[i + 1][1]
                                if prev_pft_val and pd.notna(prev_pft_val) and prev_pft_val != 0:
                                    prev_pft_cr = float(prev_pft_val) / 1e7
                                    pft_yoy = ((pft_cr - prev_pft_cr) / abs(prev_pft_cr)) * 100
                                    pft_yoy_color = TXT_GOOD if pft_yoy >= 0 else TXT_BAD
                                    pft_yoy_html = f"<span style='color:{pft_yoy_color}; font-size:11px;'>({pft_yoy:+.1f}%)</span>"

                            # Net margin — separate column so it doesn't clash with YoY
                            margin_str = f"{pft_cr/rev_cr*100:.1f}%" if pft_cr is not None and rev_cr > 0 else "—"
                            margin_color = TXT_GOOD if pft_cr and pft_cr > 0 else TXT_BAD

                            pft_cell_html = (
                                f"<span style='color:#2563EB;'>₹{pft_cr:,.0f} Cr</span> {pft_yoy_html}"
                                if pft_cr is not None
                                else "<span style='color:#5B6673;'>—</span>"
                            )

                            # NOTE: built as single-line strings (no leading
                            # indentation) deliberately. Markdown treats any
                            # line starting with 4+ spaces as a literal code
                            # block, and this code lives deeply nested inside
                            # several `with`/`for` blocks — multi-line HTML
                            # here previously printed as raw tags instead of
                            # rendering, because the string literal captured
                            # that indentation as part of the content.
                            _ei_rows_html.append(
                                f"<div class='ei-row'>"
                                f"<div class='ei-cell ei-year'>{yr}</div>"
                                f"<div class='ei-cell ei-rev'><span style='color:#374151;'>₹{rev_cr:,.0f} Cr</span> {rev_yoy_html}</div>"
                                f"<div class='ei-cell ei-pft'>{pft_cell_html}</div>"
                                f"<div class='ei-cell ei-margin' style='color:{margin_color};'>{margin_str}</div>"
                                f"</div>"
                            )

                        _ei_table_html = (
                            "<div class='ei-table'>"
                            "<div class='ei-row ei-header'>"
                            "<div class='ei-cell ei-year'>Year</div>"
                            "<div class='ei-cell ei-rev'>Revenue</div>"
                            "<div class='ei-cell ei-pft'>Net Profit</div>"
                            "<div class='ei-cell ei-margin'>Margin</div>"
                            "</div>"
                            + ''.join(_ei_rows_html) +
                            "</div>"
                        )
                        st.markdown(_ei_table_html, unsafe_allow_html=True)

                    with ei_col2:
                        if rev_cagr is not None:
                            _rc_lbl = f"{rev_cagr_years}-yr Revenue CAGR" if rev_cagr_years else "Revenue CAGR"
                            st.metric(_rc_lbl, f"{rev_cagr:.1f}%", delta=None)
                        if profit_cagr is not None:
                            _pc_lbl = f"{profit_cagr_years}-yr Profit CAGR" if profit_cagr_years else "Profit CAGR"
                            st.metric(_pc_lbl, f"{profit_cagr:.1f}%", delta=None)

                    # Earnings summary — already generated inside combined_prompt
                    # (no extra LLM call needed)
                    earnings_summary = combined_data.get("earnings_summary", "")
                    if earnings_summary and not str(earnings_summary).startswith("⚠"):
                        st.markdown(f"<p style='font-size:16px; color:#374151; margin-top:0.8rem; line-height:1.7; font-style:italic;'>💡 {sanitize_llm_html(str(earnings_summary))}</p>", unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)
            except Exception:
                pass  # earnings section fails gracefully


        # ── Stock price chart ─────────────────────────────────────────────────
        st.markdown("<div class='section-card'><div class='section-title'>Stock Price</div>", unsafe_allow_html=True)

        period_col, spacer = st.columns([3, 5])
        with period_col:
            period_choice = st.radio("", ["1D", "1M", "3M", "6M", "1Y", "3Y"],
                horizontal=True, key="price_period", label_visibility="collapsed")

        # yfinance interval constraints:
        # - 2m: max 60 days (fine for 1D)
        # - 1d: max 2 years (use for 1M/3M/6M/1Y — more points than 1wk, shows real volatility)
        # - 1wk: any range (use for 3Y — ~156 points, clean signal)
        # Do NOT use 1wk for 1Y — 52 points hides intra-week swings visible on 1d (~250 pts)
        period_map = {
            "1D":  ("1d",  "2m",  "%H:%M",   "%d %b %H:%M"),
            "1M":  ("1mo", "1d",  "%d %b",   "%d %b %Y"),
            "3M":  ("3mo", "1d",  "%d %b",   "%d %b %Y"),
            "6M":  ("6mo", "1d",  "%b '%y",  "%d %b %Y"),
            "1Y":  ("1y",  "1d",  "%b '%y",  "%d %b %Y"),
            "3Y":  ("3y",  "1wk", "%b %Y",   "%b %Y"),
        }
        hist_period, hist_interval, x_fmt, tooltip_fmt = period_map[period_choice]

        try:
            price_hist = fetch_price_history(ticker, hist_period, hist_interval)
            if price_hist is not None and not price_hist.empty:
                price_hist.index = pd.to_datetime(price_hist.index)
                closes = price_hist["Close"].dropna()

                if not closes.empty:
                    import altair as alt

                    chart_df = pd.DataFrame({
                        "Time":  closes.index,
                        "Price": closes.values,
                    })

                    # Y-axis padding:
                    # 1D — 15% pad so small intraday moves fill the chart area
                    # multi-day — 5% pad; swings are already visible at this scale
                    y_min = closes.min()
                    y_max = closes.max()
                    pad_pct = 0.15 if period_choice == "1D" else 0.05
                    pad = (y_max - y_min) * pad_pct if y_max != y_min else y_max * 0.01
                    y_lo = y_min - pad
                    y_hi = y_max + pad

                    # Colour direction:
                    # 1D  → green if current >= yesterday's close
                    # else → green if last close in window >= first close in window
                    if period_choice == "1D":
                        is_up = prev_close is not None and closes.iloc[-1] >= prev_close
                    else:
                        is_up = closes.iloc[-1] >= closes.iloc[0]
                    line_color = "#22C55E" if is_up else "#EF4444"

                    # "mouseover" only fires for an actual mouse, so this
                    # tooltip never appeared on touchscreens. "pointerover"
                    # is the unified mouse+touch+pen event, so a single,
                    # valid event name here covers both desktop hover and a
                    # mobile tap/drag. (My earlier attempt strung together
                    # several event names with commas/brackets into one
                    # string, which isn't valid Vega event-stream syntax and
                    # silently broke hover everywhere, including desktop —
                    # this reverts to something simple that actually works.)
                    nearest = alt.selection_point(
                        name="hover", nearest=True, on="pointerover",
                        fields=["Time"], empty=False
                    )

                    base = alt.Chart(chart_df)

                    line = (
                        base
                        .mark_line(color=line_color, strokeWidth=1.8)
                        .encode(
                            x=alt.X(
                                "Time:T",
                                axis=alt.Axis(
                                    format=x_fmt,
                                    labelColor="#6B7280",
                                    gridColor="#E5E7EB",
                                    tickColor="#E5E7EB",
                                    labelAngle=0,
                                ),
                            ),
                            y=alt.Y(
                                "Price:Q",
                                scale=alt.Scale(domain=[y_lo, y_hi]),
                                axis=alt.Axis(
                                    format=",.0f",
                                    labelColor="#6B7280",
                                    gridColor="#E5E7EB",
                                    tickColor="#E5E7EB",
                                ),
                            ),
                        )
                    )

                    # Invisible wide selectors — capture hover anywhere along x
                    selectors = (
                        base
                        .mark_point(opacity=0)
                        .encode(x="Time:T", opacity=alt.value(0))
                        .add_params(nearest)
                    )

                    # Dot that snaps to the nearest data point
                    points = (
                        line
                        .mark_point(color=line_color, size=60, filled=True)
                        .encode(opacity=alt.condition(nearest, alt.value(1), alt.value(0)))
                    )

                    # Vertical rule at hover position
                    rules = (
                        base
                        .mark_rule(color="#4B5563", strokeWidth=1, strokeDash=[4, 2])
                        .encode(x="Time:T")
                        .transform_filter(nearest)
                    )

                    # Tooltip layer — Vega-Lite's built-in floating DOM tooltip
                    # (shown here as a bonus on desktop where native hover is
                    # reliable), but this alone is NOT the mobile fix below.
                    tooltip_layer = (
                        line
                        .mark_point(opacity=0, size=200)
                        .encode(
                            tooltip=[
                                alt.Tooltip("Time:T", format=tooltip_fmt, title="Date"),
                                alt.Tooltip("Price:Q", format=",.2f", title="Price (₹)"),
                            ]
                        )
                        .transform_filter(nearest)
                    )

                    # In-chart price/date readout — the actual mobile fix.
                    # Vega-Lite's floating tooltip above depends on the
                    # browser continuously firing native hover events while
                    # the pointer moves; several mobile browsers only fire a
                    # single touch event and never open (or immediately
                    # close) that floating DOM tooltip, which is why only
                    # the axis label / vertical rule was visible on phone
                    # but never the price. These two text marks are driven
                    # by the same "nearest" selection that already reliably
                    # drives the rule and snapped dot on touch (per the
                    # pointerover fix above) — being part of the chart's own
                    # SVG rather than a separate hover-triggered DOM element,
                    # they render identically on desktop and mobile alike.
                    price_readout = (
                        line
                        .mark_text(align="left", baseline="top", fontSize=17, fontWeight="bold",
                                   color=line_color, dx=4, dy=4)
                        .encode(
                            x=alt.value(0), y=alt.value(0),
                            text=alt.Text("Price:Q", format=",.2f"),
                        )
                        .transform_filter(nearest)
                    )
                    date_readout = (
                        line
                        .mark_text(align="left", baseline="top", fontSize=11,
                                   color="#6B7280", dx=4, dy=26)
                        .encode(
                            x=alt.value(0), y=alt.value(0),
                            text=alt.Text("Time:T", format=tooltip_fmt),
                        )
                        .transform_filter(nearest)
                    )

                    chart = (
                        alt.layer(line, selectors, points, rules, tooltip_layer, price_readout, date_readout)
                        .properties(height=280, background="transparent")
                        .configure_view(strokeWidth=0, fill="transparent")
                        .configure_axis(domainColor="#E2E4E9", labelFontSize=11)
                    )
                    st.altair_chart(chart, use_container_width=True)

                    # Intraday stats strip (1D only)
                    if period_choice == "1D" and "High" in price_hist.columns and "Low" in price_hist.columns:
                        day_high = price_hist["High"].max()
                        day_low  = price_hist["Low"].min()
                        day_open = price_hist["Open"].iloc[0] if "Open" in price_hist.columns else None
                        strip_parts = []
                        if day_open is not None:
                            strip_parts.append(f"<span style='color:#5B6673;'>Open</span> &nbsp;<span style='color:#1F2937; font-weight:600;'>₹{day_open:,.1f}</span>")
                        strip_parts.append(f"<span style='color:#5B6673;'>Day High</span> &nbsp;<span style='color:#15803D; font-weight:600;'>₹{day_high:,.1f}</span>")
                        strip_parts.append(f"<span style='color:#5B6673;'>Day Low</span> &nbsp;<span style='color:#B91C1C; font-weight:600;'>₹{day_low:,.1f}</span>")
                        st.markdown(
                            "<div style='display:flex; gap:24px; margin-top:4px; font-size:13px;'>"
                            + "".join(f"<div>{p}</div>" for p in strip_parts)
                            + "</div>",
                            unsafe_allow_html=True,
                        )

                    # Period return badge (non-1D) — shows % gain/loss over the visible window
                    elif period_choice != "1D":
                        period_return = ((closes.iloc[-1] - closes.iloc[0]) / closes.iloc[0]) * 100
                        ret_color = TXT_GOOD if period_return >= 0 else TXT_BAD
                        ret_label = {"1M": "1-Month", "3M": "3-Month", "6M": "6-Month", "1Y": "1-Year", "3Y": "3-Year"}[period_choice]
                        st.markdown(
                            f"<div style='font-size:13px; margin-top:4px;'>"
                            f"<span style='color:#5B6673;'>{ret_label} Return</span> &nbsp;"
                            f"<span style='color:{ret_color}; font-weight:600;'>{period_return:+.1f}%</span>"
                            f"</div>",
                            unsafe_allow_html=True,
                        )

                    # 52W high/low (all periods)
                    week52_high = info.get("fiftyTwoWeekHigh")
                    week52_low  = info.get("fiftyTwoWeekLow")
                    if week52_high is not None and week52_low is not None:
                        current = info.get("currentPrice") or info.get("regularMarketPrice", 0)
                        pct_from_high = (current - week52_high) / week52_high * 100
                        pct_from_low  = (current - week52_low)  / week52_low  * 100
                        st.markdown(f"""
                        <div style='display:flex; gap:24px; margin-top:8px; font-size:13px;'>
                          <div><span style='color:#5B6673;'>52W Low</span> &nbsp;
                            <span style='color:#1F2937; font-weight:600;'>₹{week52_low:,.1f}</span>
                            <span style='color:#15803D; font-size:11px;'> ({pct_from_low:+.1f}% from low)</span>
                          </div>
                          <div><span style='color:#5B6673;'>52W High</span> &nbsp;
                            <span style='color:#1F2937; font-weight:600;'>₹{week52_high:,.1f}</span>
                            <span style='color:#B91C1C; font-size:11px;'> ({pct_from_high:+.1f}% from high)</span>
                          </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("Price chart unavailable for this ticker.")
            else:
                st.info("Price chart unavailable for this ticker.")
        except Exception:
            st.info("Price chart unavailable.")

        st.markdown("</div>", unsafe_allow_html=True)


        # ── Competitive Moat ─────────────────────────────────────────────
        if _MODULES_LOADED:
            st.markdown("<div class='section-card'><div class='section-title'>🏰 Competitive Moat</div>", unsafe_allow_html=True)
            try:
                # Use pre-computed moat result from the parallel LLM block above.
                # If unavailable (e.g. modules not loaded), fall back to rule-based.
                if _moat_result is not None:
                    moat = _moat_result
                else:
                    try:
                        moat = get_moat_analysis(
                            sector, industry,
                            roe_raw=roe, de_raw=de, revenue_cagr=rev_cagr,
                            name=name, ticker=ticker,
                            profit_margin_raw=profit_margin,
                            pe=pe,
                            mkt_cap_cr=(mkt_cap / 1e7) if mkt_cap else None,
                            ask_llm_fn=ask_llm,
                            description=business_context,
                        )
                    except TypeError:
                        moat = get_moat_analysis(
                            sector, industry,
                            roe_raw=roe, de_raw=de, revenue_cagr=rev_cagr,
                        )
                # Text colours (rating label + score pill), so text-safe steps.
                moat_color = {"Weak": TXT_BAD, "Moderate": TXT_WARN, "Strong": TXT_GOOD}.get(moat["rating"], TXT_MUTED)
                moat_score = moat.get("score", "—")
                st.markdown(f"""
                <div style='text-align:center; margin-bottom:0.8rem;'>
                  <span style='font-size:1.6rem; font-weight:700; color:{moat_color};'>{moat["rating"]}</span>
                  <span style='font-size:0.9rem; color:#5B6673;'> Moat</span>
                  <div style='display:inline-block; margin-left:10px; background:#F5F6F8; border:1px solid {moat_color}; border-radius:20px; padding:2px 12px; font-size:12px; font-weight:700; color:{moat_color};'>{moat_score}/10</div>
                </div>
                """, unsafe_allow_html=True)
                # LLM verdict (company-specific), if available
                if moat.get("llm_verdict"):
                    st.markdown(f"<p style='font-size:12.5px; color:#5B6673; line-height:1.6; margin-bottom:0.8rem;'>{moat['llm_verdict']}</p>", unsafe_allow_html=True)
                # Key sources of moat (sector-specific factors)
                if moat.get("factors"):
                    _strength_icon = {
                        "Strong": ("✓", "#22C55E"),
                        "Moderate": ("~", "#F59E0B"),
                        "Weak": ("✗", "#6B7280"),
                    }
                    moat_list_html = "".join(
                        f"<div style='font-size:12px; color:#374151; padding:4px 0; border-bottom:1px solid #E2E4E9;'>"
                        f"<span style='color:{_strength_icon.get(f.get('strength'), ('✓','#22C55E'))[1]}; margin-right:6px;'>"
                        f"{_strength_icon.get(f.get('strength'), ('✓','#22C55E'))[0]}</span>"
                        f"<b>{f['factor']}</b> — {f['description']}</div>"
                        for f in moat["factors"]
                    )
                    st.markdown(f"<div style='margin-top:8px;'>{moat_list_html}</div>", unsafe_allow_html=True)
                # Bull case
                if moat.get("bull_case"):
                    st.markdown("<div style='font-size:15px; font-weight:700; color:#5B6673; text-transform:uppercase; letter-spacing:0.5px; margin-top:10px; margin-bottom:4px;'>Bull Case</div>", unsafe_allow_html=True)
                    bull_html = "".join(
                        f"<div style='font-size:12px; color:#374151; padding:4px 0; border-bottom:1px solid #E2E4E9;'>"
                        f"<span style='color:#15803D; margin-right:6px;'>✓</span>{b}</div>"
                        for b in moat["bull_case"]
                    )
                    st.markdown(f"<div>{bull_html}</div>", unsafe_allow_html=True)
                # Bear case
                if moat.get("bear_case"):
                    st.markdown("<div style='font-size:15px; font-weight:700; color:#5B6673; text-transform:uppercase; letter-spacing:0.5px; margin-top:10px; margin-bottom:4px;'>Bear Case</div>", unsafe_allow_html=True)
                    bear_html = "".join(
                        f"<div style='font-size:12px; color:#5B6673; padding:4px 0; border-bottom:1px solid #E5E7EB;'>"
                        f"<span style='color:#B45309; margin-right:6px;'>⚠</span>{w}</div>"
                        for w in moat["bear_case"]
                    )
                    st.markdown(f"<div>{bear_html}</div>", unsafe_allow_html=True)
            except Exception:
                st.info("Moat analysis unavailable.")
            st.markdown("</div>", unsafe_allow_html=True)


        # ── Latest news ──────────────────────────────────────────────────────
        st.markdown("<div class='section-card'><div class='section-title'>Latest News</div>", unsafe_allow_html=True)
        try:
            _news_result = fetch_relevant_news(ticker, name)
            search_terms = _news_result["search_terms"]
            relevant_articles = _news_result["relevant_articles"]
            _news_error = _news_result["error"]
            if _news_error == "no_key":
                raise KeyError("NEWS_API_KEY")  # matches legacy behavior: falls to outer except below
            elif _news_error == "rate_limit":
                st.warning("⚠ News unavailable — NewsAPI rate limit reached. Try again in a few minutes.")
            elif _news_error == "invalid_key":
                st.warning("⚠ News unavailable — invalid NewsAPI key. Check your NEWS_API_KEY in secrets.toml.")
            elif _news_error == "http_error":
                st.warning(f"⚠ News unavailable — NewsAPI returned status {_news_result['error_detail']}.")
            elif _news_error == "api_error":
                st.warning(f"⚠ News unavailable — {_news_result['error_detail']}.")


            articles_to_use = relevant_articles[:6]

            if articles_to_use:
                # ── Use rule-based sentiment + deduplication from modules ─────
                if _MODULES_LOADED:
                    # Deduplicate first, then enrich with rule-based sentiment
                    articles_to_use = deduplicate_articles(relevant_articles[:10])[:6]
                    enriched = enrich_articles(articles_to_use)
                    overall_sent = compute_overall_sentiment(enriched)

                    # Overall sentiment score banner
                    st.markdown(f"""
                    <div style='display:flex; align-items:center; gap:12px; background:#F3F4F6; border:1px solid #E2E4E9; border-radius:10px; padding:10px 14px; margin-bottom:12px;'>
                      <span style='font-size:1.2rem;'>{overall_sent["icon"]}</span>
                      <div>
                        <div style='font-size:13px; font-weight:600; color:{overall_sent["color"]};'>Overall Sentiment: {overall_sent["label"]}</div>
                        <div style='font-size:11px; color:#5B6673;'>
                          🟢 {overall_sent["positive"]} positive &nbsp;·&nbsp;
                          🟡 {overall_sent["neutral"]} neutral &nbsp;·&nbsp;
                          🔴 {overall_sent["negative"]} negative &nbsp;·&nbsp;
                          from {len(enriched)} articles
                        </div>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)

                    for i, article in enumerate(enriched[:5]):
                        sent = article["sentiment"]
                        # Light tints — these were dark-theme leftovers; with text darkened
                        # for the light UI, dark-on-dark measured 1.28:1.
                        sent_bg = "#ECFDF3" if sent["label"] == "Positive" else "#FEF2F2" if sent["label"] == "Negative" else "#F1F3F5"
                        source = article.get("source", {}).get("name", "")
                        pub_date = (article.get("publishedAt", "") or "")[:10]
                        title = article.get("title", "")
                        desc = (article.get("description", "") or "")[:140]
                        url = article.get("url", "#")
                        st.markdown(f"""
                        <div style='padding:10px 0; border-bottom:1px solid #E2E4E9;'>
                          <span style='background:{sent_bg}; color:{sent["color"]}; font-size:11px; font-weight:500; padding:2px 8px; border-radius:4px;'>{sent["icon"]} {sent["label"]}</span>
                          <a href='{url}' target='_blank' style='font-size:13px; font-weight:500; color:#1F2937; margin-left:8px; text-decoration:none;'>{title}</a>
                          <div style='font-size:12px; color:#5B6673; margin-top:4px;'>{desc}</div>
                          <div style='font-size:11px; color:var(--ink-muted); margin-top:2px;'>{source} {f'· {pub_date}' if pub_date else ''}</div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    # Original LLM-based sentiment path
                    articles_to_use = relevant_articles[:6]
                    headlines_text = "\n".join([
                        f"- {a['title']} | {a.get('description','')[:100]}"
                        for a in articles_to_use if a.get('title')
                    ])
                    sentiment_prompt_llm = f"""
                    Summarize these news headlines about {name} for an Indian retail investor.
                    For each, return: title (max 8 words), 1-sentence summary, sentiment (Positive/Neutral/Negative).
                    Headlines:
                    {headlines_text}
                    Return ONLY valid JSON array: [{{"title":"...", "summary":"...", "sentiment":"Positive"}}]
                    """
                    with st.spinner("Analysing news..."):
                        sent_raw = ask_llm(sentiment_prompt_llm, "Return only valid JSON array.", model="openai/gpt-oss-20b")
                    sent_clean = sent_raw.strip()
                    if sent_clean.startswith("```"):
                        parts = sent_clean.split("```")
                        sent_clean = parts[1][4:].strip() if len(parts) > 1 else sent_clean
                    arr_start = sent_clean.find("[")
                    arr_end = sent_clean.rfind("]") + 1
                    if arr_start != -1 and arr_end > arr_start:
                        sent_clean = sent_clean[arr_start:arr_end]
                    try:
                        news_items = json.loads(sent_clean)
                    except Exception:
                        news_items = [{"title": a.get("title",""), "summary": a.get("description","") or "", "sentiment": "Neutral"} for a in articles_to_use]

                    for i, item in enumerate(news_items[:5]):
                        sent = item.get("sentiment", "Neutral")
                        sent_color = TXT_GOOD if sent == "Positive" else TXT_BAD if sent == "Negative" else TXT_MUTED
                        sent_bg = "#ECFDF3" if sent == "Positive" else "#FEF2F2" if sent == "Negative" else "#F1F3F5"
                        source = articles_to_use[i].get("source", {}).get("name", "") if i < len(articles_to_use) else ""
                        pub_date = (articles_to_use[i].get("publishedAt", "") or "")[:10] if i < len(articles_to_use) else ""
                        st.markdown(f"""
                        <div style='padding:10px 0; border-bottom:1px solid #E2E4E9;'>
                          <span style='background:{sent_bg}; color:{sent_color}; font-size:11px; font-weight:500; padding:2px 8px; border-radius:4px;'>{sent}</span>
                          <span style='font-size:13px; font-weight:500; color:#1F2937; margin-left:8px;'>{item["title"]}</span>
                          <div style='font-size:12px; color:#5B6673; margin-top:4px;'>{item["summary"]}</div>
                          <div style='font-size:11px; color:var(--ink-muted); margin-top:2px;'>{source} {f'· {pub_date}' if pub_date else ''}</div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("No recent news found for this company.")
        except Exception:
            st.info("News unavailable at the moment.")

        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div class='disclaimer'>⚠ EquiEye AI is for educational purposes only. This is not financial advice. Always consult a SEBI-registered advisor before investing.</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Compare-tab helper functions — defined at module level so they are not
# re-created on every Streamlit rerun (previously lived inside `with tab_compare:`).
# ─────────────────────────────────────────────────────────────────────────────

# Compare Stocks scoring/formatting helpers: extracted verbatim to
# services/comparison.py (Phase 1 service-layer extraction) — pure logic,
# no Streamlit dependency. Aliased back to the original names so no call
# site below needs to change. fmt_de_compare -> _fmt_de since this file
# already has a distinct `fmt_de` (services.formatters) imported earlier
# for the main Stock Research page — these are two different formatters
# that have always coexisted under different names.
from services.comparison import (
    cagr_from_fin as _cagr_from_fin,
    cmp_eps_cagr as _cmp_eps_cagr,
    val_badge as _val_badge,
    winner as _winner,
    cell as _cell,
    fmt_pct as _fmt_pct,
    fmt_cagr as _fmt_cagr,
    fmt_de_compare as _fmt_de,
    fmt_pe as _fmt_pe,
    score_stock as _score_stock,
)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 2: STOCK COMPARISON  (premium investor-grade)
# ─────────────────────────────────────────────────────────────────────────────
with tab_compare:
    # plotly is imported at module level as _pgo; re-alias here for readability
    go = _pgo

    st.markdown("<h3 style='color:#111827; font-size:1.7rem; margin-bottom:0.3rem;'>⚖️ Stock Comparison</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color:#5B6673; font-size:13px; margin-bottom:1.2rem;'>Side-by-side investor-grade analysis with winner highlighting, growth metrics, and radar chart.</p>", unsafe_allow_html=True)

    with st.form(key="compare_form"):
        c1, c2, c3 = st.columns([2, 2, 1])
        with c1:
            stock_a = st.text_input("Stock A", placeholder="e.g. TCS", key="comp_a")
        with c2:
            stock_b = st.text_input("Stock B", placeholder="e.g. Infosys", key="comp_b")
        with c3:
            st.markdown("<br>", unsafe_allow_html=True)
            compare_btn = st.form_submit_button("Compare →")

    # ── Session-state init ────────────────────────────────────────────────────
    for _k, _v in [
        ("compare_matches_a", None), ("compare_matches_b", None),
        ("compare_ticker_a",  None), ("compare_ticker_b",  None),
        ("compare_label_a",   ""),   ("compare_label_b",   ""),
    ]:
        if _k not in st.session_state:
            st.session_state[_k] = _v

    if compare_btn and stock_a and stock_b:
        st.session_state.compare_label_a = stock_a
        st.session_state.compare_label_b = stock_b
        st.session_state.compare_ticker_a = None
        st.session_state.compare_ticker_b = None
        matches_a = search_nse_matches(stock_a)
        matches_b = search_nse_matches(stock_b)
        st.session_state.compare_matches_a = matches_a if len(matches_a) > 1 else None
        st.session_state.compare_matches_b = matches_b if len(matches_b) > 1 else None
        if matches_a and len(matches_a) == 1:
            st.session_state.compare_ticker_a = matches_a[0][0]
        if matches_b and len(matches_b) == 1:
            st.session_state.compare_ticker_b = matches_b[0][0]

    # Disambiguation pickers
    if st.session_state.compare_matches_a:
        st.markdown(f"<p style='color:#5B6673; font-size:13px;'>Multiple matches for '{st.session_state.compare_label_a}' — pick one:</p>", unsafe_allow_html=True)
        cols = st.columns(min(3, len(st.session_state.compare_matches_a)))
        for i, (sym, lname) in enumerate(st.session_state.compare_matches_a):
            with cols[i % 3]:
                if st.button(f"{lname}\n({sym})", key=f"cmp_a_{i}_{sym}"):
                    st.session_state.compare_ticker_a = sym
                    st.session_state.compare_matches_a = None
                    st.rerun()

    if st.session_state.compare_matches_b:
        st.markdown(f"<p style='color:#5B6673; font-size:13px;'>Multiple matches for '{st.session_state.compare_label_b}' — pick one:</p>", unsafe_allow_html=True)
        cols = st.columns(min(3, len(st.session_state.compare_matches_b)))
        for i, (sym, lname) in enumerate(st.session_state.compare_matches_b):
            with cols[i % 3]:
                if st.button(f"{lname}\n({sym})", key=f"cmp_b_{i}_{sym}"):
                    st.session_state.compare_ticker_b = sym
                    st.session_state.compare_matches_b = None
                    st.rerun()

    ticker_a = st.session_state.compare_ticker_a
    ticker_b = st.session_state.compare_ticker_b

    if ticker_a and ticker_b:
        _fetch_error = None
        info_a, fin_a, bs_a = {}, None, None
        info_b, fin_b, bs_b = {}, None, None
        with st.spinner("Fetching data for both stocks…"):
            try:
                info_a, _, fin_a, bs_a, _ = fetch_stock(ticker_a)
            except Exception:
                _fetch_error = f"Could not fetch data for {ticker_a}. Try a different ticker."
            if _fetch_error is None:
                try:
                    info_b, _, fin_b, bs_b, _ = fetch_stock(ticker_b)
                except Exception:
                    _fetch_error = f"Could not fetch data for {ticker_b}. Try a different ticker."
        # st.stop() is called OUTSIDE the spinner context so the spinner
        # closes cleanly before Streamlit halts the script.
        if _fetch_error:
            st.error(_fetch_error)
            st.stop()

        if not info_a.get("currentPrice") and not info_a.get("regularMarketPrice"):
            st.error(f"No live data for {ticker_a}. Yahoo Finance may be throttling — try again.")
            st.stop()
        if not info_b.get("currentPrice") and not info_b.get("regularMarketPrice"):
            st.error(f"No live data for {ticker_b}. Yahoo Finance may be throttling — try again.")
            st.stop()

        name_a = info_a.get("longName", ticker_a)
        name_b = info_b.get("longName", ticker_b)
        short_a = ticker_a.replace(".NS", "")
        short_b = ticker_b.replace(".NS", "")

        # ── Helper: compute CAGRs from financials DataFrame ───────────────────
        rev_cagr_a, rev_yoy_a, rev_cagr_n_a = _cagr_from_fin(fin_a, ["Total Revenue", "Revenue", "Total Revenues"])
        rev_cagr_b, rev_yoy_b, rev_cagr_n_b = _cagr_from_fin(fin_b, ["Total Revenue", "Revenue", "Total Revenues"])
        profit_cagr_a, profit_yoy_a, profit_cagr_n_a = _cagr_from_fin(fin_a, ["Net Income", "Net Income Common Stockholders", "Net Income From Continuing Operations"])
        profit_cagr_b, profit_yoy_b, profit_cagr_n_b = _cagr_from_fin(fin_b, ["Net Income", "Net Income Common Stockholders", "Net Income From Continuing Operations"])
        eps_cagr_a = _cmp_eps_cagr(info_a, fin_a)
        eps_cagr_b = _cmp_eps_cagr(info_b, fin_b)

        # ── Valuation badges using existing sector-aware PE bands ─────────────
        pe_a = info_a.get("trailingPE")
        pe_b = info_b.get("trailingPE")
        sect_a = info_a.get("sector", ""); ind_a = info_a.get("industry", "")
        sect_b = info_b.get("sector", ""); ind_b = info_b.get("industry", "")
        badge_a = _val_badge(pe_a, sect_a, ind_a, pb=info_a.get("priceToBook"), name=name_a, description=info_a.get("longBusinessSummary", ""))
        badge_b = _val_badge(pe_b, sect_b, ind_b, pb=info_b.get("priceToBook"), name=name_b, description=info_b.get("longBusinessSummary", ""))

        # ── Raw numeric values for winner logic ───────────────────────────────
        roe_a   = info_a.get("returnOnEquity")   # fraction
        roe_b   = info_b.get("returnOnEquity")
        de_a    = info_a.get("debtToEquity")      # yfinance: already in % form → divide by 100 for display
        de_b    = info_b.get("debtToEquity")
        pm_a    = info_a.get("profitMargins")     # fraction
        pm_b    = info_b.get("profitMargins")
        rev_a   = info_a.get("totalRevenue")
        rev_b   = info_b.get("totalRevenue")
        price_a = info_a.get("currentPrice") or info_a.get("regularMarketPrice")
        price_b = info_b.get("currentPrice") or info_b.get("regularMarketPrice")
        mcap_a  = info_a.get("marketCap")
        mcap_b  = info_b.get("marketCap")

        pb_a = info_a.get("priceToBook")
        pb_b = info_b.get("priceToBook")
        _extra_a = {
            "fcf": info_a.get("freeCashflow"), "ocf": info_a.get("operatingCashflow"),
            "revenue": rev_a, "roa": info_a.get("returnOnAssets"), "pb_ratio": pb_a,
            "ev_ebitda": info_a.get("enterpriseToEbitda"),
            "price_to_sales": info_a.get("priceToSalesTrailing12Months"),
        }
        _extra_b = {
            "fcf": info_b.get("freeCashflow"), "ocf": info_b.get("operatingCashflow"),
            "revenue": rev_b, "roa": info_b.get("returnOnAssets"), "pb_ratio": pb_b,
            "ev_ebitda": info_b.get("enterpriseToEbitda"),
            "price_to_sales": info_b.get("priceToSalesTrailing12Months"),
        }
        score_a, pillars_a = _score_stock(pe_a, roe_a, de_a, pm_a, rev_cagr_a, profit_cagr_a, sect_a, ind_a, pb=pb_a, extra_metrics=_extra_a, name=name_a, description=info_a.get("longBusinessSummary", ""))
        score_b, pillars_b = _score_stock(pe_b, roe_b, de_b, pm_b, rev_cagr_b, profit_cagr_b, sect_b, ind_b, pb=pb_b, extra_metrics=_extra_b, name=name_b, description=info_b.get("longBusinessSummary", ""))

        # ── Reasons for overall winner ────────────────────────────────────────
        winner_name = short_a if score_a >= score_b else short_b
        loser_name  = short_b if score_a >= score_b else short_a
        reasons = []
        if _winner(roe_a, roe_b, True)  == ("a" if score_a >= score_b else "b"): reasons.append("Higher ROE")
        if _winner(pm_a,  pm_b,  True)  == ("a" if score_a >= score_b else "b"): reasons.append("Better profit margins")
        if _winner(rev_cagr_a, rev_cagr_b, True) == ("a" if score_a >= score_b else "b"): reasons.append("Stronger revenue growth")
        if _winner(profit_cagr_a, profit_cagr_b, True) == ("a" if score_a >= score_b else "b"): reasons.append("Higher profit CAGR")
        if _winner(pe_a,  pe_b,  False) == ("a" if score_a >= score_b else "b"): reasons.append("Better valuation")
        if _winner(de_a,  de_b,  False) == ("a" if score_a >= score_b else "b"): reasons.append("Cleaner balance sheet")
        if _winner(rev_a, rev_b, True)  == ("a" if score_a >= score_b else "b"): reasons.append("Larger revenue scale")
        if not reasons:
            reasons = ["Overall stronger fundamentals"]
        reasons_html = " &nbsp;·&nbsp; ".join(f"✓ {r}" for r in reasons[:4])

        # ── OVERALL WINNER CARD ───────────────────────────────────────────────
        winner_score = score_a if score_a >= score_b else score_b
        loser_score  = score_b if score_a >= score_b else score_a
        tie_game = abs(score_a - score_b) < 0.3
        if tie_game:
            winner_headline = f"⚖️ &nbsp;TOO CLOSE TO CALL: {short_a} vs {short_b}"
            winner_subtitle = "Both companies have very similar overall scores — the better choice depends on your investment thesis."
        else:
            winner_headline = f"🏆 &nbsp;OVERALL WINNER: {winner_name}"
            winner_subtitle = reasons_html

        st.markdown(f"""
        <div class='winner-card'>
          <div class='winner-title'>{winner_headline}</div>
          <div style='font-size:13px; color:#5B6673; margin-bottom:0.9rem;'>{winner_subtitle}</div>
          <div style='display:flex; align-items:center; gap:12px; flex-wrap:wrap;'>
            <span class='score-pill score-pill-a'>{short_a} &nbsp; {score_a}/10</span>
            <span class='score-pill score-pill-b'>{short_b} &nbsp; {score_b}/10</span>
            <span style='font-size:11px; color:var(--ink-muted); margin-left:4px;'>Compare score: Valuation 25% · Profitability 25% · Growth 25% · Balance Sheet 25% &nbsp;|&nbsp; <i>Main Health Score uses different weights (Val 30%, Prof 25%, Growth 25%, BS 20%)</i></span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # ── COMPANY HEADERS with valuation badges ─────────────────────────────
        sector_label_a = sector_label_b = ""
        if _MODULES_LOADED:
            try:
                sector_label_a = f"<span style='font-size:10px; color:#5B6673; margin-left:6px;'>· {classify_sector(sect_a, ind_a, name_a, info_a.get('longBusinessSummary', '')).replace('_',' ').title()}</span>"
                sector_label_b = f"<span style='font-size:10px; color:#5B6673; margin-left:6px;'>· {classify_sector(sect_b, ind_b, name_b, info_b.get('longBusinessSummary', '')).replace('_',' ').title()}</span>"
            except Exception:
                pass

        st.markdown(f"""
        <div class='compare-grid compare-header' style='background:#F3F4F6; border-radius:10px 10px 0 0; margin-bottom:0;'>
          <div style='padding:12px 10px; font-size:11px; color:#5B6673; font-weight:700; text-transform:uppercase; letter-spacing:1px; border-bottom:2px solid #E2E4E9;'>Metric</div>
          <div style='padding:12px 10px; border-bottom:2px solid #22C55E;'>
            <span style='font-size:14px; color:#15803D; font-weight:700;'>{name_a}</span><br>
            <span style='font-size:11px; color:#5B6673;'>{short_a} &nbsp;</span>{badge_a}{sector_label_a}
          </div>
          <div style='padding:12px 10px; border-bottom:2px solid #3B82F6;'>
            <span style='font-size:14px; color:#2563EB; font-weight:700;'>{name_b}</span><br>
            <span style='font-size:11px; color:#5B6673;'>{short_b} &nbsp;</span>{badge_b}{sector_label_b}
          </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Helper: render one compare row ────────────────────────────────────
        def _row(label, disp_a, disp_b, winner):
            return f"""
            <div class='compare-grid'>
              <div style='padding:10px; font-size:13px; color:#5B6673; border-bottom:1px solid #E5E7EB;'>{label}</div>
              {_cell(disp_a, winner, 'a')}
              {_cell(disp_b, winner, 'b')}
            </div>"""

        # ── Helper: section header row ────────────────────────────────────────
        def _section_head(label):
            return f"<div class='cmp-section-head'>{label}</div>"

        # ── Build the full metrics table HTML ─────────────────────────────────
        table_html = "<div style='border:1px solid #E2E4E9; border-radius:0 0 10px 10px; overflow:hidden; margin-bottom:1.2rem;'>"

        # — VALUATION —
        table_html += _section_head("📊 Valuation")
        table_html += _row("Price",       f"₹{price_a:,.1f}" if price_a is not None else "N/A",
                                           f"₹{price_b:,.1f}" if price_b is not None else "N/A",
                                           "na")
        table_html += _row("Market Cap",  fmt_crore(mcap_a), fmt_crore(mcap_b),
                           "na")   # informational — larger MCap ≠ better investment
        table_html += _row("P/E Ratio",   _fmt_pe(pe_a), _fmt_pe(pe_b),
                           _winner(pe_a, pe_b, False))   # lower P/E = better

        # — PROFITABILITY —
        table_html += _section_head("💰 Profitability")
        table_html += _row("ROE",          _fmt_pct(roe_a), _fmt_pct(roe_b),
                           _winner(roe_a, roe_b, True))
        table_html += _row("TTM Profit Margin", _fmt_pct(pm_a), _fmt_pct(pm_b),
                           _winner(pm_a, pm_b, True))
        table_html += _row("TTM Revenue",       fmt_crore(rev_a), fmt_crore(rev_b),
                           _winner(rev_a, rev_b, True))

        # — GROWTH —
        table_html += _section_head("🚀 Growth")
        table_html += _row("Revenue CAGR",  _fmt_cagr(rev_cagr_a, rev_cagr_n_a),    _fmt_cagr(rev_cagr_b, rev_cagr_n_b),
                           _winner(rev_cagr_a, rev_cagr_b, True))
        table_html += _row("Profit CAGR",   _fmt_cagr(profit_cagr_a, profit_cagr_n_a), _fmt_cagr(profit_cagr_b, profit_cagr_n_b),
                           _winner(profit_cagr_a, profit_cagr_b, True))
        table_html += _row("NI/Share CAGR",  _fmt_cagr(eps_cagr_a),    _fmt_cagr(eps_cagr_b),
                           _winner(eps_cagr_a, eps_cagr_b, True))
        table_html += _row("Revenue YoY",   _fmt_cagr(rev_yoy_a),     _fmt_cagr(rev_yoy_b),
                           _winner(rev_yoy_a, rev_yoy_b, True))
        table_html += _row("Profit YoY",    _fmt_cagr(profit_yoy_a),  _fmt_cagr(profit_yoy_b),
                           _winner(profit_yoy_a, profit_yoy_b, True))

        # — BALANCE SHEET —
        table_html += _section_head("🏦 Balance Sheet")
        table_html += _row("Debt/Equity",   _fmt_de(de_a), _fmt_de(de_b),
                           _winner(de_a, de_b, False))  # lower D/E = better

        table_html += "</div>"
        st.markdown(table_html, unsafe_allow_html=True)

        # ── RADAR / SPIDER CHART ──────────────────────────────────────────────
        radar_categories = ["Valuation", "Profitability", "Growth", "Balance Sheet", "Efficiency"]

        def _radar_scores(pe, roe, pm, rev_cagr, profit_cagr, de, sector, industry, info_dict=None, bs_df=None):
            """Return 5 scores (0-10) for radar axes.
            Axes: Valuation | Profitability | Growth | Balance Sheet | Efficiency

            The first four axes are now sourced from the same sector-aware
            compute_health_score() engine used in _score_stock(), so the
            radar shape reflects sector-specific scoring (e.g. a bank's
            "Profitability" axis reflects ROA/ROE within banking norms,
            not the same divisors used for an FMCG company). Falls back
            to the original generic formula if modules/ isn't loaded or
            sector scoring can't produce a result.

            Efficiency uses asset turnover (Revenue / Total Assets) — a
            genuine operational metric distinct from profit margin, and
            stays generic since it's not part of any sector config.
            """
            val_s = prof_s = grow_s = bs_s = None
            _radar_name = (info_dict or {}).get("longName", "")
            _radar_desc = (info_dict or {}).get("longBusinessSummary", "")
            if _MODULES_LOADED:
                try:
                    _pb = (info_dict or {}).get("priceToBook")
                    _extra = {
                        "fcf": (info_dict or {}).get("freeCashflow"),
                        "ocf": (info_dict or {}).get("operatingCashflow"),
                        "revenue": (info_dict or {}).get("totalRevenue"),
                        "roa": (info_dict or {}).get("returnOnAssets"),
                        "pb_ratio": _pb,
                        "ev_ebitda": (info_dict or {}).get("enterpriseToEbitda"),
                        "price_to_sales": (info_dict or {}).get("priceToSalesTrailing12Months"),
                    }
                    health = compute_health_score(
                        pe=pe, pb=_pb, roe_raw=roe, de_raw=de, profit_margin_raw=pm,
                        revenue_cagr=rev_cagr, profit_cagr=profit_cagr,
                        sector=sector, industry=industry,
                        name=_radar_name, description=_radar_desc,
                        extra_metrics=_extra,
                    )
                    sub = health.get("sub_scores", {})
                    val_s  = sub.get("Valuation")
                    prof_s = sub.get("Profitability")
                    grow_s = sub.get("Growth")
                    bs_s   = sub.get("Balance Sheet")
                except Exception:
                    pass

            # Valuation: high score = attractive price; neutral if PE negative/unknown
            if val_s is None:
                if pe is not None and pe > 0:
                    _radar_slug = classify_sector(sector or "", industry or "", _radar_name, _radar_desc)
                    low, high = get_pe_bands(sector or "", industry or "", slug=_radar_slug)
                    band = high - low if high != low else 1
                    val_s = max(0, min(10, 10 - ((pe - low) / band) * 10))
                else:
                    val_s = 5.0

            # Profitability: ROE + margin (calibrated divisors matching _score_stock)
            if prof_s is None:
                roe_s  = min(10, max(0, (roe * 100) / 4)) if roe is not None else 5.0
                pm_s   = min(10, max(0, (pm  * 100) / 3)) if pm  is not None else 5.0
                prof_s = (roe_s + pm_s) / 2

            # Growth
            if grow_s is None:
                rc_s   = min(10, max(0, (rev_cagr    / 3))) if rev_cagr    is not None else 5.0
                pc_s   = min(10, max(0, (profit_cagr / 3))) if profit_cagr is not None else 5.0
                grow_s = (rc_s + pc_s) / 2

            # Balance sheet
            if bs_s is None:
                if de is not None:
                    de_norm = de / 100
                    bs_s = max(0, min(10, 10 - de_norm * 2))
                else:
                    bs_s = 5.0

            # Efficiency: Asset Turnover = Revenue / Total Assets
            # High turnover (retail/FMCG ≈ 1.5–3x) → high score.
            # Asset-heavy (utilities/metals ≈ 0.3–0.7x) → lower score.
            # Divisor of 2.0 means turnover ≥ 2.0× → perfect 10.
            eff_s = 5.0  # default neutral
            try:
                _rev = (info_dict or {}).get("totalRevenue")
                _assets = None
                if bs_df is not None and not bs_df.empty:
                    for _ak in ["Total Assets", "TotalAssets"]:
                        if _ak in bs_df.index:
                            _a_series = bs_df.loc[_ak].dropna()
                            if len(_a_series):
                                _assets = float(_a_series.iloc[-1])
                            break
                if _rev and _assets and _assets > 0:
                    asset_turnover = float(_rev) / _assets
                    eff_s = min(10, max(0, asset_turnover / 2.0 * 10))
            except Exception:
                pass

            return [round(val_s, 1), round(prof_s, 1), round(grow_s, 1), round(bs_s, 1), round(eff_s, 1)]

        radar_a = _radar_scores(pe_a, roe_a, pm_a, rev_cagr_a, profit_cagr_a, de_a, sect_a, ind_a, info_a, bs_a)
        radar_b = _radar_scores(pe_b, roe_b, pm_b, rev_cagr_b, profit_cagr_b, de_b, sect_b, ind_b, info_b, bs_b)

        if go is not None:
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=radar_a + [radar_a[0]],
                theta=radar_categories + [radar_categories[0]],
                fill="toself",
                name=short_a,
                line=dict(color="#22C55E", width=2),
                fillcolor="rgba(34,197,94,0.12)",
                marker=dict(size=6, color="#22C55E"),
            ))
            fig.add_trace(go.Scatterpolar(
                r=radar_b + [radar_b[0]],
                theta=radar_categories + [radar_categories[0]],
                fill="toself",
                name=short_b,
                line=dict(color="#3B82F6", width=2),
                fillcolor="rgba(59,130,246,0.12)",
                marker=dict(size=6, color="#3B82F6"),
            ))
            fig.update_layout(
                polar=dict(
                    bgcolor="#F3F4F6",
                    radialaxis=dict(
                        visible=True, range=[0, 10],
                        tickfont=dict(size=10, color="#6B7280"),
                        gridcolor="#E2E4E9",
                        linecolor="#E2E4E9",
                    ),
                    angularaxis=dict(
                        tickfont=dict(size=12, color="#374151", family="Inter"),
                        gridcolor="#E2E4E9",
                        linecolor="#E2E4E9",
                    ),
                ),
                paper_bgcolor="#F5F6F8",
                plot_bgcolor="#F5F6F8",
                font=dict(family="Inter", color="#374151"),
                legend=dict(
                    font=dict(size=13, color="#374151"),
                    bgcolor="rgba(0,0,0,0)",
                    bordercolor="#E2E4E9",
                    borderwidth=1,
                    x=0.85, y=1.05,
                ),
                margin=dict(l=60, r=60, t=40, b=40),
                height=420,
            )

        st.markdown("<div class='section-card'><div class='section-title'>Radar Chart — Multidimensional Comparison</div>", unsafe_allow_html=True)
        if go is not None:
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": True, "displaylogo": False, "modeBarButtonsToRemove": ["lasso2d", "select2d"]})
            # Pillar score breakdown under chart
            pc1, pc2, pc3, pc4 = st.columns(4)
            pillar_labels = [("Valuation", "val_s"), ("Profitability", "prof_s"), ("Growth", "grow_s"), ("Balance Sheet", "bs_s")]
            pillar_keys   = ["valuation", "profitability", "growth", "balance_sheet"]
            for col, key in zip([pc1, pc2, pc3, pc4], pillar_keys):
                sa = pillars_a.get(key, 5.0)
                sb = pillars_b.get(key, 5.0)
                label = key.replace("_", " ").title()
                col.markdown(f"""
                <div style='background:#F3F4F6; border:1px solid #E2E4E9; border-radius:10px; padding:10px 12px; text-align:center;'>
                  <div style='font-size:11px; color:#5B6673; margin-bottom:6px; text-transform:uppercase; letter-spacing:0.5px;'>{label}</div>
                  <div style='display:flex; justify-content:center; gap:10px;'>
                    <span style='font-size:1.1rem; font-weight:700; color:#15803D;'>{sa}</span>
                    <span style='color:var(--ink-muted); font-size:0.9rem; padding-top:3px;'>vs</span>
                    <span style='font-size:1.1rem; font-weight:700; color:#2563EB;'>{sb}</span>
                  </div>
                  <div style='font-size:10px; color:var(--ink-muted); margin-top:3px;'>{short_a} · {short_b}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Radar chart requires plotly. Install with: pip install plotly")
        st.markdown("</div>", unsafe_allow_html=True)

        # ── AI VERDICT ────────────────────────────────────────────────────────
        st.markdown("<div class='section-card'><div class='section-title'>AI Verdict</div>", unsafe_allow_html=True)

        # Sector-aware context for each company — ensures the LLM frames
        # valuation/profitability commentary using the right lens per
        # company (e.g. P/B for a bank vs P/E for an IT company) rather
        # than applying one generic framework to both sides.
        sector_ctx_a = sector_ctx_b = ""
        cross_sector_note = ""
        if _MODULES_LOADED:
            try:
                sector_ctx_a = get_sector_prompt(sect_a, ind_a, name_a, info_a.get("longBusinessSummary", ""))
                sector_ctx_b = get_sector_prompt(sect_b, ind_b, name_b, info_b.get("longBusinessSummary", ""))
                slug_a = classify_sector(sect_a, ind_a, name_a, info_a.get("longBusinessSummary", ""))
                slug_b = classify_sector(sect_b, ind_b, name_b, info_b.get("longBusinessSummary", ""))
                if slug_a != slug_b:
                    cross_sector_note = (
                        f"\nNOTE: {short_a} and {short_b} operate in DIFFERENT sectors "
                        f"({slug_a.replace('_',' ').title()} vs {slug_b.replace('_',' ').title()}). "
                        "Flag that a direct head-to-head score comparison is less meaningful across "
                        "sectors and that sector-appropriate valuation lenses differ.\n"
                    )
            except Exception:
                pass

        compare_prompt = build_compare_prompt(
            name_a, pe_a, roe_a, de_a, pm_a, mcap_a, rev_a, rev_cagr_a, rev_cagr_n_a,
            profit_cagr_a, profit_cagr_n_a, score_a, sector_ctx_a,
            name_b, pe_b, roe_b, de_b, pm_b, mcap_b, rev_b, rev_cagr_b, rev_cagr_n_b,
            profit_cagr_b, profit_cagr_n_b, score_b, sector_ctx_b,
            cross_sector_note,
        )
        with st.spinner("Generating AI verdict…"):
            verdict = ask_llm(compare_prompt)
        st.markdown(f"<p style='font-size:16px; line-height:1.9; color:#374151;'>{verdict}</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='disclaimer'>⚠ EquiEye AI is for educational purposes only. Not financial advice.</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 3: ANNUAL REPORT SIMPLIFIER + PDF Q&A
# ─────────────────────────────────────────────────────────────────────────────
with tab_pdf:
    st.markdown("<h3 style='color:#111827; font-size:1.7rem; margin-bottom:0.5rem;'>Annual Report Simplifier</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color:#5B6673; font-size:13px;'>Upload an annual report PDF, get a plain-English breakdown, then ask follow-up questions about it.</p>", unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload Annual Report (PDF)", type=["pdf"])

    # Reset Q&A state when a new file is uploaded
    if uploaded_file:
        file_key = f"{uploaded_file.name}_{uploaded_file.size}"
        if st.session_state.get("pdf_file_key") != file_key:
            st.session_state["pdf_file_key"] = file_key
            st.session_state["pdf_extracted_text"] = None
            st.session_state["pdf_qa_history"] = []

        with st.spinner("Reading PDF..."):
            try:
                if st.session_state.get("pdf_extracted_text") is None:
                    pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
                    text = ""
                    for page in pdf_reader.pages[:20]:  # First 20 pages
                        text += page.extract_text() or ""
                    text = text[:12000]  # Increased token budget for Q&A use
                    st.session_state["pdf_extracted_text"] = text
                    st.session_state["pdf_num_pages"] = len(pdf_reader.pages)
                else:
                    text = st.session_state["pdf_extracted_text"]
            except Exception:
                st.error("Could not read PDF. Please try another file.")
                st.stop()

        # Guard: if text extraction yielded nothing (scanned/image-only PDF)
        MIN_TEXT_LENGTH = 200
        if len(text.strip()) < MIN_TEXT_LENGTH:
            st.error(
                f"⚠ Read {st.session_state.get('pdf_num_pages', '?')} pages but could not extract readable text. "
                "This is likely a scanned or image-only PDF — EquiEye can only "
                "analyse text-based PDFs. Try copying text from the PDF manually "
                "to verify, or use a text-based version of the annual report."
            )
            st.stop()

        num_pages = st.session_state.get("pdf_num_pages", "?")
        st.success(f"✓ Read {num_pages} pages ({len(text):,} characters extracted). Ready for analysis and questions.")

        # ── Initial 6-point summary ──────────────────────────────────────────
        # Trim to 6000 chars to stay well within Groq token limits
        pdf_text_for_summary = text[:6000] if _MODULES_LOADED else text[:8000]

        if "pdf_initial_summary" not in st.session_state or st.session_state.get("pdf_file_key") != file_key:
            pdf_prompt = build_pdf_summary_prompt(pdf_text_for_summary)

            with st.spinner("Analysing report..."):
                analysis = ask_llm(pdf_prompt, "You are a financial analyst. Be specific and concise. Under 400 words.")
            st.session_state["pdf_initial_summary"] = analysis

        st.markdown("<div class='section-card'><div class='section-title'>AI Analysis</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:16px; line-height:1.9; color:#374151;'>{sanitize_llm_html(st.session_state['pdf_initial_summary'])}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # ── PDF Q&A section ──────────────────────────────────────────────────
        st.markdown("<div class='section-card'><div class='section-title'>Ask Questions About This Report</div>", unsafe_allow_html=True)
        st.markdown("<p style='color:#5B6673; font-size:13px; margin-bottom:1rem;'>Ask follow-up questions about the specific report you uploaded.</p>", unsafe_allow_html=True)

        # Suggested follow-up questions
        pdf_suggestions = [
            "What did management say about margins?",
            "What are the key risks mentioned?",
            "What is the revenue growth trend?",
            "Any related-party transactions?",
            "What is the dividend policy?",
        ]
        sugg_cols = st.columns(len(pdf_suggestions))
        for i, ps in enumerate(pdf_suggestions):
            with sugg_cols[i]:
                if st.button(ps, key=f"pdf_sugg_{i}"):
                    st.session_state["pdf_pending_question"] = ps
                    st.rerun()

        # Initialize Q&A history
        if "pdf_qa_history" not in st.session_state:
            st.session_state["pdf_qa_history"] = []

        # Display Q&A history — both sides sanitized before HTML injection
        for msg in st.session_state["pdf_qa_history"]:
            if msg["role"] == "user":
                safe_content = _html.escape(msg["content"])
                st.markdown(f"<div class='chat-msg-user'>{safe_content}</div>", unsafe_allow_html=True)
            else:
                safe_ai = sanitize_llm_html(msg["content"])
                st.markdown(f"<div class='chat-msg-ai'>{safe_ai}</div>", unsafe_allow_html=True)

        # Q&A input form
        with st.form(key="pdf_qa_form", clear_on_submit=True):
            qa_col1, qa_col2 = st.columns([5, 1])
            with qa_col1:
                pdf_question = st.text_input("", placeholder="e.g. What did management say about margins?", key="pdf_q_input", label_visibility="collapsed")
            with qa_col2:
                pdf_ask_btn = st.form_submit_button("Ask →")

        # Handle pending question from suggestion buttons
        pending_pdf_q = st.session_state.pop("pdf_pending_question", None)
        active_pdf_q = pending_pdf_q or (pdf_question if pdf_ask_btn and pdf_question else None)

        if active_pdf_q:
            # Build conversation context using existing history BEFORE appending
            # the new question — this prevents an orphaned question entry in history
            # if ask_llm raises or returns an error sentinel.
            prior_history_str = "\n".join([
                f"{m['role'].upper()}: {m['content']}"
                for m in st.session_state["pdf_qa_history"][-6:]
            ])

            # Trim text for Q&A to save tokens — use first 5000 chars which
            # covers most key financial data in annual reports
            qa_text = text[:5000] if _MODULES_LOADED else text

            qa_prompt = build_pdf_qa_prompt(qa_text, prior_history_str, active_pdf_q)

            with st.spinner("Reading the report for your answer..."):
                pdf_answer = ask_llm(qa_prompt, "You are a financial analyst answering questions about a specific annual report. Only use information from the provided text.")

            # Only commit both messages to history once we have a valid answer
            st.session_state["pdf_qa_history"].append({"role": "user", "content": active_pdf_q})
            st.session_state["pdf_qa_history"].append({"role": "assistant", "content": pdf_answer})
            st.rerun()

        if st.session_state.get("pdf_qa_history"):
            if st.button("Clear Q&A history", key="clear_pdf_qa"):
                st.session_state["pdf_qa_history"] = []
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div class='disclaimer'>⚠ AI summaries may miss nuance. Always read source documents for investment decisions.</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 4: ASK EQUIEYE
# ─────────────────────────────────────────────────────────────────────────────
with tab_chat:
    st.markdown("<h3 style='color:#111827; font-size:1.7rem; margin-bottom:0.5rem;'>Ask EquiEye</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color:#5B6673; font-size:13px;'>Ask anything about Indian stocks, markets, or financial concepts.</p>", unsafe_allow_html=True)

    # Suggested questions
    st.markdown("<div style='display:flex; gap:8px; flex-wrap:wrap; margin-bottom:1rem;'>", unsafe_allow_html=True)
    suggestions = [
        "Why did Paytm fall?",
        "How does Zomato make money?",
        "What is P/E ratio?",
        "What are the risks in Tata Motors?",
        "Is HDFC Bank safe to invest in?",
    ]
    for s in suggestions:
        if st.button(s, key=f"sugg_{s}"):
            # Directly trigger the question instead of just pre-filling the box
            st.session_state["chat_pending_question"] = s
            st.rerun()

    # Chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display history — both user and AI content are sanitized before injection.
    # sanitize_llm_html escapes <, >, & and converts newlines to <br> so
    # multi-sentence AI responses still render readably.
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            safe_content = _html.escape(msg["content"])
            st.markdown(f"<div class='chat-msg-user'>{safe_content}</div>", unsafe_allow_html=True)
        else:
            safe_ai = sanitize_llm_html(msg["content"])
            st.markdown(f"<div class='chat-msg-ai'>{safe_ai}</div>", unsafe_allow_html=True)

    # Input
    with st.form(key="chat_form", clear_on_submit=True):
        chat_col1, chat_col2 = st.columns([5, 1])
        with chat_col1:
            user_q = st.text_input("", placeholder="Ask about any stock, concept, or market event...", key="chat_q", label_visibility="collapsed")
        with chat_col2:
            send_btn = st.form_submit_button("Send →")

    # Handle pending question from suggestion buttons (fires outside the form)
    pending_q = st.session_state.pop("chat_pending_question", None)
    active_q = pending_q or (user_q if send_btn and user_q else None)

    if active_q:
        st.session_state.chat_history.append({"role": "user", "content": active_q})

        history_str = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.chat_history[-6:]])

        # Try to ground the answer in real live data for any companies mentioned
        live_data_blocks = []
        ambiguous_notice = None
        matches = detect_companies_in_question(active_q)

        for match in matches:
            if match[0] == "AMBIGUOUS":
                ambiguous_notice = match[1]
                continue
            sym, company_name = match
            try:
                with st.spinner(f"Pulling live data for {company_name}..."):
                    info = fetch_quote(sym)
                if info.get("currentPrice") or info.get("regularMarketPrice"):
                    price = info.get("currentPrice") or info.get("regularMarketPrice")
                    prev_close = info.get("previousClose")
                    chg = pct(price, prev_close)
                    chg_str = f"{chg:.2f}%" if chg is not None else "N/A"
                    _pe   = info.get('trailingPE')
                    _roe  = info.get('returnOnEquity')
                    _pm   = info.get('profitMargins')
                    _de   = info.get('debtToEquity')
                    _sector = info.get('sector', '')
                    _industry = info.get('industry', '')

                    # Sector-specific framing so the LLM applies the right
                    # analytical lens (e.g. don't reach for P/E on a bank,
                    # don't apply NPA scrutiny to an IT services company).
                    _sector_ctx = ""
                    if _MODULES_LOADED:
                        try:
                            _sector_ctx = get_sector_prompt(_sector, _industry, info.get("longName", ""), info.get("longBusinessSummary", ""))
                        except Exception:
                            pass

                    live_data_blocks.append(f"""
                    LIVE DATA for {company_name} ({sym}) — use this real data, do not contradict it:
                    Current price: ₹{price:,.1f}, Change: {chg_str}
                    Market Cap: {fmt_crore(info.get('marketCap'))}
                    P/E: {f"{_pe:.1f}x" if _pe is not None else "N/A"}
                    ROE: {f"{_roe*100:.1f}%" if _roe is not None else "N/A"}
                    Profit Margin: {f"{_pm*100:.2f}%" if _pm is not None else "N/A"}
                    Debt/Equity: {f"{_de/100:.2f}x" if _de is not None else "N/A"}
                    Sector: {_sector or 'N/A'}
                    {_sector_ctx}
                    """)
            except Exception:
                pass  # fall through to general knowledge if live fetch fails for this one

        if ambiguous_notice and not live_data_blocks:
            options_str = ", ".join(str(n) for n in ambiguous_notice if n)
            clarify_msg = f"That name matches multiple listed companies: {options_str}. Could you specify which one you mean (or use the exact ticker)?"
            st.session_state.chat_history.append({"role": "assistant", "content": clarify_msg})
            st.rerun()

        live_data_context = "\n".join(live_data_blocks)

        chat_prompt = build_chat_prompt(live_data_context, history_str)

        with st.spinner("Thinking..."):
            response = ask_llm(chat_prompt, model="openai/gpt-oss-20b")

        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.rerun()

    if st.button("Clear chat", key="clear_chat"):
        st.session_state.chat_history = []
        st.rerun()

    st.markdown("<div class='disclaimer'>⚠ EquiEye AI is for educational purposes only. Not financial advice.</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 5: WATCHLIST
# ─────────────────────────────────────────────────────────────────────────────
with tab_watchlist:
    st.markdown("<h3 style='color:#111827; font-size:1.7rem; margin-bottom:0.2rem;'>⭐ My Watchlist</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color:#5B6673; font-size:13px; margin-bottom:1rem;'>Track stocks you care about. Live prices refresh each visit. Saved for this session.</p>", unsafe_allow_html=True)

    # Initialize watchlist in session state
    if "watchlist" not in st.session_state:
        st.session_state.watchlist = []  # list of (symbol, display_name) tuples

    # ── Add stock to watchlist ──────────────────────────────────────────────
    st.markdown("<div class='section-card'><div class='section-title'>Add Stock</div>", unsafe_allow_html=True)
    with st.form(key="watchlist_add_form", clear_on_submit=True):
        wl_col1, wl_col2 = st.columns([4, 1])
        with wl_col1:
            wl_input = st.text_input("", placeholder="Enter company name or ticker (e.g. Infosys, HDFCBANK)", label_visibility="collapsed", key="wl_search_input")
        with wl_col2:
            wl_add_btn = st.form_submit_button("Add →")

    if wl_add_btn and wl_input:
        with st.spinner(f"Searching for '{wl_input}'..."):
            wl_matches = search_nse_matches(wl_input)
        if not wl_matches:
            st.error(f"No NSE-listed company found matching '{wl_input}'.")
        elif len(wl_matches) == 1:
            sym, lname = wl_matches[0]
            already = any(s == sym for s, _ in st.session_state.watchlist)
            if already:
                st.info(f"{lname} ({sym}) is already in your watchlist.")
            else:
                st.session_state.watchlist.append((sym, lname))
                st.success(f"Added {lname} ({sym}) to watchlist!")
                st.rerun()
        else:
            st.session_state["wl_pending_matches"] = wl_matches
            st.session_state["wl_pending_query"] = wl_input

    # Show picker if multiple matches
    if st.session_state.get("wl_pending_matches"):
        pending = st.session_state["wl_pending_matches"]
        query = st.session_state.get("wl_pending_query", "your query")
        st.markdown(f"<p style='color:#5B6673; font-size:13px;'>Found {len(pending)} matches for '{query}' — which one?</p>", unsafe_allow_html=True)
        pick_cols = st.columns(min(3, len(pending)))
        for i, (sym, lname) in enumerate(pending[:6]):
            with pick_cols[i % 3]:
                btn_label = f"{lname}\n({sym})"
                if st.button(btn_label, key=f"wl_pick_{i}_{sym}"):
                    already = any(s == sym for s, _ in st.session_state.watchlist)
                    if not already:
                        st.session_state.watchlist.append((sym, lname))
                    st.session_state.pop("wl_pending_matches", None)
                    st.session_state.pop("wl_pending_query", None)
                    st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Quick-add popular stocks ────────────────────────────────────────────
    st.markdown("<p style='color:#5B6673; font-size:12px; margin-bottom:6px;'>Quick add:</p>", unsafe_allow_html=True)
    popular = [
        ("RELIANCE.NS", "Reliance Industries"),
        ("HDFCBANK.NS", "HDFC Bank"),
        ("INFY.NS", "Infosys"),
        ("TCS.NS", "TCS"),
        ("ETERNAL.NS", "Zomato / Eternal"),
    ]
    pop_cols = st.columns(len(popular))
    for i, (sym, lname) in enumerate(popular):
        with pop_cols[i]:
            already = any(s == sym for s, _ in st.session_state.watchlist)
            btn_label = f"✓ {lname.split()[0]}" if already else lname.split()[0]
            if st.button(btn_label, key=f"pop_{sym}", disabled=already):
                st.session_state.watchlist.append((sym, lname))
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Watchlist table ─────────────────────────────────────────────────────
    if not st.session_state.watchlist:
        st.markdown("""
        <div style='background:#F7F8FA; border:1px dashed #E2E4E9; border-radius:14px;
                    padding:2.5rem; text-align:center; color:#5B6673;'>
            <div style='font-size:2rem; margin-bottom:0.5rem;'>⭐</div>
            <div style='font-size:15px; font-weight:500; color:#374151; margin-bottom:6px;'>Your watchlist is empty</div>
            <div style='font-size:13px;'>Search for stocks above or quick-add from the popular list</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("<div class='section-card'><div class='section-title'>Your Stocks</div>", unsafe_allow_html=True)

        # Header row — wrapped in the SAME st.columns([6, 1]) split as the data
        # rows below, so the info-grid's column boundaries (Company/Price/
        # Change/Mkt Cap/P/E) line up exactly with each row's cells instead of
        # spanning the full card width while data rows are squeezed to 6/7 of
        # it to make room for the remove button.
        hdr_info_col, hdr_btn_col = st.columns([6, 1])
        with hdr_info_col:
            st.markdown(
                "<div class='wl-row wl-header'>"
                "<div class='wl-cell'>Company</div>"
                "<div class='wl-cell'>Price</div>"
                "<div class='wl-cell'>Change</div>"
                "<div class='wl-cell'>Mkt Cap</div>"
                "<div class='wl-cell'>P/E</div>"
                "</div>",
                unsafe_allow_html=True
            )
        with hdr_btn_col:
            st.markdown("<div class='wl-row wl-header'>&nbsp;</div>", unsafe_allow_html=True)

        to_remove = None
        for idx, (sym, lname) in enumerate(st.session_state.watchlist):
            # Use the module-level cached fetch_stock (TTL=300s) so that repeated
            # Streamlit reruns (button clicks, sidebar interactions) don't fire a
            # fresh Yahoo Finance request for every watchlist item every time.
            try:
                wl_full = fetch_quote(sym)
                wl_price = wl_full.get("currentPrice") or wl_full.get("regularMarketPrice")
                wl_prev  = wl_full.get("previousClose")
                wl_mcap  = wl_full.get("marketCap")
                wl_pe    = wl_full.get("trailingPE")
                wl_chg   = pct(wl_price, wl_prev)
            except Exception:
                wl_price = wl_prev = wl_mcap = wl_pe = wl_chg = None

            chg_color = "#22C55E" if wl_chg and wl_chg > 0 else "#EF4444" if wl_chg and wl_chg < 0 else "#6B7280"
            chg_str   = f"{wl_chg:+.2f}%" if wl_chg is not None else "—"
            price_str = f"₹{wl_price:,.1f}" if wl_price else "—"
            mcap_str  = fmt_crore(wl_mcap)
            pe_str    = f"{wl_pe:.1f}x" if wl_pe is not None else "—"
            short_name = lname[:28] + "…" if len(lname) > 28 else lname

            # Data cells as one HTML grid row (stays intact on mobile); the
            # remove button is the only real Streamlit widget, in its own
            # slim column so at worst it drops to its own line below the row.
            row_info_col, row_btn_col = st.columns([6, 1])
            with row_info_col:
                st.markdown(
                    f"<div class='wl-row'>"
                    f"<div class='wl-cell'><div style='font-weight:500; color:#111827;'>{short_name}</div>"
                    f"<div style='font-size:11px; color:#5B6673;'>{sym}</div></div>"
                    f"<div class='wl-cell' style='color:#111827;'>{price_str}</div>"
                    f"<div class='wl-cell' style='color:{chg_color};'>{chg_str}</div>"
                    f"<div class='wl-cell'>{mcap_str}</div>"
                    f"<div class='wl-cell'>{pe_str}</div>"
                    f"</div>",
                    unsafe_allow_html=True
                )
            with row_btn_col:
                if st.button("✕", key=f"wl_rm_{idx}_{sym}", help=f"Remove {lname}", use_container_width=True):
                    to_remove = idx

            st.markdown("<hr style='border:none; border-top:1px solid #E2E4E9; margin:4px 0;'>", unsafe_allow_html=True)

        if to_remove is not None:
            st.session_state.watchlist.pop(to_remove)
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

        # Action buttons
        act_col1, act_col2, _ = st.columns([1.5, 1.5, 5])
        with act_col1:
            if st.button("🔄 Refresh prices", key="wl_refresh"):
                st.rerun()
        with act_col2:
            if st.button("🗑 Clear watchlist", key="wl_clear"):
                st.session_state.watchlist = []
                st.rerun()

        st.markdown(
            "<div style='font-size:11px; color:var(--ink-muted); margin-top:0.5rem;'>"
            "💡 Tip: Click any stock in Stock Research and it'll be ready to add here. "
            "Watchlist is saved for this browser session.</div>",
            unsafe_allow_html=True
        )

    st.markdown("<div class='disclaimer'>⚠ EquiEye AI is for educational purposes only. Not financial advice.</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 6: PORTFOLIO TRACKER
# ─────────────────────────────────────────────────────────────────────────────
with tab_portfolio:
    st.markdown("<h3 style='color:#111827; font-size:1.7rem; margin-bottom:0.2rem;'>💼 Portfolio Tracker</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color:#5B6673; font-size:13px; margin-bottom:1rem;'>Track your holdings, P&L, and sector exposure. Data stays in your session.</p>", unsafe_allow_html=True)

    if _MODULES_LOADED:
        init_portfolio()
        holdings = get_holdings()

        # ── Add holding form ──────────────────────────────────────────────────
        st.markdown("<div class='section-card'><div class='section-title'>Add Holding</div>", unsafe_allow_html=True)

        # Using plain widgets (no st.form) so buy price persists across reruns.
        # st.form with clear_on_submit=True destroys widget session-state keys
        # before the sync block can read them, causing the price to reset to
        # the default value (100.0) every time the user clicks Add.
        #
        # Fields are cleared here, BEFORE the widgets below are instantiated.
        # Writing to st.session_state[<widget_key>] AFTER a widget with that
        # key has already been created raises StreamlitAPIException, so the
        # clear must happen on the *next* rerun, before widget creation —
        # not inline right after the Add button is clicked.
        if st.session_state.get("_pt_clear_pending"):
            st.session_state["pt_stock_input"] = ""
            st.session_state["pt_qty_input"] = 1
            st.session_state["pt_price_input"] = 100.0
            st.session_state["_pt_clear_pending"] = False

        pc1, pc2, pc3, pc4 = st.columns([3, 1.2, 1.5, 1])
        with pc1:
            pt_input = st.text_input(
                "", placeholder="Company name or ticker (e.g. Infosys, TCS)",
                label_visibility="collapsed", key="pt_stock_input"
            )
        with pc2:
            pt_qty = st.number_input(
                "Qty", min_value=1, value=1, step=1,
                label_visibility="visible", key="pt_qty_input"
            )
        with pc3:
            pt_price = st.number_input(
                "Buy Price (₹)", min_value=0.01, value=100.0, step=0.5,
                label_visibility="visible", key="pt_price_input"
            )
        with pc4:
            st.markdown("<br>", unsafe_allow_html=True)
            pt_add_btn = st.button("Add →", key="pt_add_btn")

        if pt_add_btn and pt_input:
            with st.spinner(f"Searching '{pt_input}'..."):
                pt_matches = search_nse_matches(pt_input)
            if not pt_matches:
                st.error(f"No NSE company found for '{pt_input}'.")
            elif len(pt_matches) == 1:
                sym, lname = pt_matches[0]
                try:
                    pt_info = fetch_quote(sym)
                    pt_sector = pt_info.get("sector", "Unknown")
                except Exception:
                    pt_sector = "Unknown"
                add_holding(sym, lname, float(pt_qty), float(pt_price), pt_sector)
                st.success(f"Added {lname} ({sym}) — {int(pt_qty)} shares @ ₹{pt_price:,.1f}")
                # Defer the field clear to the top of the next rerun (see
                # _pt_clear_pending check above) — can't touch these
                # session_state keys directly here, the widgets already exist.
                st.session_state["_pt_clear_pending"] = True
                st.rerun()
            else:
                st.session_state["pt_pending_matches"] = pt_matches
                st.session_state["pt_pending_qty"] = pt_qty
                st.session_state["pt_pending_price"] = pt_price

        # Disambiguation picker
        if st.session_state.get("pt_pending_matches"):
            pending_pt = st.session_state["pt_pending_matches"]
            pt_pick_cols = st.columns(min(3, len(pending_pt)))
            for i, (sym, lname) in enumerate(pending_pt[:6]):
                with pt_pick_cols[i % 3]:
                    if st.button(f"{lname}\n({sym})", key=f"pt_pick_{i}_{sym}"):
                        try:
                            pt_inf = fetch_quote(sym)
                            sec = pt_inf.get("sector", "Unknown")
                        except Exception:
                            sec = "Unknown"
                        qty_v = st.session_state.get("pt_pending_qty", 1)
                        price_v = st.session_state.get("pt_pending_price", 100.0)
                        add_holding(sym, lname, float(qty_v), float(price_v), sec)
                        st.session_state.pop("pt_pending_matches", None)
                        st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

        holdings = get_holdings()
        if not holdings:
            st.markdown("""
            <div style='background:#F7F8FA; border:1px dashed #E2E4E9; border-radius:14px;
                        padding:2.5rem; text-align:center; color:#5B6673;'>
                <div style='font-size:2rem; margin-bottom:0.5rem;'>💼</div>
                <div style='font-size:15px; font-weight:500; color:#374151; margin-bottom:6px;'>Your portfolio is empty</div>
                <div style='font-size:13px;'>Add holdings above to track your P&L</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Fetch live prices
            live_prices = {}
            with st.spinner("Fetching live prices..."):
                for h in holdings:
                    try:
                        _h_info = fetch_quote(h["ticker"])
                        _lp = _h_info.get("currentPrice") or _h_info.get("regularMarketPrice")
                        if _lp is not None:
                            live_prices[h["ticker"]] = float(_lp)
                    except Exception:
                        pass

            stats = compute_portfolio_stats(holdings, live_prices)

            # ── Summary strip ─────────────────────────────────────────────────
            total_pnl_color = "#22C55E" if stats["total_pnl"] >= 0 else "#EF4444"
            pnl_sign = "+" if stats["total_pnl"] >= 0 else ""
            # Built as one HTML string inside a CSS grid (.metric-strip) rather
            # than st.columns(4) — same fix as the hero metric strip above:
            # Streamlit's columns auto-stack to a single full-width column
            # below ~640px with no guaranteed gap, which made these four
            # cards run into each other on phone.
            _portfolio_metrics_html = "".join([
                mcard_html("Invested", f"₹{stats['total_invested']:,.0f}"),
                mcard_html("Current Value", f"₹{stats['current_value']:,.0f}"),
                mcard_html("Total P&L", f"{pnl_sign}₹{stats['total_pnl']:,.0f}", val_color=total_pnl_color),
                mcard_html("Return", f"{pnl_sign}{stats['total_pnl_pct']:.2f}%", val_color=total_pnl_color),
            ])
            st.markdown(f"<div class='metric-strip'>{_portfolio_metrics_html}</div>", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # ── Holdings table ────────────────────────────────────────────────
            st.markdown("<div class='section-card'><div class='section-title'>Holdings</div>", unsafe_allow_html=True)
            # Header row — wrapped in the SAME st.columns([5, 1, 1]) split as
            # the data rows below, so the info-grid's column boundaries
            # (Company/Qty/Buy Price/Current/P&L) line up exactly with each
            # row's cells instead of spanning the full card width while data
            # rows are squeezed to 5/7 of it to make room for the edit/delete
            # buttons.
            hdr_info_col, hdr_edit_col, hdr_del_col = st.columns([5, 1, 1])
            with hdr_info_col:
                st.markdown(
                    "<div class='pt-row pt-header'>"
                    "<div class='pt-cell'>Company</div>"
                    "<div class='pt-cell'>Qty</div>"
                    "<div class='pt-cell'>Buy Price</div>"
                    "<div class='pt-cell'>Current</div>"
                    "<div class='pt-cell'>P&amp;L</div>"
                    "</div>",
                    unsafe_allow_html=True
                )
            with hdr_edit_col:
                st.markdown("<div class='pt-row pt-header'>&nbsp;</div>", unsafe_allow_html=True)
            with hdr_del_col:
                st.markdown("<div class='pt-row pt-header'>&nbsp;</div>", unsafe_allow_html=True)

            # Track which holding is in edit mode
            if "pt_edit_ticker" not in st.session_state:
                st.session_state.pt_edit_ticker = None

            to_remove_pt = None
            for idx, h in enumerate(stats["holdings_with_stats"]):
                pnl_c = "#22C55E" if h["pnl"] >= 0 else "#EF4444"
                pnl_s = f"{'+' if h['pnl']>=0 else ''}₹{h['pnl']:,.0f} ({h['pnl_pct']:+.1f}%)"
                cur_str = f"₹{h['current_price']:,.1f}" if h["current_price"] else "—"
                ticker_key = h["ticker"]
                is_editing = (st.session_state.pt_edit_ticker == ticker_key)

                # Data cells as one HTML grid row (stays intact on mobile);
                # edit/delete stay as real Streamlit widgets in their own
                # slim columns — worst case on mobile they drop below the
                # row, each still clearly labeled and tappable.
                info_col, edit_col, del_col = st.columns([5, 1, 1])
                with info_col:
                    st.markdown(
                        f"<div class='pt-row'>"
                        f"<div class='pt-cell'><div style='font-weight:500; color:#111827;'>{h['name'][:22]}</div>"
                        f"<div style='font-size:11px; color:#5B6673;'>{ticker_key}</div></div>"
                        f"<div class='pt-cell'>{int(h['qty'])}</div>"
                        f"<div class='pt-cell'>₹{h['buy_price']:,.1f}</div>"
                        f"<div class='pt-cell'>{cur_str}</div>"
                        f"<div class='pt-cell' style='color:{pnl_c};'>{pnl_s}</div>"
                        f"</div>",
                        unsafe_allow_html=True
                    )

                # Edit toggle button
                edit_label = "✏️" if not is_editing else "✕"
                edit_help  = "Edit qty / buy price" if not is_editing else "Cancel edit"
                with edit_col:
                    if st.button(edit_label, key=f"pt_edit_btn_{idx}_{ticker_key}", help=edit_help, use_container_width=True):
                        st.session_state.pt_edit_ticker = None if is_editing else ticker_key
                        st.rerun()

                # Remove button
                with del_col:
                    if st.button("🗑", key=f"pt_rm_{idx}_{ticker_key}", help="Remove holding", use_container_width=True):
                        to_remove_pt = ticker_key

                # ── Inline edit form (shown only for the active row) ──────────
                if is_editing:
                    with st.form(key=f"pt_edit_form_{ticker_key}", clear_on_submit=False):
                        ef1, ef2, ef3 = st.columns([1.5, 1.5, 1])
                        with ef1:
                            new_qty = st.number_input(
                                "New Qty", min_value=1, value=int(h["qty"]), step=1,
                                key=f"edit_qty_{ticker_key}"
                            )
                        with ef2:
                            new_price = st.number_input(
                                "New Buy Price (₹)", min_value=0.01,
                                value=float(h["buy_price"]), step=0.5,
                                key=f"edit_price_{ticker_key}"
                            )
                        with ef3:
                            st.markdown("<br>", unsafe_allow_html=True)
                            save_btn = st.form_submit_button("Save ✓")
                        if save_btn:
                            update_holding(ticker_key, float(new_qty), float(new_price))
                            st.session_state.pt_edit_ticker = None
                            st.rerun()

                st.markdown("<hr style='border:none; border-top:1px solid #E2E4E9; margin:4px 0;'>", unsafe_allow_html=True)

            if to_remove_pt:
                remove_holding(to_remove_pt)
                if st.session_state.pt_edit_ticker == to_remove_pt:
                    st.session_state.pt_edit_ticker = None
                st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

            # ── Sector allocation ─────────────────────────────────────────────
            if stats["sector_allocation"]:
                st.markdown("<div class='section-card'><div class='section-title'>Sector Exposure</div>", unsafe_allow_html=True)
                sec_cols = st.columns(min(4, len(stats["sector_allocation"])))
                for i, (sec, pct_val) in enumerate(sorted(stats["sector_allocation"].items(), key=lambda x: -x[1])):
                    with sec_cols[i % len(sec_cols)]:
                        bar_color = "#22C55E" if pct_val >= 30 else "#F59E0B" if pct_val >= 15 else "#3B82F6"
                        st.markdown(f"""
                        <div style='background:#F3F4F6; border:1px solid #E2E4E9; border-radius:10px; padding:10px 12px; margin-bottom:10px;'>
                          <div style='font-size:13px; font-weight:600; color:#111827; margin-bottom:4px;'>{sec}</div>
                          <div style='font-size:1.2rem; font-weight:700; color:{bar_color};'>{pct_val}%</div>
                          <div style='background:#E2E4E9; border-radius:4px; height:4px; margin-top:6px;'>
                            <div style='background:{bar_color}; width:{min(pct_val,100):.0f}%; height:4px; border-radius:4px;'></div>
                          </div>
                        </div>
                        """, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            # Refresh / Clear
            act_c1, act_c2, _ = st.columns([1.5, 1.5, 5])
            with act_c1:
                if st.button("🔄 Refresh", key="pt_refresh"):
                    st.rerun()
            with act_c2:
                if st.button("🗑 Clear All", key="pt_clear"):
                    # Clear via the module's remove_holding so session state
                    # stays consistent — setting an arbitrary key like
                    # 'portfolio_holdings' would not affect the key the
                    # portfolio module actually reads from.
                    for _h in list(get_holdings()):
                        remove_holding(_h["ticker"])
                    st.rerun()
    else:
        st.info("Portfolio tracker requires the modules directory. Ensure modules/ is present.")

    st.markdown("<div class='disclaimer'>⚠ EquiEye AI is for educational purposes only. Not financial advice.</div>", unsafe_allow_html=True)
