"""Trendline prediction engine for PawPulse Premium.

Provides 30-day look-ahead forecasts for key health signals.
Uses linear trend extrapolation with confidence intervals.
For Premium tier, this provides "predictive trendlines" as described
in the business plan.
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Optional


@dataclass
class Trendline:
    """A trendline forecast for one signal."""
    signal_name: str
    current_value: float
    baseline_mean: float
    trend_direction: str  # "stable", "increasing", "decreasing", "volatile"
    trend_slope: float  # units per day
    slope_p_value: float  # statistical significance of slope
    forecast_7day: float
    forecast_14day: float
    forecast_30day: float
    confidence_interval_90_lower: float
    confidence_interval_90_upper: float
    is_significant: bool  # slope is statistically significant


@dataclass
class TrendReport:
    """Complete trend report for a pet."""
    pet_id: str
    trendlines: list[Trendline]
    overall_health_trend: str  # "improving", "stable", "declining", "mixed"
    data_sufficient: bool
    warning_flags: list[str]


def compute_trendline(
    values: pd.Series,
    signal_name: str,
    baseline_mean: float,
    min_points: int = 7,
) -> Optional[Trendline]:
    """Compute a 30-day trendline forecast from historical values.

    Uses simple linear regression for transparency and speed.
    Forecast uncertainty increases with horizon.
    """
    from scipy import stats as scipy_stats

    values = values.dropna()
    if len(values) < min_points:
        return None

    # Create time index (days from start)
    x = np.arange(len(values))
    y = values.values.astype(float)

    # Linear regression
    slope, intercept, r_value, p_value, std_err = scipy_stats.linregress(x, y)

    current = float(y[-1])
    trend_slope = float(slope)

    # Classify direction
    is_significant = p_value < 0.1  # p < 0.1 = nominally significant
    if not is_significant:
        trend_direction = "stable"
    elif slope > 0:
        trend_direction = "increasing"
    else:
        trend_direction = "decreasing"

    # Check volatility
    residuals = y - (intercept + slope * x)
    rmse = float(np.sqrt(np.mean(residuals ** 2)))
    if rmse > baseline_mean * 0.3 if baseline_mean > 0 else rmse > 10:
        trend_direction = "volatile"

    # Compute forecasts (in days from now)
    last_idx = len(values) - 1
    forecast_7day = float(intercept + slope * (last_idx + 7))
    forecast_14day = float(intercept + slope * (last_idx + 14))
    forecast_30day = float(intercept + slope * (last_idx + 30))

    # Confidence intervals expand with horizon
    ci_90_margin = 1.645 * std_err * np.sqrt(
        1 + 1 / len(values) + (np.arange(len(values)) - x.mean()) ** 2 / np.sum((x - x.mean()) ** 2)
    )
    # Use last margin for forecast
    last_margin = float(ci_90_margin[-1]) if len(ci_90_margin) > 0 else rmse
    # Scale margin by sqrt of horizon ratio
    horizon_scale_30 = np.sqrt(30 / max(1, len(values)))
    ci_margin = last_margin * 1.5 * horizon_scale_30

    return Trendline(
        signal_name=signal_name,
        current_value=current,
        baseline_mean=baseline_mean,
        trend_direction=trend_direction,
        trend_slope=trend_slope,
        slope_p_value=float(p_value),
        forecast_7day=forecast_7day,
        forecast_14day=forecast_14day,
        forecast_30day=forecast_30day,
        confidence_interval_90_lower=forecast_30day - ci_margin,
        confidence_interval_90_upper=forecast_30day + ci_margin,
        is_significant=is_significant,
    )


def compute_trend_report(
    pet_id: str,
    daily_df: pd.DataFrame,
    baseline,
) -> TrendReport:
    """Generate a complete trend report for a pet."""
    if daily_df is None or len(daily_df) < 7:
        return TrendReport(
            pet_id=pet_id,
            trendlines=[],
            overall_health_trend="stable",
            data_sufficient=False,
            warning_flags=["Insufficient data for trend analysis (need 7+ days)"],
        )

    trendlines = []
    signals_to_check = [
        ("activity_score", "Activity Score", baseline.daily_score.mean if baseline.daily_score else 500),
        ("play_minutes", "Play Time", baseline.daily_play.mean if baseline.daily_play else 45),
        ("active_minutes", "Active Time", baseline.daily_active.mean if baseline.daily_active else 135),
        ("rest_minutes", "Rest Time", baseline.daily_rest.mean if baseline.daily_rest else 960),
        ("distance_km", "Distance", baseline.daily_distance.mean if baseline.daily_distance else 5.0),
    ]

    for col, name, base_mean in signals_to_check:
        if col in daily_df.columns and len(daily_df[col].dropna()) >= 7:
            tl = compute_trendline(daily_df[col], name, base_mean)
            if tl:
                trendlines.append(tl)

    # Determine overall trend
    declining = [t for t in trendlines if t.trend_direction == "decreasing" and t.is_significant]
    improving = [t for t in trendlines if t.trend_direction == "increasing" and t.is_significant]
    volatile = [t for t in trendlines if t.trend_direction == "volatile"]

    warning_flags = []
    for tl in trendlines:
        if tl.trend_direction == "decreasing" and tl.is_significant:
            warning_flags.append(
                f"{tl.signal_name} is trending downward "
                f"({tl.trend_slope:.2f}/day, p={tl.slope_p_value:.3f})"
            )
        if tl.trend_direction == "volatile":
            warning_flags.append(f"{tl.signal_name} shows high volatility")

    if len(declining) >= 2:
        overall = "declining"
    elif len(improving) >= 2:
        overall = "improving"
    elif len(warning_flags) > 0:
        overall = "declining" if len(declining) > 0 else "mixed"
    else:
        overall = "stable"

    return TrendReport(
        pet_id=pet_id,
        trendlines=trendlines,
        overall_health_trend=overall,
        data_sufficient=len(daily_df) >= 7,
        warning_flags=warning_flags,
    )
