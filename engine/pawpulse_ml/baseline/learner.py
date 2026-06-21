"""Baseline learning system.

Learns each pet's unique behavioral and physiological baselines from
historical data. Supports both breed-informed priors and individual
learning with progressive refinement.

Key design decisions:
- Rolling statistical baselines (mean ± std) that adapt to gradual change
- Separate baselines for: daily patterns, hourly patterns, day-of-week
- Breed prior seeding for pets with <14 days of data
- Age-adjusted baselines for puppies and seniors
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import Optional

from pawpulse_ml.utils.breed_priors import compute_informed_prior, BreedPrior
from pawpulse_ml.features.preprocessor import ProcessedPetData


@dataclass
class SignalBaseline:
    """Statistical baseline for a single signal/metric."""
    mean: float
    std: float
    median: float
    mad: float  # Median Absolute Deviation (robust)
    p5: float   # 5th percentile
    p25: float  # 25th percentile
    p75: float  # 75th percentile
    p95: float  # 95th percentile
    n_samples: int
    is_breed_prior: bool = False  # True if this is a seeded prior, not from data


@dataclass
class HourlyPatternBaseline:
    """Hourly pattern baseline — typical values for each hour of day."""
    hourly_means: dict[int, float]  # hour -> mean
    hourly_stds: dict[int, float]
    hourly_mads: dict[int, float]


@dataclass
class PetBaseline:
    """Complete baseline for one pet."""
    pet_id: str
    breed: str
    age_years: float
    weight_kg: float
    breed_prior: BreedPrior

    # Daily baselines
    daily_score: Optional[SignalBaseline] = None
    daily_play: Optional[SignalBaseline] = None
    daily_active: Optional[SignalBaseline] = None
    daily_rest: Optional[SignalBaseline] = None
    daily_distance: Optional[SignalBaseline] = None
    daily_calories: Optional[SignalBaseline] = None

    # Hourly patterns
    hourly_play: Optional[HourlyPatternBaseline] = None
    hourly_active: Optional[HourlyPatternBaseline] = None
    hourly_rest: Optional[HourlyPatternBaseline] = None

    # Day-of-week effects
    dow_means: dict[int, float] = field(default_factory=dict)

    # Metadata
    data_days_used: int = 0
    is_mature: bool = False  # Has enough data for reliable detection
    z_score_tolerance: float = 2.5

    def confidence_in_baseline(self) -> float:
        """Return confidence score for this baseline (0-1)."""
        if self.is_breed_prior_only():
            return 0.3  # Low confidence without individual data
        if not self.is_mature:
            return 0.5 + (self.data_days_used / 28) * 0.3  # Scaling up
        return min(1.0, 0.8 + (self.data_days_used / 90) * 0.2)

    def is_breed_prior_only(self) -> bool:
        """True if we're still using only breed prior (no individual data)."""
        return self.data_days_used == 0


def _compute_signal_baseline(values: pd.Series) -> SignalBaseline:
    """Compute robust signal baseline from a series of values."""
    values = values.dropna()
    if len(values) < 3:
        # Can't compute reliable stats
        if len(values) > 0:
            return SignalBaseline(
                mean=float(values.mean()), std=float(values.std() or 1.0),
                median=float(values.median()), mad=1.0,
                p5=float(values.quantile(0.05)), p25=float(values.quantile(0.25)),
                p75=float(values.quantile(0.75)), p95=float(values.quantile(0.95)),
                n_samples=len(values),
            )
        return SignalBaseline(mean=0, std=1, median=0, mad=1, p5=0, p25=0, p75=0, p95=0, n_samples=0)

    median = float(values.median())
    mad = float(np.median(np.abs(values - median))) or 1.0

    return SignalBaseline(
        mean=float(values.mean()),
        std=float(values.std()),
        median=median,
        mad=mad,
        p5=float(values.quantile(0.05)),
        p25=float(values.quantile(0.25)),
        p75=float(values.quantile(0.75)),
        p95=float(values.quantile(0.95)),
        n_samples=len(values),
    )


def _compute_hourly_baseline(df: pd.DataFrame, col: str) -> HourlyPatternBaseline:
    """Compute hourly pattern baseline from hourly data."""
    if df is None or len(df) == 0 or col not in df.columns:
        return HourlyPatternBaseline(hourly_means={}, hourly_stds={}, hourly_mads={})

    hourly_means = {}
    hourly_stds = {}
    hourly_mads = {}

    for hour in range(24):
        hour_data = df[df["hour"] == hour][col].dropna()
        if len(hour_data) >= 3:
            hourly_means[hour] = float(hour_data.mean())
            hourly_stds[hour] = float(hour_data.std())
            hourly_mads[hour] = float(np.median(np.abs(hour_data - hour_data.median())))
        elif len(hour_data) > 0:
            hourly_means[hour] = float(hour_data.mean())
            hourly_stds[hour] = float(hour_data.std() or 1.0)
            hourly_mads[hour] = 1.0

    return HourlyPatternBaseline(
        hourly_means=hourly_means,
        hourly_stds=hourly_stds,
        hourly_mads=hourly_mads,
    )


