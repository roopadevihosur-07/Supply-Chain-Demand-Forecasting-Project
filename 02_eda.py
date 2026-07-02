"""
02_eda.py
=========
Exploratory Data Analysis for our retail sales time series.

WHY EDA MATTERS FOR FORECASTING:
Before throwing models at data, you need to UNDERSTAND it. This guides
which model is appropriate. Specifically, we want to identify:

  1. TREND          - long-run direction of the series
  2. SEASONALITY    - repeating patterns at fixed periods (weekly, yearly)
  3. CYCLICALITY    - longer non-fixed waves (e.g., business cycles)
  4. STATIONARITY   - statistical properties (mean, variance) stable over time?
                       ARIMA needs this; ML models tolerate it less strictly.
  5. AUTOCORRELATION - how today's value depends on past values
                       (drives ARIMA's order parameters)
  6. OUTLIERS / STRUCTURAL BREAKS - promos, holidays, COVID-style shocks
"""

import warnings
warnings.filterwarnings('ignore')

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

# ----- SETUP -----
sns.set_style('whitegrid')
PLOT_DIR = Path('outputs/plots')
PLOT_DIR.mkdir(parents=True, exist_ok=True)


def load_data(path='data/sales_data.csv'):
    df = pd.read_csv(path, parse_dates=['date'])
    df = df.sort_values('date').reset_index(drop=True)
    df = df.set_index('date')
    return df


def plot_full_series(df):
    """Step 1: just look at the data. Always do this first."""
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(df.index, df['sales'], linewidth=0.7, color='steelblue')
    ax.set_title('Daily Sales — Full History', fontsize=14, fontweight='bold')
    ax.set_xlabel('Date')
    ax.set_ylabel('Units Sold')
    plt.tight_layout()
    plt.savefig(PLOT_DIR / '01_full_series.png', dpi=120)
    plt.close()
    print("✓ Saved: 01_full_series.png")


def plot_decomposition(df):
    """
    SEASONAL DECOMPOSITION: y = Trend + Seasonal + Residual (additive)

    This is one of the most useful tools in time series analysis.
    Period=7 captures weekly seasonality. Period=365 captures yearly,
    but needs more data and is slower — we'll do weekly here.
    """
    decomp = seasonal_decompose(df['sales'], model='additive', period=7)

    fig, axes = plt.subplots(4, 1, figsize=(14, 10), sharex=True)
    axes[0].plot(decomp.observed, linewidth=0.7); axes[0].set_title('Observed')
    axes[1].plot(decomp.trend, color='orange');   axes[1].set_title('Trend (long-run direction)')
    axes[2].plot(decomp.seasonal, color='green'); axes[2].set_title('Seasonal (weekly pattern)')
    axes[3].plot(decomp.resid, color='red', linewidth=0.5); axes[3].set_title('Residual (what trend+seasonal cannot explain)')
    plt.suptitle('Time Series Decomposition (weekly period)', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(PLOT_DIR / '02_decomposition.png', dpi=120)
    plt.close()
    print("✓ Saved: 02_decomposition.png")


def test_stationarity(df):
    """
    AUGMENTED DICKEY-FULLER TEST
    H0 (null hypothesis): the series is NON-stationary (has a unit root).
    If p-value < 0.05 → reject H0 → series is stationary.

    Why we care: classical ARIMA assumes stationarity. If non-stationary,
    we DIFFERENCE the series (y_t - y_{t-1}) and re-test. That's the 'I'
    (Integrated) in ARIMA — its order 'd' = number of differencings.
    """
    print("\n" + "=" * 60)
    print("AUGMENTED DICKEY-FULLER STATIONARITY TEST")
    print("=" * 60)

    result = adfuller(df['sales'].dropna())
    print(f"ADF Statistic: {result[0]:.4f}")
    print(f"p-value:       {result[1]:.4f}")
    for k, v in result[4].items():
        print(f"  Critical Value ({k}): {v:.4f}")

    if result[1] < 0.05:
        print("→ Series is STATIONARY (reject H0)")
    else:
        print("→ Series is NON-stationary. Try first-differencing.")
        diff = df['sales'].diff().dropna()
        r2 = adfuller(diff)
        print(f"\nAfter 1st differencing — p-value: {r2[1]:.4f}")
        if r2[1] < 0.05:
            print("→ Stationary after 1 differencing. Use d=1 in ARIMA.")


def plot_acf_pacf(df):
    """
    ACF (Autocorrelation Function): correlation of series with its own lags.
    PACF (Partial ACF): direct correlation, removing intermediate lags.

    HOW TO READ THEM (used to choose ARIMA p, q):
      - ACF tails off, PACF cuts off at lag p → AR(p) model
      - ACF cuts off at lag q, PACF tails off → MA(q) model
      - Both tail off → ARMA / mixed model
      - Significant spike at lag 7 → weekly seasonality (use SARIMA, season=7)
    """
    fig, axes = plt.subplots(2, 1, figsize=(14, 6))
    plot_acf(df['sales'], lags=40, ax=axes[0])
    axes[0].set_title('Autocorrelation (ACF) — look for repeating spikes')
    plot_pacf(df['sales'], lags=40, ax=axes[1], method='ywm')
    axes[1].set_title('Partial Autocorrelation (PACF)')
    plt.tight_layout()
    plt.savefig(PLOT_DIR / '03_acf_pacf.png', dpi=120)
    plt.close()
    print("✓ Saved: 03_acf_pacf.png")


def plot_seasonal_patterns(df):
    """Aggregate by day-of-week and month to see seasonal averages clearly."""
    df_plot = df.copy()
    df_plot['day_of_week'] = df_plot.index.dayofweek
    df_plot['month'] = df_plot.index.month
    df_plot['year'] = df_plot.index.year

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    dow_labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    dow_avg = df_plot.groupby('day_of_week')['sales'].mean()
    axes[0].bar(dow_labels, dow_avg.values, color='steelblue')
    axes[0].set_title('Average Sales by Day of Week')
    axes[0].set_ylabel('Avg Units Sold')

    month_avg = df_plot.groupby('month')['sales'].mean()
    axes[1].bar(range(1, 13), month_avg.values, color='coral')
    axes[1].set_title('Average Sales by Month')
    axes[1].set_xticks(range(1, 13))
    axes[1].set_xlabel('Month')

    plt.tight_layout()
    plt.savefig(PLOT_DIR / '04_seasonal_patterns.png', dpi=120)
    plt.close()
    print("✓ Saved: 04_seasonal_patterns.png")


def summary_stats(df):
    print("\n" + "=" * 60)
    print("SUMMARY STATISTICS")
    print("=" * 60)
    print(df['sales'].describe().round(2))
    print(f"\nTotal observations: {len(df)}")
    print(f"Promo days:         {df['promo'].sum()} ({100 * df['promo'].mean():.1f}%)")


def main():
    print("Loading data...")
    df = load_data()
    summary_stats(df)
    plot_full_series(df)
    plot_decomposition(df)
    test_stationarity(df)
    plot_acf_pacf(df)
    plot_seasonal_patterns(df)
    print("\n✓ EDA complete. Check outputs/plots/")


if __name__ == '__main__':
    main()
