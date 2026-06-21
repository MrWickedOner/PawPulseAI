"""Data preprocessing for PawPulse anomaly detection engine.

Handles:
- Normalization from device-specific schema to unified format
- Gap detection and interpolation
- Rolling window feature computation
- Day/night segmentation
"""

import numpy as np
import pandas as pd
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class ProcessedPetData:
    """Normalized, preprocessed data for a single pet ready for analysis."""
    pet_id: str
    breed: str
    age_years: float
    weight_kg: float

    # Daily timeseries (pandas DataFrame with DatetimeIndex)
    daily: Optional[pd.DataFrame] = None

    # Hourly timeseries (pandas DataFrame with DatetimeIndex)
    hourly: Optional[pd.DataFrame] = None

    # Key metrics
    data_days_available: int = 0
    data_quality_score: float = 1.0  # 0-1
    gaps_detected: list = field(default_factory=list)

    # Sources available
    sources: list = field(default_factory=list)


def normalize_fitbark_daily(records: list[dict]) -> pd.DataFrame:
    """Convert FitBark ActivityDaily records to normalized DataFrame."""
    if not records:
        return pd.DataFrame()

    df = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["date"])
    df.set_index("date", inplace=True)
    df.sort_index(inplace=True)

    # Map to unified names
    df["activity_score"] = df.get("score", 0)
    df["play_minutes"] = df.get("min_play", 0)
    df["active_minutes"] = df.get("min_active", 0)
    df["rest_minutes"] = df.get("min_rest", 0)
    df["distance_km"] = df.get("distance_in_miles", 0) * 1.60934
    df["calories"] = df.get("calories", 0)
    df["goal_progress"] = df.get("goal_progress", 0)

    return df


def normalize_fitbark_hourly(records: list[dict]) -> pd.DataFrame:
    """Convert FitBark ActivityHourly records to normalized DataFrame."""
    if not records:
        return pd.DataFrame()

    df = pd.DataFrame(records)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df.set_index("timestamp", inplace=True)
    df.sort_index(inplace=True)

    df["score"] = df.get("score", 0)
    df["play_minutes"] = df.get("min_play", 0)
    df["active_minutes"] = df.get("min_active", 0)
    df["rest_minutes"] = df.get("min_rest", 0)

    return df


def detect_gaps(series: pd.Series, max_gap_hours: float = 4.0) -> list[dict]:
    """Detect gaps in time series data."""
    if len(series) < 2:
        return []

    gaps = []
    time_diff = series.index.to_series().diff()

    for i, diff in enumerate(time_diff):
        if i == 0:
            continue
        gap_hours = diff.total_seconds() / 3600
        if gap_hours > max_gap_hours:
            gaps.append({
                "start": series.index[i - 1],
                "end": series.index[i],
                "duration_hours": gap_hours,
            })

    return gaps