def compute_baseline(data: ProcessedPetData) -> PetBaseline:
    """Compute complete pet baseline from processed data.

    Combines breed-informed priors with individual data.
    Uses the breed prior when individual data is insufficient.
    """
    prior = compute_informed_prior(data.breed, data.age_years, data.weight_kg)

    baseline = PetBaseline(
        pet_id=data.pet_id,
        breed=data.breed,
        age_years=data.age_years,
        weight_kg=data.weight_kg,
        breed_prior=prior,
        z_score_tolerance=prior.z_score_tolerance(),
        data_days_used=data.data_days_available,
    )

    # Check if we have enough data for mature baseline
    min_days = prior.learning_window_days()
    baseline.is_mature = data.data_days_available >= min_days

    df = data.daily

    # === Daily Score Baseline ===
    if df is not None and "activity_score" in df.columns and len(df) >= 3:
        baseline.daily_score = _compute_signal_baseline(df["activity_score"])
    else:
        baseline.daily_score = SignalBaseline(
            mean=prior.daily_score_mean, std=prior.daily_score_std,
            median=prior.daily_score_mean, mad=prior.daily_score_std * 0.8,
            p5=prior.daily_score_mean - 2 * prior.daily_score_std,
            p25=prior.daily_score_mean - prior.daily_score_std,
            p75=prior.daily_score_mean + prior.daily_score_std,
            p95=prior.daily_score_mean + 2 * prior.daily_score_std,
            n_samples=0, is_breed_prior=True,
        )

    # === Play Minutes Baseline ===
    if df is not None and "play_minutes" in df.columns and len(df) >= 3:
        baseline.daily_play = _compute_signal_baseline(df["play_minutes"])
    else:
        baseline.daily_play = SignalBaseline(
            mean=prior.play_minutes_mean, std=prior.play_minutes_mean * 0.4,
            median=prior.play_minutes_mean, mad=prior.play_minutes_mean * 0.3,
            p25=max(0, prior.play_minutes_mean * 0.5),
            p75=prior.play_minutes_mean * 1.5,
            p5=max(0, prior.play_minutes_mean * 0.2),
            p95=prior.play_minutes_mean * 2.0,
            n_samples=0, is_breed_prior=True,
        )

    # === Active Minutes Baseline ===
    if df is not None and "active_minutes" in df.columns and len(df) >= 3:
        baseline.daily_active = _compute_signal_baseline(df["active_minutes"])
    else:
        baseline.daily_active = SignalBaseline(
            mean=prior.active_minutes_mean, std=prior.active_minutes_mean * 0.35,
            median=prior.active_minutes_mean, mad=prior.active_minutes_mean * 0.25,
            p5=max(0, prior.active_minutes_mean * 0.3),
            p25=prior.active_minutes_mean * 0.7,
            p75=prior.active_minutes_mean * 1.3,
            p95=prior.active_minutes_mean * 1.7,
            n_samples=0, is_breed_prior=True,
        )

    # === Rest Minutes Baseline ===
    if df is not None and "rest_minutes" in df.columns and len(df) >= 3:
        baseline.daily_rest = _compute_signal_baseline(df["rest_minutes"])
    else:
        baseline.daily_rest = SignalBaseline(
            mean=prior.rest_minutes_mean, std=prior.rest_minutes_mean * 0.1,
            median=prior.rest_minutes_mean, mad=prior.rest_minutes_mean * 0.08,
            p5=prior.rest_minutes_mean * 0.85,
            p25=prior.rest_minutes_mean * 0.93,
            p75=prior.rest_minutes_mean * 1.07,
            p95=prior.rest_minutes_mean * 1.15,
            n_samples=0, is_breed_prior=True,
        )

    # === Distance Baseline ===
    if df is not None and "distance_km" in df.columns and len(df) >= 3:
        baseline.daily_distance = _compute_signal_baseline(df["distance_km"])
    else:
        baseline.daily_distance = SignalBaseline(
            mean=prior.distance_km_mean, std=prior.distance_km_std,
            median=prior.distance_km_mean, mad=prior.distance_km_std * 0.7,
            p5=max(0, prior.distance_km_mean * 0.1),
            p25=prior.distance_km_mean * 0.5,
            p75=prior.distance_km_mean * 1.5,
            p95=prior.distance_km_mean * 2.5,
            n_samples=0, is_breed_prior=True,
        )

    # === Hourly patterns (only from actual data) ===
    if data.hourly is not None and len(data.hourly) > 0:
        baseline.hourly_play = _compute_hourly_baseline(data.hourly, "play_minutes")
        baseline.hourly_active = _compute_hourly_baseline(data.hourly, "active_minutes")
        baseline.hourly_rest = _compute_hourly_baseline(data.hourly, "rest_minutes")

    # === Day-of-week effects ===
    if df is not None and "activity_score" in df.columns:
        dow_means = {}
        for dow in range(7):
            dow_data = df[df.index.dayofweek == dow]["activity_score"].dropna()
            if len(dow_data) >= 2:
                dow_means[dow] = float(dow_data.mean())
        baseline.dow_means = dow_means

    return baseline
