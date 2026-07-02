"""
01_generate_data.py
====================
Generates synthetic but realistic daily retail sales data for a single SKU.

WHY SYNTHETIC DATA?
- You can run the project immediately without downloads/auth
- You know the true underlying patterns, so you can verify your models pick them up
- For your PORTFOLIO version, swap this with real data (M5, Rossmann, etc.)

WHAT WE'RE SIMULATING (these are the building blocks of any time series):
1. Level   - baseline demand (e.g., ~100 units/day)
2. Trend   - gradual growth or decline over time
3. Seasonality - repeating patterns (weekly, yearly)
4. Holidays/Events - irregular spikes on known dates
5. Promotions - business-driven temporary lifts
6. Noise   - random unexplained variation

Real-world data has ALL of these mixed together. Good forecasting separates signal from noise.
"""

import numpy as np
import pandas as pd
from pathlib import Path

# Fixed seed so results are reproducible
np.random.seed(42)


def generate_retail_sales(start_date='2022-01-01', end_date='2024-12-31'):
    """Generate 3 years of daily sales for one product."""

    dates = pd.date_range(start_date, end_date, freq='D')
    n = len(dates)

    # ---- 1. BASE LEVEL ----
    base = 100  # average baseline units sold per day

    # ---- 2. TREND ----
    # Linear growth: business is growing, +30 units over 3 years
    trend = np.linspace(0, 30, n)

    # ---- 3. WEEKLY SEASONALITY ----
    # Retail typically has weekend peaks
    day_of_week = dates.dayofweek  # Monday=0, Sunday=6
    weekly = np.zeros(n)
    weekly[day_of_week == 4] = 10   # Friday slight boost
    weekly[day_of_week == 5] = 25   # Saturday peak
    weekly[day_of_week == 6] = 22   # Sunday strong

    # ---- 4. YEARLY SEASONALITY ----
    # Sinusoidal yearly pattern + heavy Q4 holiday lift (retail reality)
    day_of_year = dates.dayofyear
    yearly = 15 * np.sin(2 * np.pi * (day_of_year - 80) / 365)
    month = dates.month
    holiday_boost = np.where(month == 11, 25, 0) + np.where(month == 12, 45, 0)

    # ---- 5. SPECIFIC HOLIDAYS ----
    # Black Friday, July 4th cause demand spikes
    holidays = {
        '2022-11-25': 80, '2023-11-24': 90, '2024-11-29': 100,  # Black Friday
        '2022-07-04': 50, '2023-07-04': 55, '2024-07-04': 60,   # July 4th
        '2022-12-23': 60, '2023-12-23': 65, '2024-12-23': 70,   # Pre-Christmas
    }
    holiday_array = np.zeros(n)
    date_to_idx = {d: i for i, d in enumerate(dates)}
    for date_str, boost in holidays.items():
        d = pd.Timestamp(date_str)
        if d in date_to_idx:
            holiday_array[date_to_idx[d]] = boost

    # ---- 6. PROMOTIONS ----
    # ~10 random promos per year, lasting 3 days each, ~60 unit lift
    promo_array = np.zeros(n)
    promo_flag = np.zeros(n, dtype=int)
    n_promos = 30
    promo_starts = np.random.choice(n - 3, n_promos, replace=False)
    for start in promo_starts:
        promo_array[start:start + 3] += 60
        promo_flag[start:start + 3] = 1

    # ---- 7. RANDOM NOISE ----
    # Gaussian noise represents all the unexplained day-to-day variation
    noise = np.random.normal(0, 8, n)

    # ---- COMBINE ALL COMPONENTS ----
    # This is an ADDITIVE model: y = level + trend + seasonal + ... + noise
    # (Real data may need a MULTIPLICATIVE model if variance grows with level)
    sales = (
        base + trend + weekly + yearly + holiday_boost
        + holiday_array + promo_array + noise
    )
    sales = np.maximum(sales, 0).round().astype(int)  # sales can't be negative

    df = pd.DataFrame({
        'date': dates,
        'sales': sales,
        'promo': promo_flag,
        'day_of_week': day_of_week,
        'month': month,
        'is_weekend': (day_of_week >= 5).astype(int),
    })

    return df


if __name__ == '__main__':
    Path('data').mkdir(exist_ok=True)
    df = generate_retail_sales()
    output_path = 'data/sales_data.csv'
    df.to_csv(output_path, index=False)

    print(f"Generated {len(df)} days of sales data")
    print(f"Date range: {df['date'].min().date()} to {df['date'].max().date()}")
    print(f"Mean daily sales: {df['sales'].mean():.1f}")
    print(f"Std daily sales:  {df['sales'].std():.1f}")
    print(f"Min / Max:        {df['sales'].min()} / {df['sales'].max()}")
    print(f"\nSaved to: {output_path}\n")
    print("First 5 rows:")
    print(df.head())
