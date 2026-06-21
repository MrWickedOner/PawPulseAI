"""Breed-specific baseline priors.

Used to seed baselines before sufficient individual data is collected.
Drawn from FitBark's similar_dogs_stat endpoint and veterinary literature.

Key insight from research: A Greyhound rests 36-40% more than an
average dog, while a Husky travels significantly farther. Using
generic baselines would generate false alerts for these breeds.
"""

import math
from dataclasses import dataclass
from typing import Optional

@dataclass
class BreedPrior:
    """Prior distribution parameters for a breed's normal signals."""
    breed: str
    breed_group: str  # e.g., "sporting", "hound", "working", "toy", "non-sporting", "herding", "terrier"

    # Activity (0-1000 score scale)
    daily_score_mean: float
    daily_score_std: float

    # Daily breakdown (minutes)
    play_minutes_mean: float
    active_minutes_mean: float
    rest_minutes_mean: float

    # Distance (km)
    distance_km_mean: float
    distance_km_std: float

    # Sleep patterns
    nighttime_sleep_hours_mean: float
    daytime_nap_count_mean: float

    # Metadata
    weight_kg_min: float
    weight_kg_max: float
    energy_level: str  # "very_low", "low", "moderate", "high", "very_high"
    learning_window: int = 10  # Days needed before individual baselines become reliable
    z_tolerance: float = 2.5  # Standard deviation threshold for anomaly flagging

    def learning_window_days(self) -> int:
        """Days needed before individual baselines become reliable."""
        return self.learning_window

    def z_score_tolerance(self) -> float:
        """How many std devs before flagging as anomaly."""
        return self.z_tolerance


# =====================================================================
# Breed Priors Database
# =====================================================================
# Sources: FitBark similar_dogs stats, AKC breed standards, vet literature
# Values are approximate and calibrated for anomaly detection initial seeding