def compute_rolling_features(df: pd.DataFrame, window_days: int = 7) -> pd.DataFrame:
    """Add rolling window features for anomaly detection."""
    df = df.copy()

    # Daily rolling
    for col in ["activity_score", "play_minutes", "active_minutes",
                "rest_minutes", "distance_km", "calories"]:
        if col in df.columns and df[col].notna().sum() > window_days:
            df[f"{col}_rolling_mean_{window_days}d"] = df[col].rolling(
                window=window_days, min_periods=max(3, window_days // 2)
            ).mean()
            df[f"{col}_rolling_std_{window_days}d"] = df[col].rolling(
                window=window_days, min_periods=max(3, window_days // 2)
            ).std()

    # Day-over-day change
    for col in ["activity_score", "play_minutes", "rest_minutes"]:
        if col in df.columns:
            df[f"{col}_dod_change"] = df[col].diff()
            df[f"{col}_dod_pct_change"] = df[col].pct_change() * 100

    return df


def compute_hourly_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add hourly-specific features."""
    if df is None or len(df) == 0:
        return df

    df = df.copy()
    df["hour"] = df.index.hour
    df["day_of_week"] = df.index.dayofweek
    df["is_night"] = (df["hour"] < 6) | (df["hour"] >= 22)
    df["is_weekend"] = df["day_of_week"] >= 5

    return df


def fill_missing_hours(df: pd.DataFrame, max_gap_hours: int = 6) -> pd.DataFrame:
    """Fill missing hours with interpolation (for short gaps only)."""
    if df is None or len(df) == 0:
        return df

    # Create complete hourly index
    full_idx = pd.date_range(
        start=df.index.min().floor("h"),
        end=df.index.max().ceil("h"),
        freq="h"
    )

    df = df.reindex(full_idx)

    # Only interpolate gaps <= max_gap_hours
    gap_mask = df.isna().any(axis=1)
    gap_runs = _find_runs(gap_mask)

    for start_idx, end_idx, is_gap in gap_runs:
        if not is_gap:
            continue
        gap_len = end_idx - start_idx
        if gap_len <= max_gap_hours:
            # Fill this short gap
            for col in df.columns:
                if col in ["is_night", "is_weekend", "hour", "day_of_week"]:
                    continue
                if df[col].dtype in (np.float64, np.int64):
                    df.loc[full_idx[start_idx:end_idx], col] = np.nan
                    df[col] = df[col].interpolate(method="linear", limit=max_gap_hours)

    # Fill remaining short gaps with forward fill then backward fill
    for col in df.select_dtypes(include=[np.number]).columns:
        if col not in ["is_night", "is_weekend", "hour", "day_of_week"]:
            df[col] = df[col].ffill(limit=2).bfill(limit=2)

    return df


def _find_runs(mask: pd.Series) -> list[tuple]:
    """Find contiguous runs of True/False values. Returns (start, end, is_gap)."""
    if len(mask) == 0:
        return []

    runs = []
    in_gap = mask.iloc[0]
    start = 0

    for i in range(1, len(mask)):
        if mask.iloc[i] != in_gap:
            runs.append((start, i, in_gap))
            start = i
            in_gap = mask.iloc[i]

    runs.append((start, len(mask), in_gap))
    return runs


def preprocess_pet_data(
    pet_id: str,
    breed: str,
    age_years: float,
    weight_kg: float,
    fitbark_daily: Optional[list] = None,
    fitbark_hourly: Optional[list] = None,
    whistle_data: Optional[list] = None,
    tractive_data: Optional[list] = None,
) -> ProcessedPetData:
    """Normalize and preprocess data from all sources into unified format."""
    sources = []
    daily_dfs = []

    # Process FitBark daily
    if fitbark_daily:
        df_daily = normalize_fitbark_daily(fitbark_daily)
        if len(df_daily) > 0:
            daily_dfs.append(df_daily)
            sources.append("fitbark")

    # Process hourly if available
    hourly = None
    if fitbark_hourly:
        hourly = normalize_fitbark_hourly(fitbark_hourly)
        if len(hourly) > 0:
            hourly = compute_hourly_features(hourly)
            hourly = fill_missing_hours(hourly)
            sources.append("fitbark_hourly")

    # Combine daily sources
    if daily_dfs:
        daily = daily_dfs[0]
        # Add rolling features
        daily = compute_rolling_features(daily)
    else:
        daily = pd.DataFrame()

    # Detect gaps
    gaps = []
    if len(daily) > 0:
        gaps = detect_gaps(daily["activity_score"] if "activity_score" in daily else daily.index.to_series())

    # Calculate data quality
    data_days = len(daily) if len(daily) > 0 else 0

    quality_score = 1.0
    if data_days > 0:
        expected_points = (daily.index.max() - daily.index.min()).days + 1
        if expected_points > 0:
            quality_score = min(1.0, data_days / expected_points)

    return ProcessedPetData(
        pet_id=pet_id,
        breed=breed,
        age_years=age_years,
        weight_kg=weight_kg,
        daily=daily,
        hourly=hourly,
        data_days_available=data_days,
        data_quality_score=quality_score,
        gaps_detected=gaps,
        sources=sources,
    )
