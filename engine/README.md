# PawPulse Anomaly Detection Engine

Python ML engine for detecting pet health anomalies from FitBark, Whistle, and Tractive wearable data.

## Quick Start

```bash
cd /home/team/shared/anomaly-engine
pip install -e .    # Install in development mode
```

Or install from the shared directory:
```bash
pip install /home/team/shared/anomaly-engine
```

## Usage

### Python API (for backend integration)

```python
from pawpulse_ml.engine import PawPulseEngine

engine = PawPulseEngine()

# Run anomaly check for one pet
result = engine.check_pet(
    pet_id="abc-123",
    breed="Labrador Retriever",    # Use breed name from breed priors
    age_years=4.5,
    weight_kg=30.0,
    fitbark_daily=[
        {
            "date": "2024-01-01",
            "score": 650,
            "min_play": 60,
            "min_active": 180,
            "min_rest": 900,
            "distance_in_miles": 3.5,
            "calories": 420,
            "goal_progress": 0.85,
        },
        # ... more daily records
    ],
    tier="premium",   # "basic" | "premium" | "pro"
)

# result is a dict ready for JSON serialization
print(result["health_status"])       # "healthy" | "attention_needed"
print(result["anomalies"])           # anomaly list with narratives
print(result["_performance_ms"])     # inference time in ms
```

### Subscription Tiers

| Tier | Features |
|------|----------|
| **basic** | Anomaly alerts + weekly summaries |
| **premium** | Everything in basic + 30-day trendlines |
| **pro** | Everything + full baseline statistics raw data |

### CLI

```bash
# Run analysis on a pet
pawpulse-check --pet-id "abc-123" \
               --breed "Labrador" \
               --age 4.5 \
               --weight 30 \
               --data-file "/path/to/sample_data.json" \
               --tier premium
```

## Architecture

```
pawpulse_ml/
├── engine.py           # Main orchestrator (single entry point)
├── baseline/
│   └── learner.py      # Statistical per-pet baselines
├── detectors/
│   ├── anomaly.py       # Multi-signal anomaly detection
│   └── trends.py        # 30-day trendline prediction
├── features/
│   └── preprocessor.py  # Data normalization, gap filling
├── output/
│   └── formatter.py     # JSON output formatting (tier-aware)
└── utils/
    └── breed_priors.py  # 14 breed baselines + age/weight adjustment
```

## Design Principles

1. **Precision-first**: Requires 2+ corroborating signals before alerting
2. **Breed-aware**: Greyhound (score: 420) ≠ Bulldog (score: 280) ≠ Husky (score: 720)
3. **Fast**: ~15ms inference per pet per check (< 500ms requirement)
4. **Sparse data tolerant**: Breed prior fallback when data insufficient
5. **False-positive resistant**: Sustained deviation requirement, cooldown periods

## Engine Configuration

```python
engine = PawPulseEngine(
    z_score_threshold=2.5,          # Higher = fewer alerts (precision-focused)
    min_corroborating_signals=2,    # Min signals in deviation to alert
    enable_trends=True,             # Compute trends (Premium+ feature)
)
```

## Response Format

```json
{
  "pet_id": "abc-123",
  "generated_at": "2024-01-15T10:30:00",
  "tier": "premium",
  "health_status": "attention_needed",
  "baseline_confidence": 0.92,
  "data_days": 30,
  "is_mature": true,
  "anomalies": {
    "pet_id": "abc-123",
    "is_healthy": false,
    "anomaly_count": 1,
    "anomalies": [{
      "date": "2024-01-15",
      "severity": "medium",
      "confidence": 1.0,
      "signals_affected": [
        {"signal": "activity_score", "value": 200, "expected_mean": 550,
         "z_score": 3.2, "direction": "below", "severity": "high"}
      ],
      "narrative": "activity score, active time, and distance traveled are significantly lower than usual",
      "recommendation": "Your pet is less active than usual...",
      "requires_vet_attention": false
    }],
    "notable_signals": []
  },
  "trends": {
    "overall_health_trend": "stable",
    "trendlines": [...]
  },
  "_performance_ms": 25.3
}
```

## Data Input Format

The engine directly accepts raw FitBark ActivityDaily records:

```json
{
  "date": "YYYY-MM-DD",
  "score": 650,
  "min_play": 60,
  "min_active": 180,
  "min_rest": 900,
  "distance_in_miles": 3.5,
  "calories": 420,
  "goal_progress": 0.85
}
```

## Testing

```bash
cd /home/team/shared/anomaly-engine
pip install -e ".[dev]"
python -m pytest tests/ -v
```

## Supported Breeds (14 + Mixed)

Greyhound, Beagle, Basset Hound, Siberian Husky, Bernese Mountain Dog,
Chihuahua, Pomeranian, Labrador Retriever, Golden Retriever, Bulldog,
French Bulldog, Poodle, Australian Shepherd, Border Collie,
Jack Russell Terrier, Mixed

## Integration Checklist

- [ ] Backend calls `engine.check_pet()` with pet data after ingestion
- [ ] Engine caches baselines per `pet_id` in memory
- [ ] Set `tier` based on subscription level
- [ ] Anomalies with `requires_vet_attention: true` trigger notifications
- [ ] Store anomaly feedback (acknowledged/dismissed/vet-visit) for model improvement