BREED_PRIORS: dict[str, BreedPrior] = {
    # === HOUND GROUP ===
    "Greyhound": BreedPrior(
        breed="Greyhound", breed_group="hound",
        daily_score_mean=420, daily_score_std=85,
        play_minutes_mean=25, active_minutes_mean=95, rest_minutes_mean=1080,
        distance_km_mean=8.0, distance_km_std=3.5,
        nighttime_sleep_hours_mean=10.5, daytime_nap_count_mean=3,
        weight_kg_min=27, weight_kg_max=40, energy_level="moderate",
        learning_window=10, z_tolerance=2.5,
    ),
    "Beagle": BreedPrior(
        breed="Beagle", breed_group="hound",
        daily_score_mean=580, daily_score_std=90,
        play_minutes_mean=55, active_minutes_mean=150, rest_minutes_mean=920,
        distance_km_mean=6.5, distance_km_std=2.5,
        nighttime_sleep_hours_mean=8.5, daytime_nap_count_mean=3,
        weight_kg_min=9, weight_kg_max=13, energy_level="high",
        learning_window=14, z_tolerance=3.0,
    ),
    "Basset Hound": BreedPrior(
        breed="Basset Hound", breed_group="hound",
        daily_score_mean=350, daily_score_std=70,
        play_minutes_mean=20, active_minutes_mean=80, rest_minutes_mean=1100,
        distance_km_mean=3.0, distance_km_std=1.5,
        nighttime_sleep_hours_mean=11, daytime_nap_count_mean=4,
        weight_kg_min=20, weight_kg_max=29, energy_level="low",
        learning_window=10, z_tolerance=2.5,
    ),

    # === WORKING GROUP ===
    "Siberian Husky": BreedPrior(
        breed="Siberian Husky", breed_group="working",
        daily_score_mean=720, daily_score_std=110,
        play_minutes_mean=80, active_minutes_mean=220, rest_minutes_mean=780,
        distance_km_mean=16.0, distance_km_std=6.0,
        nighttime_sleep_hours_mean=7.5, daytime_nap_count_mean=2,
        weight_kg_min=16, weight_kg_max=27, energy_level="very_high",
        learning_window=14, z_tolerance=3.0,
    ),
    "Bernese Mountain Dog": BreedPrior(
        breed="Bernese Mountain Dog", breed_group="working",
        daily_score_mean=450, daily_score_std=75,
        play_minutes_mean=35, active_minutes_mean=120, rest_minutes_mean=1020,
        distance_km_mean=5.0, distance_km_std=2.0,
        nighttime_sleep_hours_mean=10, daytime_nap_count_mean=3,
        weight_kg_min=36, weight_kg_max=54, energy_level="moderate",
        learning_window=10, z_tolerance=2.5,
    ),

    # === TOY GROUP ===
    "Chihuahua": BreedPrior(
        breed="Chihuahua", breed_group="toy",
        daily_score_mean=620, daily_score_std=100,
        play_minutes_mean=60, active_minutes_mean=160, rest_minutes_mean=920,
        distance_km_mean=2.5, distance_km_std=1.5,
        nighttime_sleep_hours_mean=9, daytime_nap_count_mean=4,
        weight_kg_min=1.5, weight_kg_max=3, energy_level="high",
        learning_window=14, z_tolerance=3.0,
    ),
    "Pomeranian": BreedPrior(
        breed="Pomeranian", breed_group="toy",
        daily_score_mean=580, daily_score_std=95,
        play_minutes_mean=50, active_minutes_mean=150, rest_minutes_mean=940,
        distance_km_mean=2.0, distance_km_std=1.0,
        nighttime_sleep_hours_mean=9.5, daytime_nap_count_mean=4,
        weight_kg_min=1.5, weight_kg_max=3.5, energy_level="high",
        learning_window=14, z_tolerance=3.0,
    ),

    # === SPORTING GROUP ===
    "Labrador Retriever": BreedPrior(
        breed="Labrador Retriever", breed_group="sporting",
        daily_score_mean=650, daily_score_std=95,
        play_minutes_mean=70, active_minutes_mean=180, rest_minutes_mean=900,
        distance_km_mean=8.0, distance_km_std=3.0,
        nighttime_sleep_hours_mean=8, daytime_nap_count_mean=3,
        weight_kg_min=25, weight_kg_max=36, energy_level="high",
        learning_window=14, z_tolerance=3.0,
    ),
    "Golden Retriever": BreedPrior(
        breed="Golden Retriever", breed_group="sporting",
        daily_score_mean=600, daily_score_std=90,
        play_minutes_mean=60, active_minutes_mean=170, rest_minutes_mean=920,
        distance_km_mean=7.0, distance_km_std=2.5,
        nighttime_sleep_hours_mean=8.5, daytime_nap_count_mean=3,
        weight_kg_min=25, weight_kg_max=34, energy_level="high",
        learning_window=14, z_tolerance=3.0,
    ),

    # === NON-SPORTING GROUP ===
    "Bulldog": BreedPrior(
        breed="Bulldog", breed_group="non-sporting",
        daily_score_mean=280, daily_score_std=65,
        play_minutes_mean=15, active_minutes_mean=60, rest_minutes_mean=1140,
        distance_km_mean=1.5, distance_km_std=1.0,
        nighttime_sleep_hours_mean=12, daytime_nap_count_mean=5,
        weight_kg_min=22, weight_kg_max=25, energy_level="very_low",
        learning_window=10, z_tolerance=3.0,
    ),
    "French Bulldog": BreedPrior(
        breed="French Bulldog", breed_group="non-sporting",
        daily_score_mean=320, daily_score_std=70,
        play_minutes_mean=20, active_minutes_mean=75, rest_minutes_mean=1100,
        distance_km_mean=2.0, distance_km_std=1.0,
        nighttime_sleep_hours_mean=11, daytime_nap_count_mean=5,
        weight_kg_min=8, weight_kg_max=14, energy_level="low",
        learning_window=10, z_tolerance=2.5,
    ),
    "Poodle": BreedPrior(
        breed="Poodle", breed_group="non-sporting",
        daily_score_mean=520, daily_score_std=85,
        play_minutes_mean=45, active_minutes_mean=140, rest_minutes_mean=960,
        distance_km_mean=5.0, distance_km_std=2.0,
        nighttime_sleep_hours_mean=9, daytime_nap_count_mean=3,
        weight_kg_min=20, weight_kg_max=32, energy_level="moderate",
        learning_window=10, z_tolerance=2.5,
    ),

    # === HERDING GROUP ===
    "Australian Shepherd": BreedPrior(
        breed="Australian Shepherd", breed_group="herding",
        daily_score_mean=700, daily_score_std=105,
        play_minutes_mean=85, active_minutes_mean=200, rest_minutes_mean=800,
        distance_km_mean=14.0, distance_km_std=5.0,
        nighttime_sleep_hours_mean=7.5, daytime_nap_count_mean=2,
        weight_kg_min=18, weight_kg_max=29, energy_level="very_high",
        learning_window=14, z_tolerance=3.0,
    ),
    "Border Collie": BreedPrior(
        breed="Border Collie", breed_group="herding",
        daily_score_mean=750, daily_score_std=110,
        play_minutes_mean=90, active_minutes_mean=220, rest_minutes_mean=760,
        distance_km_mean=16.0, distance_km_std=5.5,
        nighttime_sleep_hours_mean=7, daytime_nap_count_mean=2,
        weight_kg_min=14, weight_kg_max=20, energy_level="very_high",
        learning_window=14, z_tolerance=3.0,
    ),

    # === TERRIER GROUP ===
    "Jack Russell Terrier": BreedPrior(
        breed="Jack Russell Terrier", breed_group="terrier",
        daily_score_mean=680, daily_score_std=100,
        play_minutes_mean=75, active_minutes_mean=190, rest_minutes_mean=860,
        distance_km_mean=7.0, distance_km_std=3.0,
        nighttime_sleep_hours_mean=8, daytime_nap_count_mean=3,
        weight_kg_min=5, weight_kg_max=8, energy_level="very_high",
        learning_window=14, z_tolerance=3.0,
    ),

    # === MIXED / UNKNOWN ===
    "Mixed": BreedPrior(
        breed="Mixed", breed_group="mixed",
        daily_score_mean=500, daily_score_std=120,
        play_minutes_mean=45, active_minutes_mean=135, rest_minutes_mean=960,
        distance_km_mean=5.0, distance_km_std=3.0,
        nighttime_sleep_hours_mean=9, daytime_nap_count_mean=3,
        weight_kg_min=5, weight_kg_max=45, energy_level="moderate",
        learning_window=10, z_tolerance=2.5,
    ),
}


