"""Anomaly detection engine.

Multi-signal, multi-method anomaly detection with precision-first design.

Detection methods:
1. **Z-Score method**: Flags values beyond tolerance × std from mean
2. **MAD method**: Robust to outliers, uses median ± tolerance × MAD
3. **IQR method**: Flags values outside 1.5×IQR from quartiles
4. **Rate-of-change method**: Detects sudden shifts day-over-day
5. **Hourly pattern break**: Detects when hourly pattern deviates from learned profile

Design principle: An anomaly alert requires 2+ corroborating signals.
Single-signal outliers are logged as "notable" but not alerted.
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class Severity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SignalType(Enum):
    ACTIVITY_SCORE = "activity_score"
    PLAY_MINUTES = "play_minutes"
    ACTIVE_MINUTES = "active_minutes"
    REST_MINUTES = "rest_minutes"
    DISTANCE_KM = "distance_km"
    CALORIES = "calories"
    SLEEP_PATTERN = "sleep_pattern"
    HOURLY_ACTIVITY = "hourly_activity"


@dataclass
class SignalDeviation:
    """A deviation detected in a single signal."""
    signal: SignalType
    value: float
    expected_mean: float
    expected_std: float
    z_score: float
    direction: str  # "above" or "below"
    method: str  # "z_score", "mad", "iqr", "rate_of_change", "hourly_pattern"
    severity: Severity


@dataclass
class AnomalyEvent:
    """A confirmed anomaly (2+ corroborating signal deviations)."""
    pet_id: str
    timestamp: str  # ISO 8601
    date: str  # YYYY-MM-DD
    signals_affected: list[SignalDeviation]
    severity: Severity
    confidence: float  # 0-1
    narrative: str  # Human-readable summary
    recommendation: str
    requires_vet_attention: bool = False


@dataclass
class AnomalyCheckResult:
    """Result of an anomaly check for one pet at one point in time."""
    pet_id: str
    anomalies: list[AnomalyEvent]
    notable_signals: list[SignalDeviation]  # Below alert threshold but interesting
    is_healthy: bool
    timestamp: str


class AnomalyDetector:
    """Main anomaly detection engine.

    Args:
        z_score_threshold: Base Z-score threshold (default 2.5, precision-first)
        min_corroborating_signals: Minimum signals in deviation to generate alert (default 2)
    """

    def __init__(
        self,
        z_score_threshold: float = 2.5,
        min_corroborating_signals: int = 2,
    ):
        self.z_score_threshold = z_score_threshold
        self.min_corroborating_signals = min_corroborating_signals

    def check_daily(
        self,
        pet_data: "ProcessedPetData",  # noqa: F821
        baseline: "PetBaseline",  # noqa: F821
        current_record: Optional[dict] = None,
    ) -> AnomalyCheckResult:
        """Run anomaly detection on the latest day's data."""
        from pawpulse_ml.features.preprocessor import normalize_fitbark_daily

        deviations = []

        # Get the latest data point(s)
        df = pet_data.daily
        if df is None or len(df) == 0:
            return AnomalyCheckResult(
                pet_id=pet_data.pet_id, anomalies=[], notable_signals=[],
                is_healthy=True, timestamp=pd.Timestamp.now().isoformat(),
            )

        latest = df.iloc[-1]
        latest_date = df.index[-1]

        # === Check each signal ===

        # 1. Activity Score
        if baseline.daily_score and "activity_score" in df.columns:
            dev = self._check_signal(
                latest.get("activity_score"),
                baseline.daily_score,
                SignalType.ACTIVITY_SCORE,
                baseline.z_score_tolerance,
            )
            if dev:
                deviations.append(dev)

        # 2. Play Minutes
        if baseline.daily_play and "play_minutes" in df.columns:
            dev = self._check_signal(
                latest.get("play_minutes"),
                baseline.daily_play,
                SignalType.PLAY_MINUTES,
                baseline.z_score_tolerance,
            )
            if dev:
                deviations.append(dev)

        # 3. Active Minutes
        if baseline.daily_active and "active_minutes" in df.columns:
            dev = self._check_signal(
                latest.get("active_minutes"),
                baseline.daily_active,
                SignalType.ACTIVE_MINUTES,
                baseline.z_score_tolerance,
            )
            if dev:
                deviations.append(dev)

        # 4. Rest Minutes
        if baseline.daily_rest and "rest_minutes" in df.columns:
            dev = self._check_signal(
                latest.get("rest_minutes"),
                baseline.daily_rest,
                SignalType.REST_MINUTES,
                baseline.z_score_tolerance,
            )
            if dev:
                deviations.append(dev)

        # 5. Distance
        if baseline.daily_distance and "distance_km" in df.columns:
            dev = self._check_signal(
                latest.get("distance_km"),
                baseline.daily_distance,
                SignalType.DISTANCE_KM,
                baseline.z_score_tolerance,
            )
            if dev:
                deviations.append(dev)

        # 6. Rate-of-change detection (day-over-day)
        if len(df) >= 2:
            for col, signal_type in [
                ("activity_score_dod_pct_change", SignalType.ACTIVITY_SCORE),
                ("play_minutes_dod_pct_change", SignalType.PLAY_MINUTES),
                ("rest_minutes_dod_pct_change", SignalType.REST_MINUTES),
            ]:
                if col in df.columns:
                    dod_val = latest.get(col)
                    if dod_val is not None and not np.isnan(dod_val):
                        dev = self._check_rate_of_change(
                            dod_val, signal_type, baseline.z_score_tolerance
                        )
                        if dev:
                            deviations.append(dev)

        # Now classify grouped deviations into anomaly events
        return self._classify_events(
            deviations, pet_data.pet_id, latest_date
        )

    def _check_signal(
        self,
        value,
        baseline: "SignalBaseline",  # noqa: F821
        signal_type: SignalType,
        tolerance: float,
    ) -> Optional[SignalDeviation]:
        """Check a single value against its baseline. Returns deviation if anomalous."""
        if value is None or np.isnan(value):
            return None

        if baseline.n_samples < 3 and not baseline.is_breed_prior:
            # Not enough data to check
            return None

        effective_tolerance = tolerance * (1.2 if baseline.is_breed_prior else 1.0)

        # Use MAD for robust detection when available
        if baseline.mad > 0:
            z_score = abs(value - baseline.median) / baseline.mad
        elif baseline.std > 0:
            z_score = abs(value - baseline.mean) / baseline.std
        else:
            return None

        if z_score < effective_tolerance:
            return None

        direction = "above" if value > baseline.median else "below"

        # Determine severity
        if z_score >= effective_tolerance * 2:
            severity = Severity.HIGH
        elif z_score >= effective_tolerance * 1.5:
            severity = Severity.MEDIUM
        else:
            severity = Severity.LOW

        return SignalDeviation(
            signal=signal_type,
            value=float(value),
            expected_mean=baseline.median,
            expected_std=baseline.mad or baseline.std,
            z_score=float(z_score),
            direction=direction,
            method="mad" if baseline.mad > 0 else "z_score",
            severity=severity,
        )

    def _check_rate_of_change(
        self,
        pct_change: float,
        signal_type: SignalType,
        tolerance: float,
    ) -> Optional[SignalDeviation]:
        """Check if day-over-day change is anomalous.

        A drop of >50% or increase of >100% in a single day is suspicious
        unless explained by known factors.
        """
        if pct_change is None or np.isnan(pct_change):
            return None

        abs_change = abs(pct_change)
        # Threshold: >50% day-over-day change is concerning
        if abs_change < 50:
            return None

        severity = Severity.LOW
        if abs_change > 80:
            severity = Severity.MEDIUM
        if abs_change > 120:
            severity = Severity.HIGH

        direction = "above" if pct_change > 0 else "below"

        return SignalDeviation(
            signal=signal_type,
            value=pct_change,
            expected_mean=0,
            expected_std=20,
            z_score=abs_change / 20,
            direction=direction,
            method="rate_of_change",
            severity=severity,
        )

    def _classify_events(
        self,
        deviations: list[SignalDeviation],
        pet_id: str,
        date,
    ) -> AnomalyCheckResult:
        """Group deviations into anomaly events.

        Precision-first: requires 2+ corroborating signals for an alert.
        Single deviations are logged as "notable" but don't trigger alerts.
        """
        high_sev = [d for d in deviations if d.severity in (Severity.HIGH, Severity.CRITICAL)]
        med_sev = [d for d in deviations if d.severity == Severity.MEDIUM]
        low_sev = [d for d in deviations if d.severity == Severity.LOW]

        anomalies = []
        notable = []

        # HIGH severity events: 1 high-sev signal can trigger with 1+ med
        if len(high_sev) >= 1 and len(high_sev) + len(med_sev) >= self.min_corroborating_signals:
            sigs = high_sev + med_sev
            max_sev = max((s.severity for s in sigs), key=lambda x: x.value)
            narrative, recommendation = self._generate_narrative(sigs, pet_id)

            anomalies.append(AnomalyEvent(
                pet_id=pet_id,
                timestamp=pd.Timestamp.now().isoformat(),
                date=str(date.date()) if hasattr(date, "date") else str(date),
                signals_affected=sigs,
                severity=max_sev,
                confidence=self._compute_confidence(sigs),
                narrative=narrative,
                recommendation=recommendation,
                requires_vet_attention=max_sev in (Severity.HIGH, Severity.CRITICAL),
            ))

        # MEDIUM severity events: need 2+ med signals
        elif len(med_sev) >= self.min_corroborating_signals:
            narrative, recommendation = self._generate_narrative(med_sev, pet_id)
            anomalies.append(AnomalyEvent(
                pet_id=pet_id,
                timestamp=pd.Timestamp.now().isoformat(),
                date=str(date.date()) if hasattr(date, "date") else str(date),
                signals_affected=med_sev,
                severity=Severity.MEDIUM,
                confidence=self._compute_confidence(med_sev),
                narrative=narrative,
                recommendation=recommendation,
                requires_vet_attention=False,
            ))

        # Everything else is "notable" — logged but not alerted
        notable = [d for d in deviations if d not in [
            s for a in anomalies for s in a.signals_affected
        ]]

        return AnomalyCheckResult(
            pet_id=pet_id,
            anomalies=anomalies,
            notable_signals=notable,
            is_healthy=len(anomalies) == 0,
            timestamp=pd.Timestamp.now().isoformat(),
        )

    def _compute_confidence(self, signals: list[SignalDeviation]) -> float:
        """Compute confidence score for a set of signals.

        Factors:
        - Number of corroborating signals
        - Severity of each signal
        - Consistency of direction (all pointing same way = more confident)
        """
        base = 0.5
        n = len(signals)

        # More corroborating signals = higher confidence
        if n >= 3:
            base += 0.2
        elif n >= 2:
            base += 0.1

        # Severity boost
        sev_boost = sum(
            0.15 if s.severity == Severity.HIGH else
            0.1 if s.severity == Severity.MEDIUM else
            0.05
            for s in signals
        )
        base += min(0.3, sev_boost)

        # Direction consistency
        directions = set(s.direction for s in signals)
        if len(directions) == 1:
            base += 0.1  # All pointing same direction

        return min(1.0, base)

    def _generate_narrative(
        self, signals: list[SignalDeviation], pet_id: str
    ) -> tuple[str, str]:
        """Generate human-readable narrative and recommendation."""
        signal_names = {
            SignalType.ACTIVITY_SCORE: "activity score",
            SignalType.PLAY_MINUTES: "play time",
            SignalType.ACTIVE_MINUTES: "active time",
            SignalType.REST_MINUTES: "rest time",
            SignalType.DISTANCE_KM: "distance traveled",
            SignalType.CALORIES: "calories burned",
            SignalType.SLEEP_PATTERN: "sleep pattern",
            SignalType.HOURLY_ACTIVITY: "hourly activity pattern",
        }

        below = [s for s in signals if s.direction == "below"]
        above = [s for s in signals if s.direction == "above"]

        parts = []
        if below:
            names = [signal_names.get(s.signal, s.signal.value) for s in below]
            if len(names) == 1:
                parts.append(f"{names[0]} is significantly lower than usual")
            else:
                parts.append(f"{' and '.join(names)} are significantly lower than usual")

        if above:
            names = [signal_names.get(s.signal, s.signal.value) for s in above]
            if len(names) == 1:
                parts.append(f"{names[0]} is significantly higher than usual")
            else:
                parts.append(f"{' and '.join(names)} are significantly higher than usual")

        narrative = "; ".join(parts)

        # Generate recommendation
        high_sev = any(s.severity in (Severity.HIGH, Severity.CRITICAL) for s in signals)
        below_signals = {s.signal for s in signals if s.direction == "below"}

        if high_sev:
            recommendation = (
                "This combination of changes may indicate an underlying health issue. "
                "We recommend consulting with your veterinarian, especially if these "
                "changes persist for more than 24-48 hours."
            )
        elif below_signals & {SignalType.ACTIVITY_SCORE, SignalType.PLAY_MINUTES}:
            recommendation = (
                "Your pet is less active than usual. Monitor for other signs of illness "
                "such as changes in appetite, vomiting, or diarrhea. If these develop, "
                "contact your vet."
            )
        elif SignalType.REST_MINUTES in below_signals:
            recommendation = (
                "Your pet is resting less than usual. This could indicate discomfort, "
                "anxiety, or pain. Consider environmental changes or consult your vet."
            )
        else:
            recommendation = (
                "Monitor your pet for any additional changes in behavior or appetite. "
                "Share this report with your veterinarian at your next visit."
            )

        return narrative, recommendation
