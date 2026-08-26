# services/prompts.py
"""
LLM prompt template builders for Stock Research (combined snapshot+bull+
bear), Compare Stocks, Annual Report Simplifier (initial summary + Q&A),
and Ask EquiEye chat. Extracted from app.py's f-strings verbatim, turned
into pure functions — no Streamlit dependency.

build_combined_prompt() takes ~28 already-computed values as parameters
rather than computing them itself — the upstream logic that decides
*which* sector-guardrail text / financials-syntax branch applies to a
given company (in app.py's Stock Research tab) stays in app.py for now.
That branching logic is lower-risk to leave in place than to also
extract and re-verify in the same pass as this already-large template.
"""

from __future__ import annotations

from services.formatters import fmt_crore
from services.comparison import fmt_pe, fmt_pct, fmt_de_compare, fmt_cagr


def build_compare_prompt(
    name_a, pe_a, roe_a, de_a, pm_a, mcap_a, rev_a, rev_cagr_a, rev_cagr_n_a,
    profit_cagr_a, profit_cagr_n_a, score_a, sector_ctx_a,
    name_b, pe_b, roe_b, de_b, pm_b, mcap_b, rev_b, rev_cagr_b, rev_cagr_n_b,
    profit_cagr_b, profit_cagr_n_b, score_b, sector_ctx_b,
    cross_sector_note,
) -> str:
    return f"""
        Compare {name_a} vs {name_b} for an Indian retail investor. Use ONLY the data below — no assumptions.

        {name_a}: P/E={fmt_pe(pe_a)}, ROE={fmt_pct(roe_a)}, D/E={fmt_de_compare(de_a)}, NetMargin={fmt_pct(pm_a)}, MCap={fmt_crore(mcap_a)}, TTM Rev={fmt_crore(rev_a)}, RevCAGR={fmt_cagr(rev_cagr_a, rev_cagr_n_a)}, ProfitCAGR={fmt_cagr(profit_cagr_a, profit_cagr_n_a)}, Score={score_a}/10
        {sector_ctx_a}

        {name_b}: P/E={fmt_pe(pe_b)}, ROE={fmt_pct(roe_b)}, D/E={fmt_de_compare(de_b)}, NetMargin={fmt_pct(pm_b)}, MCap={fmt_crore(mcap_b)}, TTM Rev={fmt_crore(rev_b)}, RevCAGR={fmt_cagr(rev_cagr_b, rev_cagr_n_b)}, ProfitCAGR={fmt_cagr(profit_cagr_b, profit_cagr_n_b)}, Score={score_b}/10
        {sector_ctx_b}
        {cross_sector_note}
        Write exactly 3 focused sentences:
        1. Valuation: compare using the sector-appropriate lens noted above for each company, mention which looks cheaper and why.
        2. Profitability & Growth: compare ROE, margins, and CAGR — which company is compounding faster?
        3. Key risk trade-off: one specific, sector-grounded risk for each company (e.g. high valuation, low growth, high debt, or a sector-specific risk like NPA/attrition/take-rate).
        End with: "Not financial advice."
        """


def build_pdf_summary_prompt(pdf_text_for_summary: str) -> str:
    return f"""
            Analyse this annual report for an Indian retail investor (no prior knowledge assumed).

            1. **Business Summary** (3 sentences: what they do, how they earn, key markets)
            2. **Strengths** (3 specific bullet points)
            3. **Risks** (3 specific bullet points)
            4. **Growth Opportunities** (2 bullet points)
            5. **Financial Health** (2 sentences on revenue, profit, debt trends)
            6. **Key Investor Insight** (1 sentence — most important thing to know)

            Annual Report Text:
            {pdf_text_for_summary}

            Be specific. Avoid jargon — if unavoidable, explain in brackets. Max 400 words total.
            """


def build_pdf_qa_prompt(qa_text: str, prior_history_str: str, active_pdf_q: str) -> str:
    return f"""Answer this question about an annual report. Use ONLY the report text below.
If the answer isn't in the text, say so. Reference actual numbers when present.

REPORT TEXT:
{qa_text}

CONVERSATION:
{prior_history_str}
USER: {active_pdf_q}

Answer concisely (max 150 words). End with disclaimer only if giving financial views.
"""