def get_breed_prior(breed: str) -> BreedPrior:
    """Look up breed prior, falling back to Mixed if not found."""
    normalized = breed.strip().title()
    if normalized in BREED_PRIORS:
        return BREED_PRIORS[normalized]
    # Fuzzy match
    for key, prior in BREED_PRIORS.items():
        if key.lower() in normalized.lower() or normalized.lower() in key.lower():
            return prior
    return BREED_PRIORS["Mixed"]


def get_age_adjustment(age_years: float) -> dict[str, float]:
    """Return multipliers to adjust baselines for age.

    Puppies (<1yr): higher activity, more sleep fragmentation
    Seniors (>7yr): lower activity, more rest, higher variance
    """
    if age_years < 1:
        return {
            "score_multiplier": 1.3,
            "rest_multiplier": 0.85,
            "play_multiplier": 1.5,
            "tolerance_multiplier": 1.2,  # More variation = more tolerance
        }
    elif age_years < 3:
        return {
            "score_multiplier": 1.1,
            "rest_multiplier": 0.95,
            "play_multiplier": 1.2,
            "tolerance_multiplier": 1.0,
        }
    elif age_years < 7:
        return {
            "score_multiplier": 1.0,
            "rest_multiplier": 1.0,
            "play_multiplier": 1.0,
            "tolerance_multiplier": 1.0,
        }
    elif age_years < 10:
        return {
            "score_multiplier": 0.85,
            "rest_multiplier": 1.15,
            "play_multiplier": 0.7,
            "tolerance_multiplier": 1.1,
        }
    else:
        return {
            "score_multiplier": 0.7,
            "rest_multiplier": 1.3,
            "play_multiplier": 0.5,
            "tolerance_multiplier": 1.25,
        }


def compute_informed_prior(breed: str, age_years: float, weight_kg: float) -> BreedPrior:
    """Combine breed prior with age/weight adjustments for a personalized starting prior."""
    prior = get_breed_prior(breed)
    adj = get_age_adjustment(age_years)

    # Weight adjustment: heavier within breed = lower activity
    weight_range = prior.weight_kg_max - prior.weight_kg_min
    if weight_range > 0 and prior.energy_level != "mixed":
        weight_factor = (weight_kg - prior.weight_kg_min) / weight_range
        weight_factor = max(0, min(1, weight_factor))
        weight_penalty = 1.0 - (weight_factor * 0.2)  # Up to 20% reduction
    else:
        weight_penalty = 1.0

    return BreedPrior(
        breed=prior.breed,
        breed_group=prior.breed_group,
        daily_score_mean=prior.daily_score_mean * adj["score_multiplier"] * weight_penalty,
        daily_score_std=prior.daily_score_std * adj["tolerance_multiplier"],
        play_minutes_mean=prior.play_minutes_mean * adj["play_multiplier"],
        active_minutes_mean=prior.active_minutes_mean * adj["score_multiplier"],
        rest_minutes_mean=prior.rest_minutes_mean * adj["rest_multiplier"],
        distance_km_mean=prior.distance_km_mean * adj["score_multiplier"] * weight_penalty,
        distance_km_std=prior.distance_km_std * adj["tolerance_multiplier"],
        nighttime_sleep_hours_mean=prior.nighttime_sleep_hours_mean * adj["rest_multiplier"],
        daytime_nap_count_mean=prior.daytime_nap_count_mean * (1.0 if age_years < 7 else 1.3),
        weight_kg_min=prior.weight_kg_min,
        weight_kg_max=prior.weight_kg_max,
        energy_level=prior.energy_level,
        learning_window=prior.learning_window,
        z_tolerance=prior.z_tolerance,
    )
