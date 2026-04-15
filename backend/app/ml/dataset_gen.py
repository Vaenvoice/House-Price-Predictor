"""
EstateAI Synthetic Dataset Generator
Generates realistic house price data for Indian cities with configurable noise.
"""
import numpy as np
import pandas as pd
from app.config import LOCATIONS, DATASET_SIZE, DATASET_PATH


def generate_dataset(n_samples=DATASET_SIZE, save=True):
    """
    Generate a synthetic house price dataset with realistic pricing logic.
    
    Pricing factors:
    - Larger area → higher price
    - Better location (tier-1 cities) → higher price  
    - More rooms → higher price
    - Older house → lower price (depreciation)
    - Area-per-room premium for spacious layouts
    - Random noise to simulate real-world variance
    """
    np.random.seed(42)

    locations = list(LOCATIONS.keys())
    
    # Calculate weights based on city tiers (more samples for major cities)
    tier_weights = {
        "tier-1": 10,
        "tier-2": 5,
        "tier-3": 2,
        "suburban": 3,
        "rural": 2
    }
    
    raw_weights = [tier_weights.get(LOCATIONS[loc]["type"], 1) for loc in locations]
    weights = np.array(raw_weights) / sum(raw_weights)

    # Generate features with realistic distributions
    areas = np.random.normal(1800, 650, n_samples).clip(500, 5000).astype(int)
    rooms = np.random.choice(
        [1, 2, 3, 4, 5, 6], n_samples,
        p=[0.05, 0.20, 0.35, 0.25, 0.10, 0.05]
    )
    locs = np.random.choice(locations, n_samples, p=weights)
    ages = np.random.exponential(12, n_samples).clip(0, 50).astype(int)

    # Calculate prices using multi-factor formula
    BASE_PRICE_PER_SQFT = 3500  # INR base rate
    prices = []

    for i in range(n_samples):
        loc_mult = LOCATIONS[locs[i]]["multiplier"]

        # Base price from area × location
        price = areas[i] * BASE_PRICE_PER_SQFT * loc_mult

        # Room bonus (each room adds value, scaled by location)
        price += rooms[i] * 280000 * loc_mult

        # Age depreciation (non-linear: rapid early, then slower)
        age_factor = max(0.50, 1 - (ages[i] * 0.011) - (ages[i] ** 2 * 0.00004))
        price *= age_factor

        # Spaciousness premium: more area per room = higher value
        area_per_room = areas[i] / rooms[i]
        if area_per_room > 500:
            price *= 1.10
        elif area_per_room > 350:
            price *= 1.04
        elif area_per_room < 200:
            price *= 0.94

        # Random noise (±12% to simulate market variance)
        noise = np.random.normal(1.0, 0.07)
        price *= noise

        # Floor at 5 lakh, round to nearest thousand
        prices.append(max(500000, round(price, -3)))

    df = pd.DataFrame({
        "area": areas,
        "rooms": rooms,
        "location": locs,
        "age": ages,
        "price": prices
    })

    if save:
        DATASET_PATH.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(DATASET_PATH, index=False)
        print(f"Generated {n_samples} samples -> {DATASET_PATH}")

    return df
