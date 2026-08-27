# services/derived_metrics.py
"""
Balance-sheet / income-statement metrics derived from the statement
DataFrames rather than read straight off yfinance's `info` dict.

Extracted verbatim from the inline block in app.py's Stock Research tab.
These feed sector red-flag rules (metals_mining and telecom's
net_debt_ebitda, renewable_energy's interest_coverage) and scoring buckets
that would otherwise always report "missing_data" — yfinance doesn't
expose them directly, but they're derivable from the same bs/fin frames
already loaded for the CAGR calculation.

Best-effort throughout: line-item naming varies by ticker and statement
vintage, so any missing item leaves its metric as None rather than
raising. A partial metrics dict is fine — the scoring engine already
treats None as "no data" and reweights around it.
"""

from __future__ import annotations

from services.financial_utils import is_quarterly_financials


def latest_stmt_value(df, candidate_keys):
    """Most recent non-null value for the first matching row key."""
    if df is None or df.empty:
        return None
    for key in candidate_keys:
        if key in df.index:
            series = df.loc[key].dropna().sort_index()
            if len(series) >= 1:
                return series.iloc[-1]
    return None


def compute_derived_metrics(info: dict, fin, bs) -> dict:
    """
    Returns a dict with keys: net_debt_ebitda, interest_coverage,
    receivable_days, inventory_months, total_debt, cash, ebitda.

    `fin` may be quarterly rather than annual (yfinance's financials call
    falls back to quarterly_financials for some tickers). Flow metrics are
    annualized x4 in that case; stock metrics (a balance-sheet snapshot)
    are point-in-time and must NOT be scaled.
    """
    out = {
        "net_debt_ebitda": None,
        "interest_coverage": None,
        "receivable_days": None,
        "inventory_months": None,
        "total_debt": None,
        "cash": None,
        "ebitda": None,
    }
    try:
        annualize = 4 if is_quarterly_financials(fin) else 1

        total_debt = latest_stmt_value(bs, ["Total Debt"])
        cash = latest_stmt_value(bs, [
            "Cash And Cash Equivalents",
            "Cash Cash Equivalents And Short Term Investments",
            "Cash",
        ])
        ebitda = info.get("ebitda")
        out["total_debt"], out["cash"], out["ebitda"] = total_debt, cash, ebitda

        if total_debt is not None and ebitda:
            out["net_debt_ebitda"] = (total_debt - (cash or 0)) / ebitda

        ebit = latest_stmt_value(fin, ["EBIT", "Operating Income"])
        interest_exp = latest_stmt_value(fin, [
            "Interest Expense", "Interest Expense Non Operating",
        ])
        if ebit is not None and interest_exp:
            out["interest_coverage"] = ebit / abs(interest_exp)

        receivables = latest_stmt_value(bs, [
            "Receivables", "Accounts Receivable", "Net Receivables",
        ])
        revenue_latest = latest_stmt_value(fin, [
            "Total Revenue", "Revenue", "Total Revenues",
        ])
        if revenue_latest is not None:
            revenue_latest *= annualize
        else:
            # info["totalRevenue"] is already TTM/annual — no annualization.
            revenue_latest = info.get("totalRevenue")
        if receivables is not None and revenue_latest:
            out["receivable_days"] = (receivables / revenue_latest) * 365

        inventory = latest_stmt_value(bs, ["Inventory"])
        cogs = latest_stmt_value(fin, ["Cost Of Revenue", "Reconciled Cost Of Revenue"])
        if cogs is not None:
            cogs *= annualize
        if inventory is not None and cogs:
            out["inventory_months"] = (inventory / cogs) * 12
    except Exception:
        pass
    return out


def compute_ev_ebitda(info: dict, mkt_cap, total_debt, cash, ebitda):
    """EV/EBITDA, falling back to a manual computation when yfinance's
    `enterpriseToEbitda` is absent.

    That field comes back None for a number of NSE large caps (RELIANCE.NS
    among them). When it does, the conglomerate blended-band check in the
    valuation scorer never fires — even though it exists precisely for
    companies like Reliance — and valuation silently falls back to a
    generic single-sector P/E band, judging Jio/Retail/Media segments
    against a pure oil & gas bar.
    """
    direct = info.get("enterpriseToEbitda")
    if direct is not None:
        return direct
    if mkt_cap is not None and total_debt is not None and ebitda:
        ev = mkt_cap + total_debt - (cash or 0)
        if ev > 0:
            return round(ev / ebitda, 2)
    return None
