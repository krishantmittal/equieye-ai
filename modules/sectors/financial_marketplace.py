# modules/sectors/financial_marketplace.py
"""
Financial Products Marketplace / Aggregator — Sector Module
==============================================================
For companies like PB Fintech (Policybazaar + Paisabazaar) that sell OTHER
companies' insurance policies and loans for a commission, rather than
underwriting insurance risk themselves or processing payment transaction
volume. This was previously falling through to whichever keyword matched
first in the detector — "insurance" (because "Insurance Brokers" is the
literal yfinance industry tag) or occasionally "fintech" — neither of which
fits. An insurer's risk framework (underwriting discipline, combined ratio,
persistency of the POLICY, embedded value, catastrophic claims) describes
the insurer's balance sheet risk, not this company's, since this company
never holds underwriting risk at all. A payments fintech's framework (TPV,
take rate on transaction volume) doesn't fit either — this company earns
commission on POLICIES/LOANS SOLD, not on payment volume processed.
"""

SECTOR_CONFIG: dict = {
    "slug": "financial_marketplace",
    "display_name": "Financial Products Marketplace",

    "key_metrics": [
        {"id": "insurance_premium_sold", "label": "Insurance Premium Sold (Annualised)", "unit": "₹Cr", "yf_key": None, "higher_is_better": True},
        {"id": "loan_disbursal_growth",  "label": "Loan Disbursal Growth (YoY)",          "unit": "%",   "yf_key": None, "higher_is_better": True},
        {"id": "renewal_persistency",    "label": "Renewal/Trail Persistency (Platform)", "unit": "%",   "yf_key": None, "higher_is_better": True},
        {"id": "cac",                    "label": "Customer Acquisition Cost",            "unit": "₹",   "yf_key": None, "higher_is_better": False},
        {"id": "contribution_margin",    "label": "Contribution Margin",                  "unit": "%",   "yf_key": None, "higher_is_better": True},
        {"id": "ebitda_margin",          "label": "EBITDA Margin",                        "unit": "%",   "yf_key": "ebitdaMargins", "higher_is_better": True},
        {"id": "revenue_growth",         "label": "Revenue Growth (YoY)",                 "unit": "%",   "yf_key": "revenueGrowth", "higher_is_better": True},
        {"id": "organic_traffic_share",  "label": "Organic/Direct Traffic Share",         "unit": "%",   "yf_key": None, "higher_is_better": True},
    ],

    "scoring_rules": [
        {"metric": "revenue_growth",      "op": ">", "threshold": 30.0, "points": 20, "max": 20},
        {"metric": "revenue_growth",      "op": ">", "threshold": 15.0, "points": 10, "max": 20},
        {"metric": "ebitda_margin",       "op": ">", "threshold": 10.0, "points": 20, "max": 20},
        {"metric": "ebitda_margin",       "op": ">", "threshold": 0.0,  "points": 10, "max": 20},
        {"metric": "renewal_persistency", "op": ">", "threshold": 80.0, "points": 20, "max": 20},
        {"metric": "renewal_persistency", "op": ">", "threshold": 60.0, "points": 10, "max": 20},
        {"metric": "contribution_margin", "op": ">", "threshold": 40.0, "points": 20, "max": 20},
        {"metric": "organic_traffic_share","op": ">", "threshold": 50.0, "points": 20, "max": 20},
    ],
    "score_max": 100,

    "risk_factors": [
        "Commission-rate risk — insurers/lenders can cut payout rates to distributors at any renewal of the "
        "distribution agreement, directly compressing the platform's core revenue line",
        "Insurer/lender disintermediation risk — partners can build their own direct-to-consumer digital "
        "channel and bypass the marketplace entirely once they've captured enough of the demand it generated",
        "Renewal/trail commission attrition — if customers stop renewing THROUGH the platform (switching to "
        "the insurer directly, or to a competing aggregator), trail income erodes even if the underlying "
        "policy itself stays active",
        "Customer acquisition cost inflation as digital ad costs rise and competition from other aggregators "
        "and insurer-direct apps intensifies",
        "Regulatory risk specific to intermediaries — IRDAI can cap broker/corporate-agent commission "
        "structures directly, independent of anything happening on the insurer's own balance sheet",
        "Organic search/SEO dependency — a material share of customer acquisition relies on search ranking "
        "for comparison queries, which is not fully within the company's control",
        "Cross-sell execution risk — the bull case depends on successfully cross-selling loans/credit "
        "products to the insurance customer base (or vice versa); this requires real operational execution, "
        "not just having both business lines under one roof",
    ],

    "moat_factors": [
        {"factor": "Organic Traffic / SEO Dominance", "description": "Years of SEO investment for high-intent comparison-shopping search queries is slow and expensive to replicate — a real, structural customer-acquisition-cost advantage over a new entrant"},
        {"factor": "Multi-Category Cross-Sell Platform", "description": "Insurance + lending under one platform lets the company amortise customer acquisition cost across multiple products, lowering blended CAC versus a single-category competitor"},
        {"factor": "Marketplace Scale / Partner Breadth", "description": "The largest number of insurer/lender tie-ups gives customers the most complete comparison, which itself attracts more traffic and reinforces scale — a real, if moderate, network effect"},
        {"factor": "Aggregator Brand Trust", "description": "Being the recognised default place to compare insurance/loan products is a genuine, slow-to-build brand asset for a category where trust drives the click"},
        {"factor": "Offline Agent Network Reach", "description": "A physical advisor/agent network (e.g. PB Partners) extends distribution into Tier 2/3 geographies that pure digital acquisition doesn't reach cost-effectively"},
        {"factor": "Switching Costs (Weak — Not a Real Moat Here)", "description": "Unlike a payments app or an insurer's own policyholder base, a customer can freely compare across multiple aggregators with no switching cost at all — this is a genuine structural weakness of the marketplace model, not a strength, and should not be scored as a moat factor the way brand or scale are"},
    ],

    "bull_case": [
        "India's insurance penetration (~4% of GDP) remains well below the global average, and lending "
        "penetration/formal credit access has similar headroom — a long runway for aggregator-led "
        "distribution specifically, not just the underlying insurer/lender market",
        "Cross-selling loans and credit products to the existing insurance customer base (and vice versa) "
        "lowers blended customer acquisition cost as the platform matures",
        "Rising online insurance/loan comparison adoption structurally shifts distribution share away from "
        "costly offline-only agent channels toward aggregators",
        "Operating leverage: the core tech/brand platform is largely fixed-cost, so incremental revenue from "
        "scale drops through disproportionately to margin",
        "Offline agent network (PB Partners-type channel) opening Tier 2/3 city distribution without a "
        "proportional increase in digital customer acquisition cost",
        "Regulatory push toward expanding insurance coverage (e.g. IRDAI's 'Insurance for All' agenda) grows "
        "the total addressable market for every distribution channel, aggregators included",
    ],

    "bear_case": [
        "Falling insurance/loan commission rates from partner insurers and lenders directly compress the "
        "core revenue line — this is a distribution-side pricing risk specific to being an intermediary, "
        "not an underwriting or credit risk",
        "Rising customer acquisition cost as digital ad inflation and aggregator/insurer-direct competition "
        "intensify, compressing unit economics even if gross transaction volume keeps growing",
        "Structural dependence on insurer/lender partners who could reduce reliance on the marketplace by "
        "investing more heavily in their own direct digital acquisition",
        "Reduced renewal/trail income if platform-level persistency declines — customers renewing away from "
        "the platform (directly with the insurer, or via a competing aggregator) rather than the underlying "
        "policy lapsing",
        "Lower quote-to-conversion rates if regulatory disclosure or comparison-display requirements change "
        "the way products can be presented",
        "Technology/new-entrant disruption — a well-funded new aggregator or an insurer's own upgraded "
        "direct-to-consumer app could erode market share faster than the incumbent's brand moat protects it",
    ],

    "red_flags": [
        {"condition": "revenue_growth < 10",       "severity": "high",   "message": "Revenue growth < 10% — core marketplace growth engine losing momentum"},
        {"condition": "ebitda_margin < -15",        "severity": "high",   "message": "EBITDA margin < -15% — cash burn rate raises sustainability concerns"},
        {"condition": "renewal_persistency < 50",   "severity": "high",   "message": "Renewal persistency < 50% — customers not renewing through the platform, eroding trail/recurring revenue"},
        {"condition": "cac > contribution_margin",  "severity": "medium", "message": "Customer acquisition cost rising faster than contribution margin can absorb — unit economics under pressure"},
    ],

    "valuation": {
        "primary":   ["EV/Sales", "P/E (only once durably profitable)"],
        "secondary": ["EV/Gross Profit", "Price/Insurance Premium Sold"],
        "notes": (
            "Do NOT apply an insurer's valuation framework (embedded value, P/EV, solvency-adjusted book "
            "value) — this company has no underwriting balance sheet to value that way. Early-stage / "
            "pre-consistent-profitability periods are better judged on EV/Sales and path to EBITDA "
            "positivity, similar to other consumer-internet platforms; once profitability is durable and "
            "not a one-off recovery from a previously loss-making base, a growth-adjusted P/E (PEG) becomes "
            "more relevant. A high headline P/E immediately after a swing from loss to profit often reflects "
            "the market pricing in a normalized future earnings run-rate rather than current-year earnings — "
            "worth flagging rather than treating as a straightforward sign of overvaluation, though it isn't "
            "evidence of undervaluation either."
        ),
    },

    "llm_context": (
        "This is a FINANCIAL PRODUCTS MARKETPLACE / AGGREGATOR (e.g. PB Fintech — Policybazaar for "
        "insurance, Paisabazaar for loans) — it sells other companies' insurance policies and loans for a "
        "commission, and never holds underwriting risk, policyholder reserves, or a combined ratio. "
        "Distinct from an INSURER (underwriting discipline, embedded value, VNB margin, catastrophic-claims "
        "exposure — none apply here) and from a PAYMENTS FINTECH (transaction take-rate — also doesn't "
        "apply). 'Persistency' here means whether the customer renews THROUGH THIS PLATFORM, not the "
        "insurer's policy-level persistency used in embedded-value calculations. "
        "Focus on: CAC trend and organic/SEO traffic dependency, insurance-lending cross-sell, digital + "
        "offline agent-network distribution scale, commission-rate risk from partner insurers/lenders (this "
        "company's real 'pricing' risk), and disintermediation risk if partners build their own "
        "direct-to-consumer channel. "
        "BULL theme: India's insurance/credit under-penetration driving structural, aggregator-led "
        "distribution growth, plus cross-sell-driven CAC efficiency as the platform matures. "
        "BEAR theme: commission-rate/payout cuts from partners and rising CAC — never underwriting losses, "
        "catastrophic claims, or combined-ratio deterioration, none of which apply to a distributor."
    ),
}