def build_chat_prompt(live_data_context: str, history_str: str) -> str:
    return f"""You are EquiEye AI — an expert on Indian stock markets. Answer grounded in real data.

{f"LIVE MARKET DATA:{chr(10)}{live_data_context}" if live_data_context else "No live data retrieved. Answer from general knowledge. Be clear you don't have real-time figures."}

CONVERSATION:
{history_str}

Rules:
- If live data available, reference specific numbers (P/E, ROE, D/E, revenue, price change)
- If a SECTOR block is present for a company, apply that sector's specific lens (e.g. use P/B not P/E for banks, flag NPA/CASA for banks, take-rate/TPV for fintechs, attrition for IT services) instead of generic analysis
- If concept question, explain simply with an Indian market example
- For comparisons, directly compare the metrics side by side, noting if the companies are in different sectors and therefore need different valuation lenses
- Max 200 words. End with 1-line disclaimer only for stock-specific views.
"""


def build_combined_prompt(
    name, ticker, sector, cfg_display_name, industry, sec_class_label, sec_class_rule,
    ttm_net_margin, ttm_revenue, ttm_ebitda_m, mkt_cap, pe_display, pb_display,
    roe_display, roa_display, de_display, cur_ratio_disp, div_yield_disp, beta_disp, fcf_disp,
    net_margin_anomalous, ebitda_margin_pct_raw,
    rev_cagr_disp_lbl, prof_cagr_disp_lbl,
    context_source, business_context, sector_prompt_addition, news_context_block,
    fin_display_syntax,
) -> str:
    """The Stock Research tab's combined snapshot+bull+bear analysis
    prompt — the single largest and most heavily-tuned prompt in the
    app. Every parameter here is an already-computed display string or
    boolean; the branching logic that decides their values (sector
    classification, net-margin-anomaly detection, financials-syntax
    choice) stays in app.py's Stock Research tab."""
    return f"""
        You are a senior equity research analyst writing an institutional-grade company brief on {name} ({ticker}) for a sophisticated Indian retail investor.
        Sector: {sector}{f' — classified as {cfg_display_name}' if cfg_display_name else ''} | Industry: {industry} | Asset Class: {sec_class_label}

        ════════════════════════════════════════════════════════
        DESIGNATED METRIC VARIABLES — COPY VERBATIM, DO NOT ALTER OR REFORMAT
        ════════════════════════════════════════════════════════

        ── TTM METRICS (Trailing Twelve Months — rolling 12-month window, NOT a fiscal year) ──
        {{ttm_net_margin}}    = {ttm_net_margin}
        {{ttm_revenue}}       = {ttm_revenue}
        {{ttm_ebitda_margin}} = {ttm_ebitda_m}
        {{market_cap}}        = {mkt_cap}
        {{pe}}                = {pe_display}
        {{pb}}                = {pb_display}
        {{roe}}               = {roe_display}
        {{roa}}               = {roa_display}
        {{de}}                = {de_display}
        {{current_ratio}}     = {cur_ratio_disp}
        {{div_yield}}         = {div_yield_disp}
        {{beta}}              = {beta_disp}
        {{fcf}}               = {fcf_disp}
        {"NET MARGIN CAVEAT: {ttm_net_margin} for this company is not a reliable measure of core operating profitability — reported net income likely includes a large non-operating or exceptional gain (e.g. an asset sale, litigation/arbitration settlement, licensing windfall, or corporate restructuring such as a demerger/spinoff), not core business performance. {roe} may also be unreliable for a related reason (e.g. a restructuring resetting the equity base) — do not treat {ttm_net_margin} and {roe} as contradictory or as evidence of anything about the underlying business; both can be artifacts of the same one-off item. NEVER cite {ttm_net_margin} or {roe} as bull evidence." + (" TTM EBITDA Margin ({ttm_ebitda_margin}) is the more reliable profitability read instead." if ebitda_margin_pct_raw is not None else " EBITDA margin data is not available either — do not substitute any profitability metric as bull evidence for this company; use a qualitative business-strength point instead.") if net_margin_anomalous else ""}

        ── HISTORICAL FY METRICS (from annual fiscal year results — NOT TTM, NOT single-year) ──
        CAGR is a compounded multi-year growth rate spanning discrete fiscal years.
        NEVER write "TTM CAGR", "CAGR over the TTM", or imply CAGR reflects a single year.
        The year span is already embedded in the label (e.g. "4-yr CAGR: 7.2%") — do not restate it.
        {{rev_cagr}}          = {rev_cagr_disp_lbl}
        {{profit_cagr}}       = {prof_cagr_disp_lbl}

        ROUNDING RULE: Copy every variable character-for-character.
        If {{ttm_net_margin}} = {ttm_net_margin}, write "{ttm_net_margin}" — never a truncated form.

        DATA SOURCE RULE: When citing a TTM metric, label it "TTM" in the sentence.
        When citing {{rev_cagr}} or {{profit_cagr}}, these are historical FY trend metrics — do not prefix with "TTM".
        Never mix a TTM figure and a CAGR in a single clause without distinguishing their source.

        COMPANY DESCRIPTION (from {context_source} — treat as authoritative ground truth):
        {business_context}

        {sector_prompt_addition}
        {news_context_block}

        SECTOR CLASS GUARDRAIL — read before writing any bear point:
        This company is classified as {sec_class_label}. {sec_class_rule}

        METRIC USAGE RULES:
        - Each section must cite AT MOST 2 metrics from the designated variables above.
        - Spread metric usage: if {{roe}} or {{roa}} appears in "financials", do not repeat it in bull/bear.
        - Never start two consecutive sentences with the same metric name.
        - Omit a metric if you have nothing new to add — insight beats repetition.

        SNAPSHOT REQUIREMENTS:
        1. "business": What the company does and its revenue model. Cite NO metrics. Source ONLY from the
           company description above. Be SPECIFIC, not generic — name the actual product segments, business
           lines, technology platforms, or operating divisions the description mentions, using vocabulary
           appropriate to THIS company's own sector (e.g. for a pharma company: "chronic therapies, complex
           generics, inhalation products and biosimilars"; for a metals/mining company: "integrated aluminium,
           zinc-lead-silver, and oil & gas operations with captive raw-material sources" — pick examples that
           actually fit the sector in front of you, never reuse a pharma-specific word like "therapy" for a
           non-pharma company). PREFER CONCRETE, ENUMERABLE FACTS over vague summarizing phrases whenever the
           description actually contains them — if the source text gives a count of facilities, named product
           lines, or specific platforms (e.g. "11 R&D centres", "21 manufacturing divisions", "combat aircraft,
           helicopters, UAVs, and jet engines"), USE those specifics rather than collapsing them into a vague
           phrase like "produces a wide range of aircraft" — the vague version is strictly worse when the
           precise version is sitting right there in the source. A sentence that would apply equally to any
           company in this sector is too generic — rewrite it to surface what makes THIS company's business mix
           distinctive, using only what the description actually states. Do NOT just restate the sector
           classification label as the entire answer (e.g. never write only "X is a Generic Formulator
           company" or "X is a Metals & Mining company, with no specific segments mentioned") — that's a
           category, not a description of the business. If the description genuinely contains nothing beyond
           the sector-level classification, it's fine to stay generic rather than invent specifics, but check
           first — most company descriptions do contain real segment/product detail worth surfacing.
        2. "position": Market standing and competitive scale. MUST include {{market_cap}} and {{ttm_revenue}}
           for quantitative scale, AND should also surface qualitative positioning facts drawn ONLY from the
           company description above where available — e.g. market rank/scale claims (only if the description
           actually states one, e.g. "a top-3 generic exporter" or "India's largest diversified natural
           resources company" — never invent a ranking claim that isn't there), named franchise/segment
           strengths appropriate to the sector (e.g. a pharma company's "diabetes and respiratory franchise",
           or a miner's "captive iron ore and bauxite reserves"), geographic footprint, operational/regulatory
           network (e.g. USFDA-approved plants, or integrated smelter-to-finished-product capacity), or a named
           growth vector the description calls out. Write it as a cohesive 1-2 sentence positioning statement,
           not a bare metrics sentence — e.g. "A top-tier Indian generic exporter with a strong diabetes and
           respiratory franchise across 100+ countries and a USFDA-approved manufacturing network, backed by a
           Market Cap of {{market_cap}} and TTM Revenue of {{ttm_revenue}}." Every qualitative claim must trace
           to something the company description actually says — never invent a rank, country count, or
           franchise claim the description doesn't support; if the description offers nothing beyond the
           metrics, it's fine to fall back to the plain "...a Market Cap of {{market_cap}} and TTM Revenue of
           {{ttm_revenue}}." sentence rather than fabricate positioning color.
        3. "financials": MUST follow this exact syntax, chosen by sector:
           — For BANKING or NBFC / LENDING: "The company's financial health is underscored by its Return on Assets of {{roa}} and Return on Equity of {{roe}}, reflecting [one-line qualitative insight]."
             (Net Margin and Revenue CAGR are NOT used here — a lender's "revenue" is interest income, not a comparable growth metric, and margin is meaningless for a bank's cost structure.)
           — For ALL OTHER sectors: "The company's financial health is underscored by its TTM Net Margin of {{ttm_net_margin}} and a {{rev_cagr}}, reflecting [one-line qualitative insight]."
           — {{ttm_net_margin}}/{{roa}}/{{roe}} are TTM figures. {{rev_cagr}} is a historical FY CAGR. Copy all verbatim.
           — Do NOT substitute any other metrics beyond the two specified for the applicable syntax. Do NOT prefix {{rev_cagr}} with "TTM".
        4. "outlook": One forward-looking sentence on the key opportunity or risk for the next 12-24 months.
           At most 1 metric. Full sentence — never truncate mid-phrase. PREFER naming a SPECIFIC program,
           product platform, order, contract, or policy driver over vague phrasing whenever the company
           description or recent news headlines above actually name one — e.g. "growth is tied to Tejas Mk1A
           delivery ramp-up and progress on the AMCA program" is far more credible and useful than "increasing
           demand for its products". Only fall back to vague phrasing if nothing specific is genuinely
           available in the source material — never invent a program or contract name that isn't grounded in
           the description or news provided.

        BULL/BEAR RULES:
        - Each headline: 2-4 words, title case — must match the theme of the explanation
        - Each explanation: one sentence grounded in a specific metric or fact from the designated
          variables, OR — for at most ONE bull and ONE bear point total — a genuinely relevant item
          from RECENT NEWS HEADLINES above, if provided. A real, specific recent event (an
          acquisition, a regulatory action, a management change, a rating action) is stronger
          evidence than a generic sector-level metric point and should be preferred for one slot
          when a relevant headline exists — don't let all 3 slots default to metrics just because
          metrics are always available; a real event beats a generic one.
        - The metric (or news item) must LOGICALLY SUPPORT the headline — never pick a metric just because it hasn't been used yet
        - Choose the 3 most compelling bull themes AND 3 most genuine bear themes for THIS specific company and sector
        - HEADLINE ↔ METRIC COHERENCE (hard rule):
            • A profitability headline (e.g. "Pricing Power", "Margin Strength") → must use a profitability metric (ROE, net margin, EBITDA margin)
              {"— EXCEPT for this company: {ttm_net_margin}/{roe} are not reliable profitability evidence (see NET MARGIN CAVEAT above) and CANNOT be used as bull evidence. Do not create a bull headline like 'Strong Net Margin', 'Pricing Power', 'Exceptional Profitability', or 'High Returns' for this company. Use a qualitative business-strength theme instead, grounded ONLY in the company description and sector context above — e.g. product/brand strength, market position, distribution or network scale, R&D/pipeline depth, or a genuine competitive advantage relevant to this specific sector. Pick whichever is actually supported by the business description; never invent a specific not given to you." if net_margin_anomalous else ""}
            • A growth headline (e.g. "Revenue Momentum", "Compounding Growth") → must use a growth metric (revenue CAGR, profit CAGR, YoY)
            • A balance sheet headline (e.g. "Clean Balance Sheet", "Low Leverage") → must use D/E or current ratio
            • A cash headline (e.g. "Cash Generation", "FCF Strength") → must use FCF
            • A valuation headline (e.g. "Valuation Risk", "Expensive") → must use P/E or P/B
            • A cost/margin risk headline (e.g. "Input Cost Pressure") → must cite the margin or cost metric at risk, NOT current ratio or beta
            • A regulatory/competitive headline → must cite a pricing, margin, or revenue metric at risk — NOT beta or D/E
            • A recent-development headline (choose a label matching the actual event — e.g. "Product Launch" for
              a new offering, "Strategic Acquisition" ONLY for an actual acquisition/purchase, "Leadership Change"
              for a management change, "Credit Rating Action" for a ratings move — never reuse an example label
              whose meaning doesn't match what happened) → must cite the
              specific RECENT NEWS HEADLINE item it's grounded in (paraphrased) — this is the one category that
              does NOT require a designated metric variable, but ONLY use it if a genuinely relevant headline
              was actually provided above; never invent a news event that wasn't given to you.
        - SECTOR OVERRIDE: if Asset Class = BANKING, NBFC / LENDING, or INSURANCE, the generic bull headline
          categories above do NOT apply — use ONLY the headline list given in the SECTOR CLASS GUARDRAIL below
          for that specific asset class (they differ: a bank talks about CASA, an NBFC does not take deposits
          so CASA is invalid for it, and insurance talks about premium/persistency, not credit growth at all).
          The recent-development/news category above is NOT part of this override — it remains available
          for these sectors too, since a real event (e.g. an acquisition, an RBI action) is sector-agnostic.
        - NEVER use "strong growth" or "well-positioned" without a specific number
        - SECTOR CONTRADICTION CHECK: {sec_class_rule}
        - METRIC CONTRADICTION CHECK: if D/E={{de}} do NOT say high debt; if ROE={{roe}} do NOT say weak
          profitability; if P/E={{pe}} sits at or above the sector's own "attractive" valuation threshold
          (see the sector's valuation bands, if given above), do NOT write a bull point saying the stock "may
          be undervalued" or has an "attractive valuation" — a P/E inside or above the sector's normal/fair
          range is not undervaluation, regardless of how the qualitative Quality of the business reads.
          Undervaluation-framed bull points are ONLY valid when the P/E is genuinely low for the sector.
        - LEVERAGE IS SECTOR-RELATIVE, NOT A FIXED THRESHOLD: do NOT label a D/E as "low debt" or "clean
          balance sheet" using a generic all-sector cutoff (e.g. "under 2x = low"). Capital-intensive or
          regulated-asset-base sectors — utilities (generation/transmission/distribution), telecom, real
          estate, capital goods, infrastructure/EPC, NBFC — structurally and appropriately run higher
          leverage than an asset-light sector (IT services, FMCG, pharma, consumer internet); a D/E of
          1.0-2.5x is NORMAL, not a distinguishing strength, for the former group, while the same ratio
          would be genuinely low for the latter. AIRLINES are a distinct, even more extreme case: Ind AS
          116 lease capitalisation of leased aircraft inflates reported D/E to routinely 4-9x+ for a
          perfectly healthy carrier — never describe an airline's D/E as "reasonable", "low", or "clean"
          on an absolute-number basis, and never treat it as alarming without noting it is largely
          lease-driven; judge it only against what is typical for other lease-heavy airlines. Judge
          whether a given D/E is actually low, moderate, or high relative to what is structurally typical
          for THIS company's own sector — use the sector context above as your reference point — never
          against a fixed number that ignores the sector's capital intensity. If leverage is merely
          typical-for-sector, it is not bull-case material at all; only flag it as a bull point when it is
          genuinely LOW relative to sector norms, and only flag it as a bear point when it is genuinely
          HIGH relative to sector norms.

        STRICT OUTPUT RULES:
        - Return ONLY valid JSON. No markdown. No backticks. Start with {{ end with }}
        - Never fabricate metrics — use N/A if data is missing

        {{
          "snapshot": {{
            "business":   "Specific description of what the company does — its actual product lines, business segments, or operating divisions (as applicable to this company's sector) — and how it earns. No metrics, no restating the sector label alone.",
            "position":   "A cohesive positioning statement blending qualitative scale/franchise/footprint facts from the company description with a Market Cap of {mkt_cap} and TTM Revenue of {ttm_revenue}.",
            "financials": "{fin_display_syntax}",
            "outlook":    "One complete forward-looking sentence, at most 1 metric, no truncation."
          }},
          "earnings_summary": "2 sentences on earnings trend. Use {{rev_cagr}} and {{profit_cagr}} verbatim — both are historical FY CAGR metrics, not TTM. Do not write 'TTM CAGR'. No other metrics. No disclaimer.",
          "bull": [
            {{"headline": "Theme headline matching the metric below", "explanation": "One sentence — metric chosen because it is the strongest evidence for THIS headline, not because it is unused."}},
            {{"headline": "Theme headline matching the metric below", "explanation": "One sentence — metric chosen because it is the strongest evidence for THIS headline, not because it is unused."}},
            {{"headline": "Theme headline matching the metric below", "explanation": "One sentence — metric chosen because it is the strongest evidence for THIS headline, not because it is unused."}}
          ],
          "bear": [
            {{"headline": "Risk headline matching the evidence below", "explanation": "One sentence — metric or fact chosen because it directly evidences THIS risk, not because it is unused."}},
            {{"headline": "Risk headline matching the evidence below", "explanation": "One sentence — metric or fact chosen because it directly evidences THIS risk, not because it is unused."}},
            {{"headline": "Risk headline matching the evidence below", "explanation": "One sentence — metric or fact chosen because it directly evidences THIS risk, not because it is unused."}}
          ]
        }}
        """
