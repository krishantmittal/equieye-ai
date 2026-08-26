# EquiEye AI — Sector Intelligence System

This replaces the old generic-metrics-for-everyone approach with a
modular, sector-aware engine. Drop this `modules/` folder into your
project root (it preserves the exact public function signatures your
`app.py` already calls — `classify_sector`, `get_sector_prompt`,
`compute_health_score`, `get_pe_bands`, `detect_flags`,
`get_moat_analysis`, `compute_risk` — so **no changes to app.py are
required**).

## Architecture

```
modules/
├── sector_analysis.py     # classify_sector() / get_sector_prompt()
├── health_score.py         # compute_health_score() / get_pe_bands()
├── red_flags.py             # detect_flags()
├── moat_analysis.py         # get_moat_analysis()
├── risk_meter.py            # compute_risk()
└── sectors/
    ├── __init__.py          # SECTOR_REGISTRY — the master list
    ├── detector.py           # keyword-based sector classification
    ├── engine.py              # shared scoring/red-flag rule evaluator
    ├── banking.py             # one config file per sector...
    ├── fintech.py
    ├── auto_ev.py
    ├── renewable_energy.py
    ├── it_services.py
    ├── pharma.py
    ├── fmcg.py
    ├── insurance.py
    ├── nbfc.py
    ├── telecom.py
    ├── metals_mining.py
    ├── real_estate.py
    ├── power_utilities.py
    └── generic.py            # fallback when nothing matches
```

### How a request flows

1. `app.py` calls `classify_sector(sector, industry)` with yfinance's
   broad `sector`/`industry` strings (e.g. `"Financial Services"` /
   `"Banks - Regional"`).
2. `modules/sectors/detector.py` keyword-matches that text (plus
   company name/description when available) against every sector
   module's trigger words and returns a fine-grained internal slug
   (e.g. `"banking"`), falling back to `"generic"` if nothing matches.
3. `compute_health_score`, `detect_flags`, `get_moat_analysis`, and
   `compute_risk` all classify the company the same way, then pull
   that sector's `scoring_rules` / `red_flags` / `moat_factors` /
   `risk_factors` and run them through the shared rule engine in
   `modules/sectors/engine.py`.
4. Results are folded back into the **exact return shapes app.py
   already expects** (0-10 health score with `sub_scores`, a 1-4 risk
   `level`, a `"Weak"/"Moderate"/"Strong"` moat `rating`, etc.) so the
   existing UI renders unchanged.

## Adding a new sector — no core logic changes required

1. Create `modules/sectors/<your_sector>.py` modeled on any existing
   module (e.g. copy `fmcg.py`). It must export a single dict,
   `SECTOR_CONFIG`, with these keys:
   - `slug`, `display_name`
   - `key_metrics` — list of metric definitions
   - `scoring_rules` — list of `{"metric", "op", "threshold", "points", "max"}`
   - `risk_factors` — list of strings
   - `moat_factors` — list of `{"factor", "description"}`
   - `bull_case` / `bear_case` — lists of strings
   - `red_flags` — list of `{"condition": "metric_id OP threshold", "severity", "message"}`
   - `valuation` — `{"primary": [...], "secondary": [...], "notes": str, "bands": {...}}`
   - `llm_context` — a paragraph telling the LLM how to frame this sector

2. Register it in `modules/sectors/__init__.py`:
   ```python
   from .your_sector import SECTOR_CONFIG as YOUR_SECTOR
   SECTOR_REGISTRY["your_sector"] = YOUR_SECTOR
   ```

3. Add detection keywords for it in `modules/sectors/detector.py`'s
   `_RULES` list.

That's it — `health_score.py`, `red_flags.py`, `moat_analysis.py`, and
`risk_meter.py` never need to be touched. They're generic engines that
read whatever `scoring_rules`/`red_flags`/`moat_factors` the matched
sector config declares.

## Supplying sector-specific metrics yfinance doesn't have

Things like CASA ratio, Gross NPA, TPV growth, or PLF aren't available
from `yfinance`. The legacy call signatures app.py uses (`pe`,
`roe_raw`, `de_raw`, `profit_margin_raw`, `revenue_cagr`, etc.) are
mapped onto each sector's generic-equivalent metrics automatically.
For richer, sector-native scoring, you can extend any call site to
pass additional sector-specific values — the rule engine gracefully
treats anything missing as "no data for that metric" rather than
penalizing the score, so partial data is always safe.

## Testing

Every module was verified end-to-end: 17+ real-world company/industry
combinations classify correctly, all 14 sectors run cleanly through
the full pipeline (health score, red flags, moat, risk) with no
crashes, and the engine correctly distinguishes "no data" (returns
`None`) from "data exists and is actually bad" (returns `0`).
