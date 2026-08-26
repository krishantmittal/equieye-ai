# modules/sectors/engine.py
"""
Sector Rule Engine
==================
Shared, generic evaluation logic used by health_score, red_flags, and
risk_meter. Every sector module expresses its rules as plain data
(scoring_rules / red_flags lists of dicts) — this engine is the single
place that knows how to *evaluate* that data against a metrics dict.

This is what makes "adding a new sector = new config file" true: the
engine never needs to change when a sector module is added.
"""

from __future__ import annotations
import operator
import re

_OPS = {
    ">":  operator.gt,
    ">=": operator.ge,
    "<":  operator.lt,
    "<=": operator.le,
    "==": operator.eq,
    "!=": operator.ne,
}

# Matches simple condition strings like "gross_npa > 5" or "net_debt_ebitda > 4"
_COND_RE = re.compile(r"^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*(>=|<=|==|!=|>|<)\s*(-?\d+(?:\.\d+)?)\s*$")


def safe_get(metrics: dict, key: str):
    """Returns metrics[key] if present and not None, else None."""
    if metrics is None:
        return None
    val = metrics.get(key)
    return val if val is not None else None


def eval_scoring_rules(metrics: dict, scoring_rules: list[dict], score_max: int = 100) -> dict:
    """
    Evaluates a sector's `scoring_rules` against a metrics dict.

    Each rule: {"metric": str, "op": str, "threshold": float, "points": int, "max": int}
    For each unique (metric, max) "bucket", only the HIGHEST satisfied
    points value is awarded (rules are written in descending threshold
    order, so this picks the best tier the company qualifies for).

    Returns
    -------
    dict with:
        "total_score"     : float, scaled to score_max
        "raw_score"       : float, sum of awarded points
        "raw_max"         : float, sum of all distinct bucket maxes
        "breakdown"       : list of per-metric results
        "metrics_missing" : list of metric ids that had no data
    """
    # Group rules by (metric, max) so we pick the best-satisfied tier per bucket
    buckets: dict[tuple[str, int], list[dict]] = {}
    for rule in scoring_rules:
        key = (rule["metric"], rule["max"])
        buckets.setdefault(key, []).append(rule)

    breakdown = []
    raw_score = 0.0
    raw_max = 0.0
    missing = []

    for (metric_id, bucket_max), rules in buckets.items():
        raw_max += bucket_max
        val = safe_get(metrics, metric_id)
        if val is None:
            missing.append(metric_id)
            breakdown.append({
                "metric": metric_id, "value": None, "awarded": 0,
                "max": bucket_max, "status": "missing_data",
            })
            continue

        # Evaluate every rule in this bucket and keep the highest awarded
        # points among satisfied ones — robust regardless of the order
        # rules happen to be written in within the sector config.
        awarded = 0
        for rule in rules:
            op_fn = _OPS.get(rule["op"], operator.gt)
            try:
                if op_fn(float(val), float(rule["threshold"])) and rule["points"] > awarded:
                    awarded = rule["points"]
            except (TypeError, ValueError):
                continue

        raw_score += awarded
        breakdown.append({
            "metric": metric_id, "value": val, "awarded": awarded,
            "max": bucket_max, "status": "ok",
        })

    # If every bucket's metric was missing, we genuinely have nothing to
    # score on — return None rather than a misleading 0.0 (which would
    # read as "terrible fundamentals" instead of "no data available").
    all_missing = len(missing) == len(buckets)
    total_score = (raw_score / raw_max * score_max) if (raw_max > 0 and not all_missing) else None

    return {
        "total_score": round(total_score, 1) if total_score is not None else None,
        "raw_score": raw_score,
        "raw_max": raw_max,
        "breakdown": breakdown,
        "metrics_missing": missing,
    }


def eval_red_flags(metrics: dict, red_flag_rules: list[dict]) -> list[dict]:
    """
    Evaluates a sector's `red_flags` list against a metrics dict.

    Each rule: {"condition": "metric_id OP threshold", "severity": str, "message": str}

    Returns a list of triggered flags:
        [{"severity": "high", "message": "...", "metric": "gross_npa", "value": 6.2}, ...]
    Flags whose metric is missing from `metrics` are silently skipped
    (we don't warn about data we don't have).
    """
    triggered = []
    for rule in red_flag_rules:
        cond = rule.get("condition", "")
        m = _COND_RE.match(cond)
        if not m:
            continue
        metric_id, op_str, threshold_str = m.groups()
        val = safe_get(metrics, metric_id)
        if val is None:
            continue
        op_fn = _OPS.get(op_str)
        if not op_fn:
            continue
        try:
            if op_fn(float(val), float(threshold_str)):
                triggered.append({
                    "severity": rule.get("severity", "medium"),
                    "message": rule.get("message", f"{metric_id} {op_str} {threshold_str}"),
                    "metric": metric_id,
                    "value": val,
                })
        except (TypeError, ValueError):
            continue

    # Sort: high severity first, then medium, then low
    sev_order = {"high": 0, "medium": 1, "low": 2}
    triggered.sort(key=lambda f: sev_order.get(f["severity"], 3))
    return triggered


def severity_to_risk_points(severity: str) -> int:
    """Maps a red-flag severity to a risk-meter point contribution."""
    return {"high": 25, "medium": 12, "low": 5}.get(severity, 8)
