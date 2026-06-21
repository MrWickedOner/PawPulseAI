"""PawPulse CLI — Run anomaly detection from the command line.

Usage:
    pawpulse-check --pet-id "abc" --breed "Labrador" --age 4.5 --weight 30 \\
                   --data-file "data.json" --tier premium
"""

import argparse
import json
import sys
from datetime import datetime

from pawpulse_ml.engine import PawPulseEngine


def load_data_file(path: str) -> list:
    """Load FitBark daily records from a JSON file."""
    with open(path) as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return data.get("records", data.get("daily", data.get("fitbark_daily", [data])))
    return []


def main():
    parser = argparse.ArgumentParser(
        description="PawPulse Anomaly Detection CLI",
    )
    parser.add_argument("--pet-id", required=True, help="Pet UUID")
    parser.add_argument("--breed", required=True, help="Breed name")
    parser.add_argument("--age", type=float, required=True, help="Age in years")
    parser.add_argument("--weight", type=float, required=True, help="Weight in kg")
    parser.add_argument("--data-file", help="JSON file with FitBark daily records")
    parser.add_argument("--tier", default="basic", choices=["basic", "premium", "pro"],
                        help="Subscription tier")
    parser.add_argument("--threshold", type=float, default=2.5,
                        help="Z-score anomaly threshold (higher = fewer alerts)")
    parser.add_argument("--min-signals", type=int, default=2,
                        help="Minimum corroborating signals for alert")
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")

    args = parser.parse_args()

    # Load data
    if args.data_file:
        records = load_data_file(args.data_file)
        print(f"Loaded {len(records)} records from {args.data_file}", file=sys.stderr)
    else:
        records = []

    # Initialize engine
    engine = PawPulseEngine(
        z_score_threshold=args.threshold,
        min_corroborating_signals=args.min_signals,
    )

    # Run analysis
    result = engine.check_pet(
        pet_id=args.pet_id,
        breed=args.breed,
        age_years=args.age,
        weight_kg=args.weight,
        fitbark_daily=records,
        tier=args.tier,
    )

    # Add metadata
    result["_cli_version"] = "0.1.0"
    result["_generated_by"] = "pawpulse-cli"

    # Output
    output = json.dumps(result, indent=2, default=str)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Results written to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
