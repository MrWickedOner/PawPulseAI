"""PawPulse ML — Pet Health Anomaly Detection Engine.

Detects health anomalies from pet wearable data (FitBark, Whistle, Tractive)
by learning individual baselines and surfacing deviations before symptoms appear.

Design principles:
- Precision-first: minimize false positives (#1 risk for pet owners)
- Multi-signal corroboration: an alert requires 2+ signals deviating together
- Breed-aware personalization: Greyhound ≠ Bulldog
- Sparse data tolerant: handles irregular sampling gracefully
"""
__version__ = "0.1.0"
