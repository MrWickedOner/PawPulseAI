"""Output formatter — converts detection results into structured JSON
for the backend API to serve to the frontend.

The output format follows the unified schema agreed upon by the team.
"""

import json
from datetime import datetime
from typing import Any

from pawpulse_ml.baseline.learner import PetBaseline
from pawpulse_ml.detectors.anomaly import (
    AnomalyCheckResult, AnomalyEvent, Severity, SignalDeviation
)
from pawpulse_ml.detectors.trends import TrendReport


def _serialize_severity(s: Severity) -> str:
    return s.value


def _deviation_to_dict(d: SignalDeviation) -> dict:
    return {
        "signal": d.signal.value,
        "value": round(d.value, 2),
        "expected_mean": round(d.expected_mean, 2),
        "expected_std": round(d.expected_std, 2),
        "z_score": round(d.z_score, 2),
        "direction": d.direction,
        "method": d.method,
        "severity": _serialize_severity(d.severity),
    }


def _anomaly_to_dict(a: AnomalyEvent) -> dict:
    return {
        "date": a.date,
        "severity": _serialize_severity(a.severity),
        "confidence": round(a.confidence, 3),
        "signals_affected": [_deviation_to_dict(s) for s in a.signals_affected],
        "narrative": a.narrative,
        "recommendation": a.recommendation,
        "requires_vet_attention": a.requires_vet_attention,
    }


def format_anomaly_result(result: AnomalyCheckResult) -> dict:
    """Format anomaly check result for the API response."""
    return {
        "pet_id": result.pet_id,
        "timestamp": result.timestamp,
        "is_healthy": result.is_healthy,
        "anomaly_count": len(result.anomalies),
        "anomalies": [_anomaly_to_dict(a) for a in result.anomalies],
        "notable_signals": [_deviation_to_dict(d) for d in result.notable_signals],
    }


def format_trend_report(report: TrendReport) -> dict:
    """Format trend report for the API response."""
    trendlines_out = []
    for tl in report.trendlines:
        trendlines_out.append({
            "signal_name": tl.signal_name,
            "current_value": round(tl.current_value, 1),
            "baseline_mean": round(tl.baseline_mean, 1),
            "trend_direction": tl.trend_direction,
            "trend_slope": round(tl.trend_slope, 3),
            "is_significant": tl.is_significant,
            "forecast": {
                "7day": round(tl.forecast_7day, 1),
                "14day": round(tl.forecast_14day, 1),
                "30day": round(tl.forecast_30day, 1),
            },
            "confidence_interval_90": {
                "lower": round(tl.confidence_interval_90_lower, 1),
                "upper": round(tl.confidence_interval_90_upper, 1),
            },
        })

    return {
        "pet_id": report.pet_id,
        "generated_at": datetime.utcnow().isoformat(),
        "data_sufficient": report.data_sufficient,
        "overall_health_trend": report.overall_health_trend,
        "trendlines": trendlines_out,
        "warning_flags": report.warning_flags,
    }


def format_health_summary(
    pet_id: str,
    baseline: PetBaseline,
    anomaly_result: AnomalyCheckResult,
    trend_report: TrendReport,
    tier: str = "basic",
) -> dict:
    """Format complete health summary for the dashboard.

    Tier determines level of detail:
    - basic: anomaly alerts + summary
    - premium: + trendlines, multi-pet dashboard data
    - pro: + full raw data exports
    """
    summary = {
        "pet_id": pet_id,
        "generated_at": datetime.utcnow().isoformat(),
        "tier": tier,
        "baseline_confidence": round(baseline.confidence_in_baseline(), 3),
        "data_days": baseline.data_days_used,
        "is_mature": baseline.is_mature,
        "health_status": "healthy" if anomaly_result.is_healthy else "attention_needed",
        "anomalies": format_anomaly_result(anomaly_result),
        "breed": baseline.breed,
        "age_years": baseline.age_years,
    }

    if tier in ("premium", "pro"):
        summary["trends"] = format_trend_report(trend_report)

    if tier == "pro":
        summary["baseline_stats"] = {
            "daily_score": _baseline_to_dict(baseline.daily_score),
            "daily_play": _baseline_to_dict(baseline.daily_play),
            "daily_active": _baseline_to_dict(baseline.daily_active),
            "daily_rest": _baseline_to_dict(baseline.daily_rest),
            "daily_distance": _baseline_to_dict(baseline.daily_distance),
        }

    return summary


def _baseline_to_dict(baseline) -> dict:
    if baseline is None:
        return {}
    return {
        "mean": round(baseline.mean, 2),
        "std": round(baseline.std, 2),
        "median": round(baseline.median, 2),
        "p5": round(baseline.p5, 2),
        "p25": round(baseline.p25, 2),
        "p75": round(baseline.p75, 2),
        "p95": round(baseline.p95, 2),
        "n_samples": baseline.n_samples,
        "is_breed_prior": baseline.is_breed_prior,
    }
