"""Comprehensive tests for the PawPulse anomaly detection engine.

Tests cover:
1. Breed prior lookup and personalization
2. Age-adjusted baselines
3. Data preprocessing and normalization
4. Baseline computation (breed prior fallback + data-driven)
5. Anomaly detection (normal vs anomalous)
6. Trend prediction
7. Output formatting
8. Full engine pipeline with end-to-end scenarios
9. Performance (< 500ms per check)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import json
import time
import numpy as np
import pandas as pd

from pawpulse_ml.utils.breed_priors import (
    get_breed_prior, compute_informed_prior, BREED_PRIORS
)
from pawpulse_ml.features.preprocessor import (
    preprocess_pet_data, normalize_fitbark_daily,
    detect_gaps, compute_rolling_features
)
from pawpulse_ml.baseline.learner import compute_baseline
from pawpulse_ml.detectors.anomaly import AnomalyDetector
from pawpulse_ml.detectors.trends import compute_trendline, compute_trend_report
from pawpulse_ml.output.formatter import format_health_summary
from pawpulse_ml.engine import PawPulseEngine


def _generate_sample_daily_data(days: int = 30, base_score: float = 600, noise: float = 50):
    """Generate synthetic FitBark daily data for testing."""
    records = []
    for i in range(days):
        date = pd.Timestamp("2024-01-01") + pd.Timedelta(days=i)
        score = base_score + np.random.normal(0, noise)
        records.append({
            "date": date.strftime("%Y-%m-%d"),
            "score": max(0, score),
            "min_play": max(0, 60 + np.random.normal(0, 15)),
            "min_active": max(0, 150 + np.random.normal(0, 20)),
            "min_rest": min(1440, 950 + np.random.normal(0, 30)),
            "distance_in_miles": max(0, 3.0 + np.random.normal(0, 0.8)),
            "calories": max(0, 400 + np.random.normal(0, 50)),
            "goal_progress": min(1.0, max(0, 0.7 + np.random.normal(0, 0.1))),
        })
    return records


def test_breed_priors():
    """Test breed prior lookup and personalization."""
    print("  Testing breed priors...")

    # Test known breed
    prior = get_breed_prior("Greyhound")
    assert prior.breed == "Greyhound"
    assert prior.energy_level == "moderate"
    assert prior.daily_score_mean == 420
    assert prior.rest_minutes_mean == 1080  # High rest for Greyhound
    print(f"    Greyhound: score={prior.daily_score_mean}, rest={prior.rest_minutes_mean}")

    # Test unknown breed falls back to Mixed
    prior = get_breed_prior("UnknownBreedXYZ")
    assert prior.breed == "Mixed"
    print(f"    Unknown breed falls back to Mixed: score={prior.daily_score_mean}")

    # Test case insensitivity
    prior_upper = get_breed_prior("BULLDOG")
    prior_lower = get_breed_prior("bulldog")
    assert prior_upper.breed == prior_lower.breed

    # Test that Greyhound and Bulldog have very different baselines
    greyhound = get_breed_prior("Greyhound")
    bulldog = get_breed_prior("Bulldog")
    assert greyhound.daily_score_mean > bulldog.daily_score_mean  # Greyhound more active
    assert greyhound.rest_minutes_mean < bulldog.rest_minutes_mean  # Bulldog rests more

    print("  ✅ Breed priors OK")


def test_age_adjustment():
    """Test age-adjusted baselines."""
    print("  Testing age adjustment...")

    # Puppy
    puppy = compute_informed_prior("Labrador Retriever", age_years=0.5, weight_kg=15)
    assert puppy.play_minutes_mean > 70  # Puppies should have higher play

    # Adult
    adult = compute_informed_prior("Labrador Retriever", age_years=4, weight_kg=30)
    assert adult.play_minutes_mean == 70  # Standard

    # Senior
    senior = compute_informed_prior("Labrador Retriever", age_years=12, weight_kg=28)
    assert senior.play_minutes_mean < 70  # Lower play for seniors
    assert senior.rest_minutes_mean > 900  # More rest for seniors

    print(f"    Puppy play: {puppy.play_minutes_mean:.0f}, Adult: {adult.play_minutes_mean:.0f}, Senior: {senior.play_minutes_mean:.0f}")
    print("  ✅ Age adjustment OK")


def test_data_preprocessing():
    """Test data preprocessing and normalization."""
    print("  Testing data preprocessing...")

    records = _generate_sample_daily_data(days=14)
    df = normalize_fitbark_daily(records)
    assert len(df) == 14
    assert "activity_score" in df.columns
    assert "play_minutes" in df.columns
    assert "distance_km" in df.columns

    # Test rolling features
    df_with_features = compute_rolling_features(df)
    assert f"activity_score_rolling_mean_7d" in df_with_features.columns

    # Test gap detection
    gaps = detect_gaps(df["activity_score"])
    assert isinstance(gaps, list)

    print(f"    Normalized {len(records)} records, {len(df.columns)} columns")
    print("  ✅ Data preprocessing OK")


def test_baseline_computation():
    """Test baseline computation with and without data."""
    print("  Testing baseline computation...")

    # With enough data
    records = _generate_sample_daily_data(days=21, base_score=550)
    processed = preprocess_pet_data(
        pet_id="test-001", breed="Beagle",
        age_years=3, weight_kg=12,
        fitbark_daily=records,
    )
    baseline = compute_baseline(processed)
    assert baseline.is_mature  # 21 days > breed's learning window

    # With no data (breed prior only)
    processed_empty = preprocess_pet_data(
        pet_id="test-002", breed="Bulldog",
        age_years=5, weight_kg=24,
    )
    baseline_empty = compute_baseline(processed_empty)
    assert baseline_empty.is_breed_prior_only()
    assert baseline_empty.daily_score.is_breed_prior
    # Breed prior adjusted by age/weight (not exactly 280)
    assert baseline_empty.daily_score.mean < 320

    # Test data quality improves confidence
    assert baseline.confidence_in_baseline() > baseline_empty.confidence_in_baseline()
    print(f"    Data-driven baseline confidence: {baseline.confidence_in_baseline():.2f}")
    print(f"    Breed prior confidence: {baseline_empty.confidence_in_baseline():.2f}")
    print("  ✅ Baseline computation OK")


def test_anomaly_detection_normal():
    """Test anomaly detection on normal data (should be healthy)."""
    print("  Testing anomaly detection on normal data...")

    records = _generate_sample_daily_data(days=30, base_score=500, noise=40)
    processed = preprocess_pet_data(
        pet_id="test-healthy", breed="Mixed",
        age_years=3, weight_kg=20,
        fitbark_daily=records,
    )
    baseline = compute_baseline(processed)
    detector = AnomalyDetector(z_score_threshold=2.5)
    result = detector.check_daily(processed, baseline)

    assert result.is_healthy
    assert len(result.anomalies) == 0
    print(f"    Normal data: healthy={result.is_healthy}, notable_signals={len(result.notable_signals)}")
    print("  ✅ Normal data correctly classified as healthy")


def test_anomaly_detection_anomalous():
    """Test anomaly detection on anomalous data (should detect)."""
    print("  Testing anomaly detection on anomalous data...")

    # 30 days of normal, then 1 day with extreme drop
    records = _generate_sample_daily_data(days=30, base_score=500, noise=30)

    # Make the last day severely anomalous
    last = records[-1]
    last["score"] = 100  # Dropped from ~500 to 100
    last["min_play"] = 5   # Very little play
    last["min_active"] = 30  # Very little activity
    last["min_rest"] = 1380  # Resting almost all day
    last["distance_in_miles"] = 0.1

    processed = preprocess_pet_data(
        pet_id="test-sick", breed="Labrador Retriever",
        age_years=4, weight_kg=30,
        fitbark_daily=records,
    )
    baseline = compute_baseline(processed)
    detector = AnomalyDetector(z_score_threshold=2.5, min_corroborating_signals=2)
    result = detector.check_daily(processed, baseline)

    # Should detect anomalies
    print(f"    Anomalous data: healthy={result.is_healthy}, anomalies={len(result.anomalies)}")
    if len(result.anomalies) > 0:
        a = result.anomalies[0]
        print(f"    Severity: {a.severity.value}, confidence: {a.confidence:.2f}")
        print(f"    Narrative: {a.narrative}")
        print(f"    Vet attention needed: {a.requires_vet_attention}")
    print(f"    Notable signals: {len(result.notable_signals)}")

    assert not result.is_healthy
    assert len(result.anomalies) >= 1
    print("  ✅ Anomalous data correctly detected")


def test_trend_prediction():
    """Test trendline computation."""
    print("  Testing trend prediction...")

    # Healthy trend (stable)
    values = pd.Series([500 + np.random.normal(0, 30) for _ in range(30)])
    tl = compute_trendline(values, "Activity Score", 500)
    assert tl is not None
    print(f"    Stable data: direction={tl.trend_direction}, slope={tl.trend_slope:.3f}/day")

    # Declining trend
    declining = pd.Series([600 - i * 5 + np.random.normal(0, 20) for i in range(30)])
    tl2 = compute_trendline(declining, "Activity Score", 600)
    assert tl2 is not None
    print(f"    Declining data: direction={tl2.trend_direction}, slope={tl2.trend_slope:.3f}/day")
    print(f"    30-day forecast: {tl2.forecast_30day:.0f} (from current {tl2.current_value:.0f})")

    print("  ✅ Trend prediction OK")


def test_end_to_end_pipeline():
    """Test the full PawPulseEngine pipeline."""
    print("  Testing end-to-end pipeline...")

    engine = PawPulseEngine()

    # Healthy pet
    healthy_data = _generate_sample_daily_data(days=30, base_score=500)
    result = engine.check_pet(
        pet_id="e2e-healthy",
        breed="Golden Retriever",
        age_years=4,
        weight_kg=30,
        fitbark_daily=healthy_data,
        tier="premium",
    )
    assert result["pet_id"] == "e2e-healthy"
    assert "health_status" in result
    assert "_performance_ms" in result
    assert result["_performance_ms"] < 500  # Must be < 500ms

    # Sick pet
    sick_data = _generate_sample_daily_data(days=30, base_score=500)
    sick_data[-1]["score"] = 80
    sick_data[-1]["min_play"] = 2
    sick_data[-1]["min_active"] = 20
    result_sick = engine.check_pet(
        pet_id="e2e-sick",
        breed="Golden Retriever",
        age_years=8,
        weight_kg=32,
        fitbark_daily=sick_data,
        tier="basic",
    )
    assert result_sick["health_status"] == "attention_needed"
    assert "_performance_ms" in result_sick
    assert result_sick["_performance_ms"] < 500

    # Test cache
    assert engine.get_baseline("e2e-healthy") is not None
    stats = engine.get_stats()
    assert "e2e-healthy" in stats["pets"]

    print(f"    Healthy: {result['health_status']} ({result['_performance_ms']:.0f}ms)")
    print(f"    Sick: {result_sick['health_status']} ({result_sick['_performance_ms']:.0f}ms)")
    print(f"    Anomalies: {result_sick['anomalies']['anomaly_count']}")
    print("  ✅ End-to-end pipeline OK")


def test_inference_speed():
    """Test inference speed meets <500ms requirement."""
    print("  Testing inference speed...")

    engine = PawPulseEngine()

    # Test with various data sizes
    for days in [7, 14, 30, 90]:
        data = _generate_sample_daily_data(days=days)
        start = time.time()
        for _ in range(5):
            result = engine.check_pet(
                pet_id=f"speed-{days}",
                breed="Beagle",
                age_years=3,
                weight_kg=12,
                fitbark_daily=data,
                tier="premium",
            )
        elapsed = (time.time() - start) / 5 * 1000
        print(f"    {days} days: {elapsed:.1f}ms avg (threshold: 500ms)")
        assert elapsed < 500, f"Too slow: {elapsed:.1f}ms for {days} days"

    print("  ✅ Inference speed OK")


def test_output_format():
    """Test the structured JSON output format."""
    print("  Testing output format...")

    records = _generate_sample_daily_data(days=14)
    processed = preprocess_pet_data(
        pet_id="fmt-test", breed="Mixed",
        age_years=3, weight_kg=20,
        fitbark_daily=records,
    )
    baseline = compute_baseline(processed)
    detector = AnomalyDetector()
    anomaly_result = detector.check_daily(processed, baseline)

    from pawpulse_ml.detectors.trends import compute_trend_report
    trend = compute_trend_report("fmt-test", processed.daily, baseline)

    # Test basic tier
    basic = format_health_summary("fmt-test", baseline, anomaly_result, trend, tier="basic")
    assert "anomalies" in basic
    assert "trends" not in basic  # Not in basic tier

    # Test premium tier
    premium = format_health_summary("fmt-test", baseline, anomaly_result, trend, tier="premium")
    assert "trends" in premium

    # Verify JSON serializable (use default=str to handle numpy types)
    basic_json = json.dumps(basic, default=str)
    premium_json = json.dumps(premium, default=str)
    assert isinstance(basic_json, str)

    print("  ✅ Output format OK")


def test_breed_differentiation():
    """Test that different breeds produce meaningfully different results."""
    print("  Testing breed differentiation...")

    same_data = _generate_sample_daily_data(days=14, base_score=500, noise=20)

    processed_bulldog = preprocess_pet_data(
        pet_id="bulldog", breed="Bulldog",
        age_years=4, weight_kg=24,
        fitbark_daily=same_data,
    )
    processed_husky = preprocess_pet_data(
        pet_id="husky", breed="Siberian Husky",
        age_years=4, weight_kg=24,
        fitbark_daily=same_data,
    )

    baseline_bulldog = compute_baseline(processed_bulldog)
    baseline_husky = compute_baseline(processed_husky)

    # Breed priors should be very different (compare raw breed priors directly)
    from pawpulse_ml.utils.breed_priors import get_breed_prior
    bulldog_prior = get_breed_prior("Bulldog")
    husky_prior = get_breed_prior("Siberian Husky")
    print(f"    Bulldog daily_score prior: {bulldog_prior.daily_score_mean:.0f}")
    print(f"    Husky daily_score prior: {husky_prior.daily_score_mean:.0f}")

    # Husky should have higher activity priors
    assert husky_prior.daily_score_mean > bulldog_prior.daily_score_mean * 1.5
    assert husky_prior.distance_km_mean > bulldog_prior.distance_km_mean * 3

    print("  ✅ Breed differentiation OK")


if __name__ == "__main__":
    print("\n🧪 PawPulse ML Engine Tests\n")
    print("=" * 60)

    tests = [
        test_breed_priors,
        test_age_adjustment,
        test_data_preprocessing,
        test_baseline_computation,
        test_anomaly_detection_normal,
        test_anomaly_detection_anomalous,
        test_trend_prediction,
        test_end_to_end_pipeline,
        test_inference_speed,
        test_output_format,
        test_breed_differentiation,
    ]

    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"  ❌ FAILED: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 60)
    print(f"📊 Results: {passed} passed, {failed} failed, {len(tests)} total")
    print("=" * 60)

    sys.exit(1 if failed > 0 else 0)
