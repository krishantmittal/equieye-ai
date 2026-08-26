# EquiEye AI 📈
### AI-Powered Equity Research Assistant for Indian Retail Investors

> **Disclaimer:** EquiEye AI is for educational and research purposes only. It does not constitute financial advice. Always consult a SEBI-registered investment advisor before making investment decisions.

---

## What is EquiEye AI?

EquiEye AI helps first-generation Indian retail investors research stocks the way analysts do — without needing to read 200-page annual reports or decode financial jargon.

The Indian retail investor base has grown sharply in recent years, yet most retail investors make decisions based on tips and YouTube videos rather than fundamentals. EquiEye AI bridges that gap by combining live market data with AI-generated, plain-English analysis.

---

## Features

### 📊 Stock Research (Core Module)
- Live price, market cap, P/E, ROE, Debt/Equity via yfinance
- Revenue & profit trend charts (multi-year)
- AI-generated Company Snapshot in plain English
- Bull Case & Bear Case, each rendered as distinct, separated points (not a single paragraph)
- Financial Health Score (out of 10) with a plain-English verdict
- **Red Flag Detector** — flags high debt, margin compression, cash flow risk, and overvaluation
- Live news headlines (via NewsAPI) with AI-generated sentiment labeling

### 🔎 Company Search & Disambiguation
- Backed by NSE's own official equity listing (~2,374 companies), not just an AI guess
- Typing an ambiguous group name (e.g. "HDFC", "Tata", "Bajaj") shows every matching listed entity as a picker, instead of silently guessing one
- Correctly handles the 2025 Tata Motors demerger into two separately listed entities (Commercial Vehicles and Passenger Vehicles)
- Manual ticker entry available as a fallback if a company genuinely isn't found

### ⚖️ Stock Comparison
- Compare any two NSE-listed stocks side-by-side, with the same disambiguation picker as Stock Research
- Key metrics table
- AI verdict on relative valuation and risk

### 📄 Annual Report Simplifier
- Upload any annual report PDF
- AI extracts: business summary, strengths, risks, growth opportunities, financial health
- Designed for investors who have never read an annual report

### 💬 Ask EquiEye
- Conversational AI chat for Indian markets, grounded in live data when a specific company is detected in the question
- Can detect and pull live data for **two** companies in one question (e.g. "Compare HDFC Bank and ICICI Bank", "TCS vs Infosys")
- Asks for clarification rather than guessing when a question is genuinely ambiguous (e.g. "Tata Motors" without specifying which of the two demerged entities)
- Examples:
  - *"Why did Paytm fall?"*
  - *"How does Zomato make money?"*
  - *"What is free cash flow?"*
  - *"Compare HDFC Bank and ICICI Bank"*

---

## Tech Stack

| Layer | Tool |
|---|---|
| Frontend | Streamlit |
| Stock Data | yfinance (NSE via Yahoo Finance) |
| Company Database | NSE's official equity listing CSV (local, bundled) |
| News | NewsAPI |
| AI Engine | Groq API (openai/gpt-oss-120b, with openai/gpt-oss-20b for lightweight calls) — Gemini 2.5 Flash as fallback |
| PDF Parsing | PyPDF2 |
| Deployment | Streamlit Cloud |

---

## Local Setup

```bash
# 1. Clone the repo
git clone https://github.com/yourusername/finsight-ai.git
cd finsight-ai

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your API keys
# Edit .streamlit/secrets.toml and add:
# GROQ_API_KEY = "your-groq-key-here"
# NEWS_API_KEY = "your-newsapi-key-here"

# 4. Run
streamlit run app.py
```

---

## Company Search

Company search isn't a hardcoded list — it's backed by NSE's own published equity listing file (`data/nse_equity_list.csv`), downloaded directly from nseindia.com. This means:

- Any of NSE's ~2,374 listed companies can be found by name or ticker
- Ambiguous names show every real match as a picker (e.g. typing "HDFC" shows HDFC Bank, HDFC Life, and HDFC AMC)
- Corporate actions that were live in the data at the time of download — like the Tata Motors 2025 demerger or the Zomato → Eternal rename — are correctly reflected

---

## Known Limitations

This section is intentional — understanding where the app falls short is as important as what it gets right, and it's documented honestly rather than glossed over.

1. **The company database is a static snapshot, not a live feed.** `nse_equity_list.csv` reflects NSE's listings as of the day it was downloaded. New listings, delistings, or future corporate actions (mergers, demergers, renames) won't be reflected until the file is manually re-downloaded from nseindia.com and replaced. A production version would need either a paid data subscription or a scheduled refresh job.

2. **yfinance is an unofficial, free data source — not a licensed feed.** It occasionally fails to return data for legitimate, heavily-traded stocks due to Yahoo Finance throttling, even with retry logic built in. This is a structural limitation of the tool, not a bug that can be fully eliminated without switching to a paid provider (e.g. a broker API like Kite Connect, or a commercial feed like Bloomberg/Refinitiv).

3. **Ask EquiEye detects at most two distinct companies per question.** It can compare two named companies (e.g. "TCS vs Infosys") but doesn't attempt to handle three or more in a single question — those would need to be asked as follow-ups.

4. **Genuinely ambiguous questions are met with a clarification request, not a guess.** If a question mentions a group name that maps to multiple real, currently-listed entities (e.g. "Tata Motors" after its 2025 demerger), the app asks the user to specify which one rather than silently picking one and potentially giving wrong context.

5. **News coverage depends on NewsAPI's free tier**, which has a request-volume cap and can have limited or delayed coverage for smaller-cap Indian companies. Sentiment labeling on those headlines is AI-generated, not human-verified.

6. **AI-generated content is an interpretation, not a guarantee.** Bull case, bear case, financial health scores, and red flags are LLM-generated readings of real financial metrics — the underlying numbers are real and live, but the narrative judgment around them is probabilistic. It should be read as a starting point for research, not a recommendation.

7. **No portfolio or transaction features, by design.** This is a research and analysis tool, not a trading platform — there's no brokerage integration, no real money involved, and no holdings tracking.

8. **PDF parsing works best on text-based annual reports.** Scanned or image-only PDFs aren't OCR-processed, so text extraction may be incomplete for those documents.

---

## Project Context

Built as a personal project to explore the intersection of LLMs and financial analysis in the Indian market context — including the practical engineering challenges of keeping company data accurate (ticker renames, demergers, ambiguous group names) rather than just wiring up an API and calling it done.

---

## License

MIT License. Not for commercial use without permission.
