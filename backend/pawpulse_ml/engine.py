"""PawPulse ML Engine — Main orchestrator.

Ties together baseline learning, anomaly detection, trend prediction,
and output formatting into a single, fast inference pipeline.

Usage:
    from pawpulse_ml.engine import PawPulseEngine

    engine = PawPulseEngine()
    result = engine.check_pet(
        pet_id="abc123",
        breed="Labrador Retriever",
        age_years=4.5,
        weight_kg=30.0,
        fitbark_daily=[...],
    )

Performance: < 500ms per pet per check (typical: 50-150ms).
"""

import time
import logging
from typing import Optional

from pawpulse_ml.features.preprocessor import preprocess_pet_data, ProcessedPetData
from pawpulse_ml.baseline.learner import compute_baseline, PetBaseline
from pawpulse_ml.detectors.anomaly import AnomalyDetector, AnomalyCheckResult
from pawpulse_ml.detectors.trends import compute_trend_report, TrendReport
from pawpulse_ml.output.formatter import format_health_summary

logger = logging.getLogger("pawpulse_ml")


class PawPulseEngine:
    """Main anomaly detection engine.

    Performs baseline learning, anomaly detection, and trend analysis
    for pet health monitoring.

    Args:
        z_score_threshold: Base threshold for anomaly detection (default 2.5)
        min_corroborating_signals: Min signals needed for alert (default 2)
        enable_trends: Whether to compute trendlines (Premium feature)
    """

    def __init__(
        self,
        z_score_threshold: float = 2.5,
        min_corroborating_signals: int = 2,
        enable_trends: bool = True,
    ):
        self.detector = AnomalyDetector(
            z_score_threshold=z_score_threshold,
            min_corroborating_signals=min_corroborating_signals,
        )
        self.enable_trends = enable_trends
        self._baseline_cache: dict[str, PetBaseline] = {}

    def check_pet(
        self,
        pet_id: str,
        breed: str,
        age_years: float,
        weight_kg: float,
        fitbark_daily: Optional[list] = None,
        fitbark_hourly: Optional[list] = None,
        whistle_data: Optional[list] = None,
        tractive_data: Optional[list] = None,
        tier: str = "basic",
        force_rebaseline: bool = False,
    ) -> dict:
        """Run the full detection pipeline for a single pet.

        Args:
            pet_id: Unique identifier for the pet
            breed: Breed name (for breed-aware prior)
            age_years: Pet's age in years
            weight_kg: Pet's weight in kg
            fitbark_daily: List of FitBark ActivityDaily records
            fitbark_hourly: List of FitBark ActivityHourly records
            whistle_data: List of Whistle data records
            tractive_data: List of Tractive data records
            tier: Subscription tier ("basic", "premium", "pro")
            force_rebaseline: Force recomputation of baseline

        Returns:
            dict: Structured JSON response for the API
        """
        start_time = time.time()

        # Step 1: Preprocess data (normalize, fill gaps, compute features)
        processed = preprocess_pet_data(
            pet_id=pet_id,
            breed=breed,
            age_years=age_years,
            weight_kg=weight_kg,
            fitbark_daily=fitbark_daily,
            fitbark_hourly=fitbark_hourly,
            whistle_data=whistle_data,
            tractive_data=tractive_data,
        )

        # Step 2: Compute/retrieve baseline
        if force_rebaseline or pet_id not in self._baseline_cache:
            baseline = compute_baseline(processed)
            self._baseline_cache[pet_id] = baseline
        else:
            baseline = self._baseline_cache[pet_id]

        # Step 3: Run anomaly detection
        anomaly_result = self.detector.check_daily(processed, baseline)

        # Step 4: Compute trends (Premium+)
        trend_report = TrendReport(
            pet_id=pet_id, trendlines=[], overall_health_trend="stable",
            data_sufficient=False, warning_flags=[],
        )
        if self.enable_trends and processed.daily is not None and len(processed.daily) >= 7:
            trend_report = compute_trend_report(pet_id, processed.daily, baseline)

        # Step 5: Format output
        result = format_health_summary(
            pet_id=pet_id,
            baseline=baseline,
            anomaly_result=anomaly_result,
            trend_report=trend_report,
            tier=tier,
        )

        # Add performance metadata
        elapsed_ms = (time.time() - start_time) * 1000
        result["_performance_ms"] = round(elapsed_ms, 1)

        logger.info(
            "Pet %s: %s (%.0fms, %d days data, %d anomalies, tier=%s)",
            pet_id,
            "healthy" if anomaly_result.is_healthy else f"{len(anomaly_result.anomalies)} anomaly/ies",
            elapsed_ms,
            processed.data_days_available,
            len(anomaly_result.anomalies),
            tier,
        )

        return result

    def get_baseline(self, pet_id: str) -> Optional[PetBaseline]:
        """Retrieve cached baseline for a pet."""
        return self._baseline_cache.get(pet_id)

    def clear_cache(self, pet_id: Optional[str] = None):
        """Clear baseline cache for one or all pets."""
        if pet_id:
            self._baseline_cache.pop(pet_id, None)
        else:
            self._baseline_cache.clear()

    def get_stats(self) -> dict:
        """Return engine statistics."""
        return {
            "cached_baselines": len(self._baseline_cache),
            "pets": list(self._baseline_cache.keys()),
        }
