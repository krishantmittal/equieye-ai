"""
modules/news_sentiment.py
-------------------------
News sentiment classification and deduplication for EquiEye AI.

Features:
- Rule-based sentiment classifier (no extra API calls needed)
- Duplicate article removal via title similarity
- Overall sentiment score aggregation
- Sentiment labels: Positive / Neutral / Negative
"""

from __future__ import annotations
import re


# ── Keyword lists for rule-based sentiment ────────────────────────────────────
_POSITIVE_KEYWORDS = [
    "profit", "surge", "record", "growth", "beat", "outperform", "rally",
    "upgrade", "buy", "strong", "expansion", "deal", "win", "award",
    "dividend", "buyback", "acquisition", "launch", "revenue rise",
    "earnings beat", "raises guidance", "positive", "gain", "up",
    "increase", "improve", "recovery", "boost", "approval", "milestone",
    "order", "contract", "partnership", "invest", "expand", "higher",
    "quarterly profit", "annual profit", "net profit rises", "jumps", "soars"
]

_NEGATIVE_KEYWORDS = [
    "loss", "decline", "fall", "drop", "miss", "disappoint", "downgrade",
    "sell", "weak", "cut", "layoff", "resign", "fraud", "scandal",
    "penalty", "fine", "sebi", "probe", "investigation", "default",
    "debt", "downfall", "crash", "slump", "below expectations",
    "miss estimates", "negative", "concern", "risk", "pressure", "warning",
    "reduces guidance", "revenue miss", "profit falls", "drops", "plunges",
    "npa", "bad loan", "restructuring", "closure", "suspend"
]

_NEUTRAL_KEYWORDS = [
    "meeting", "annual general", "agm", "announcement", "regulatory",
    "board approves", "board meeting", "quarterly", "result", "report"
]


def classify_sentiment(title: str, description: str = "") -> dict:
    """
    Rule-based sentiment classifier for news headlines.
    Returns {'label': str, 'icon': str, 'color': str, 'score': int}
    score: +1 = positive, 0 = neutral, -1 = negative
    """
    text = (f"{title} {description}").lower()

    pos_hits = sum(1 for kw in _POSITIVE_KEYWORDS if kw in text)
    neg_hits = sum(1 for kw in _NEGATIVE_KEYWORDS if kw in text)

    if pos_hits > neg_hits + 1:
        return {"label": "Positive", "icon": "🟢", "color": "#166534", "score": 1}
    elif neg_hits > pos_hits + 1:
        return {"label": "Negative", "icon": "🔴", "color": "#B91C1C", "score": -1}
    elif pos_hits > neg_hits:
        return {"label": "Positive", "icon": "🟢", "color": "#166534", "score": 1}
    elif neg_hits > pos_hits:
        return {"label": "Negative", "icon": "🔴", "color": "#B91C1C", "score": -1}
    else:
        return {"label": "Neutral", "icon": "🟡", "color": "#92400E", "score": 0}


def _title_fingerprint(title: str) -> str:
    """Normalize title for deduplication."""
    t = title.lower()
    t = re.sub(r'[^a-z0-9 ]', '', t)
    words = t.split()
    # Take first 6 significant words
    stop = {"the", "a", "an", "in", "on", "at", "of", "and", "or", "for", "to", "is", "are", "was"}
    sig_words = [w for w in words if w not in stop][:6]
    return " ".join(sig_words)


def deduplicate_articles(articles: list[dict]) -> list[dict]:
    """
    Remove duplicate/near-duplicate articles based on title similarity.
    Keeps the first occurrence of each near-duplicate cluster.
    """
    seen = set()
    result = []
    for article in articles:
        fp = _title_fingerprint(article.get("title", ""))
        if fp and fp not in seen:
            seen.add(fp)
            result.append(article)
    return result


def enrich_articles(articles: list[dict]) -> list[dict]:
    """
    Add sentiment classification to each article.
    Returns enriched list with 'sentiment' key added.
    """
    enriched = []
    for article in articles:
        title = article.get("title", "")
        desc  = article.get("description", "")
        sentiment = classify_sentiment(title, desc)
        enriched.append({**article, "sentiment": sentiment})
    return enriched


def compute_overall_sentiment(enriched_articles: list[dict]) -> dict:
    """
    Aggregate overall sentiment from a list of enriched articles.
    Returns {'label', 'icon', 'color', 'score', 'positive', 'neutral', 'negative'}
    """
    if not enriched_articles:
        return {"label": "No Data", "icon": "⚪", "color": "#6B7280", "score": 0,
                "positive": 0, "neutral": 0, "negative": 0}

    scores = [a["sentiment"]["score"] for a in enriched_articles]
    pos = scores.count(1)
    neg = scores.count(-1)
    neu = scores.count(0)
    total = len(scores)

    avg = sum(scores) / total

    if avg > 0.25:
        label, icon, color = "Positive", "🟢", "#166534"
    elif avg < -0.25:
        label, icon, color = "Negative", "🔴", "#B91C1C"
    else:
        label, icon, color = "Neutral", "🟡", "#92400E"

    return {
        "label": label, "icon": icon, "color": color,
        "score": round(avg, 2),
        "positive": pos, "neutral": neu, "negative": neg
    }
