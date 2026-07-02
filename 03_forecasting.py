"""
03_forecasting.py
==================
Build, train, and compare multiple demand-forecasting models.

MODELS WE IMPLEMENT (simple → complex):
  1. Naive               - tomorrow = today (the surprisingly hard-to-beat baseline)
  2. Seasonal Naive      - tomorrow = same day last week
  3. Moving Average      - mean of last 7 days
  4. Holt-Winters (ETS)  - exponential smoothing with trend + seasonality
  5. SARIMA              - autoregressive model with seasonality
  6. Prophet             - Facebook/Meta's tool, great for business series
  7. XGBoost             - gradient boosted trees on engineered features

KEY CONCEPT: TRAIN/TEST SPLIT FOR TIME SERIES
We CANNOT shuffle randomly like in regular ML. Time has direction.
Train must come BEFORE test — otherwise we leak future info.
We hold out the LAST 60 days as the test set.

EVALUATION METRICS (each tells a different story):
  - MAE   (Mean Absolute Error): average size of error, same units as data
  - RMSE  (Root Mean Squared Error): penalizes large errors more
  - MAPE  (Mean Absolute % Error): scale-free, easy to communicate to business
  - Bias  (Mean Error): are we systematically over- or under-forecasting?
"""

import warnings
warnings.filterwarnings('ignore')

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Statistical models
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.statespace.sarimax import SARIMAX

# Try optional libraries; project still works without them
try:
    from prophet import Prophet
    PROPHET_OK = True
except ImportError:
    PROPHET_OK = False
    print("⚠ Prophet not installed — skipping. (pip install prophet)")

try:
    from xgboost import XGBRegressor
    XGB_OK = True
except ImportError:
    XGB_OK = False
    print("⚠ XGBoost not installed — skipping. (pip install xgboost)")

# ----- CONFIG -----
sns.set_style('whitegrid')
PLOT_DIR = Path('outputs/plots')
PLOT_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR = Path('outputs')
TEST_DAYS = 60   # forecast horizon — last 60 days held out for evaluation


# ============================================================
# DATA + SPLIT
# ============================================================
def load_and_split(path='data/sales_data.csv', test_days=TEST_DAYS):
    df = pd.read_csv(path, parse_dates=['date']).sort_values('date')
    df = df.set_index('date')
    train = df.iloc[:-test_days]
    test = df.iloc[-test_days:]
    print(f"Train: {train.index.min().date()} → {train.index.max().date()} ({len(train)} days)")
    print(f"Test:  {test.index.min().date()} → {test.index.max().date()} ({len(test)} days)")
    return train, test


# ============================================================
# METRICS
# ============================================================
def evaluate(y_true, y_pred, model_name):
    """Compute error metrics. Each highlights something different."""
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    err = y_pred - y_true

    mae  = np.mean(np.abs(err))
    rmse = np.sqrt(np.mean(err ** 2))
    # Guard against div-by-zero in MAPE
    mape = np.mean(np.abs(err) / np.maximum(y_true, 1)) * 100
    bias = np.mean(err)

    return {
        'model': model_name,
        'MAE': round(mae, 2),
        'RMSE': round(rmse, 2),
        'MAPE (%)': round(mape, 2),
        'Bias': round(bias, 2),
    }


# ============================================================
# MODEL 1: NAIVE  — y_hat(t+h) = y(T) for all h
# WHY: the simplest possible baseline. If a fancy model can't beat this,
# it's adding no value. Surprisingly hard to beat on noisy short horizons.
# ============================================================
def naive_forecast(train, test):
    last_val = train['sales'].iloc[-1]
    return np.full(len(test), last_val)


# ============================================================
# MODEL 2: SEASONAL NAIVE  — y_hat(t+h) = y(t+h-7)
# WHY: if data has weekly seasonality (retail!), looking back one week
# is a strong baseline that respects the seasonal structure.
# ============================================================
def seasonal_naive_forecast(train, test, season=7):
    last_season = train['sales'].iloc[-season:].values
    n = len(test)
    return np.array([last_season[i % season] for i in range(n)])


# ============================================================
# MODEL 3: MOVING AVERAGE  — average of last N days
# WHY: smooths out noise. Larger window = more smoothing but slower
# to react to changes.
# ============================================================
def moving_average_forecast(train, test, window=7):
    avg = train['sales'].iloc[-window:].mean()
    return np.full(len(test), avg)


# ============================================================
# MODEL 4: HOLT-WINTERS (Triple Exponential Smoothing)
# Decomposes series into Level, Trend, Seasonality and updates each
# with its own smoothing parameter (alpha, beta, gamma).
#
# When to use: clear trend + seasonality, fast to fit, no covariates needed.
# Limitation: can't easily incorporate external regressors like 'promo'.
# ============================================================
def holt_winters_forecast(train, test, season=7):
    model = ExponentialSmoothing(
        train['sales'],
        trend='add',
        seasonal='add',
        seasonal_periods=season,
    ).fit(optimized=True)
    return model.forecast(len(test)).values


# ============================================================
# MODEL 5: SARIMA — Seasonal ARIMA
# ARIMA(p,d,q) × (P,D,Q,s):
#   p  = AR order (how many past values affect current)
#   d  = differencing (to remove trend)
#   q  = MA order (how many past errors affect current)
#   P,D,Q,s = the same but for seasonal component, with period s
#
# In production you'd grid-search or use auto_arima. We use sensible defaults
# for weekly seasonality.
# ============================================================
def sarima_forecast(train, test, season=7):
    model = SARIMAX(
        train['sales'],
        order=(1, 1, 1),
        seasonal_order=(1, 1, 1, season),
        enforce_stationarity=False,
        enforce_invertibility=False,
    ).fit(disp=False)
    return model.forecast(len(test)).values


# ============================================================
# MODEL 6: PROPHET (Meta)
# Decomposes y(t) = g(t) + s(t) + h(t) + ε
#   g(t) = trend (with automatic changepoint detection)
#   s(t) = seasonality (Fourier-based for flexibility)
#   h(t) = holidays
# Great for business series; handles missing data and outliers gracefully.
# ============================================================
def prophet_forecast(train, test):
    df_train = train.reset_index().rename(columns={'date': 'ds', 'sales': 'y'})
    m = Prophet(
        weekly_seasonality=True,
        yearly_seasonality=True,
        daily_seasonality=False,
    )
    m.fit(df_train)
    future = m.make_future_dataframe(periods=len(test), freq='D')
    forecast = m.predict(future)
    return forecast['yhat'].iloc[-len(test):].values


# ============================================================
# MODEL 7: XGBOOST
# Treats forecasting as a SUPERVISED REGRESSION problem on engineered features.
# Strengths:  handles non-linearities, captures interactions, uses external
#             regressors (promo, holidays) directly.
# Tradeoff:   needs feature engineering and care not to leak future info.
# ============================================================
def build_features(df):
    """Calendar features that are known in advance for any future date."""
    out = df.copy()
    out['day_of_week'] = out.index.dayofweek
    out['month']       = out.index.month
    out['day_of_month']= out.index.day
    out['day_of_year'] = out.index.dayofyear
    out['week_of_year']= out.index.isocalendar().week.astype(int)
    out['quarter']     = out.index.quarter
    out['is_weekend']  = (out.index.dayofweek >= 5).astype(int)
    return out


def xgboost_forecast(train, test):
    feature_cols = [
        'day_of_week', 'month', 'day_of_month', 'day_of_year',
        'week_of_year', 'quarter', 'is_weekend', 'promo',
    ]
    train_feat = build_features(train)
    test_feat  = build_features(test)

    X_train, y_train = train_feat[feature_cols], train_feat['sales']
    X_test           = test_feat[feature_cols]

    model = XGBRegressor(
        n_estimators=500,
        learning_rate=0.05,
        max_depth=5,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)
    return model.predict(X_test), model, feature_cols


# ============================================================
# ORCHESTRATION
# ============================================================
def run_all_models(train, test):
    """Train each model, generate forecasts, collect into one dict."""
    forecasts = {}
    print("\n" + "=" * 60)
    print("TRAINING MODELS")
    print("=" * 60)

    print("→ Naive ...");           forecasts['Naive']          = naive_forecast(train, test)
    print("→ Seasonal Naive ...");  forecasts['SeasonalNaive']  = seasonal_naive_forecast(train, test)
    print("→ Moving Average ...");  forecasts['MovingAvg(7)']   = moving_average_forecast(train, test)
    print("→ Holt-Winters ...");    forecasts['HoltWinters']    = holt_winters_forecast(train, test)
    print("→ SARIMA ...");          forecasts['SARIMA']         = sarima_forecast(train, test)

    if PROPHET_OK:
        print("→ Prophet ...");     forecasts['Prophet']        = prophet_forecast(train, test)
    if XGB_OK:
        print("→ XGBoost ...");     pred, model, _ = xgboost_forecast(train, test)
        forecasts['XGBoost'] = pred

    return forecasts


def build_results_table(test, forecasts):
    rows = [evaluate(test['sales'], pred, name) for name, pred in forecasts.items()]
    results = pd.DataFrame(rows).sort_values('RMSE').reset_index(drop=True)
    return results


def plot_forecast_comparison(train, test, forecasts):
    """Show the last 90 days of training plus all model forecasts on test set."""
    fig, ax = plt.subplots(figsize=(14, 6))

    history_tail = train['sales'].iloc[-90:]
    ax.plot(history_tail.index, history_tail.values, label='Training (last 90d)', color='gray', linewidth=1)
    ax.plot(test.index, test['sales'].values, label='Actual', color='black', linewidth=2)

    colors = sns.color_palette('tab10', n_colors=len(forecasts))
    for (name, pred), c in zip(forecasts.items(), colors):
        ax.plot(test.index, pred, label=name, linewidth=1.3, color=c, alpha=0.85)

    ax.axvline(test.index[0], color='red', linestyle='--', alpha=0.5, label='Train/Test split')
    ax.set_title(f'Forecast Comparison — {TEST_DAYS}-day Horizon', fontsize=14, fontweight='bold')
    ax.set_xlabel('Date'); ax.set_ylabel('Units Sold')
    ax.legend(loc='upper left', ncol=2, fontsize=9)
    plt.tight_layout()
    plt.savefig(PLOT_DIR / '05_forecast_comparison.png', dpi=120)
    plt.close()
    print("✓ Saved: 05_forecast_comparison.png")


def plot_best_model(test, forecasts, best_name):
    """Zoom in on the best model with residuals."""
    fig, axes = plt.subplots(2, 1, figsize=(14, 7), sharex=True,
                              gridspec_kw={'height_ratios': [2, 1]})
    pred = forecasts[best_name]

    axes[0].plot(test.index, test['sales'].values, label='Actual', color='black', linewidth=2)
    axes[0].plot(test.index, pred, label=f'{best_name} forecast', color='red', linewidth=1.5)
    axes[0].fill_between(test.index, test['sales'].values, pred, alpha=0.2, color='red')
    axes[0].legend(); axes[0].set_title(f'Best Model: {best_name}', fontweight='bold')
    axes[0].set_ylabel('Units')

    residuals = test['sales'].values - pred
    axes[1].bar(test.index, residuals, color=np.where(residuals >= 0, 'steelblue', 'coral'))
    axes[1].axhline(0, color='black', linewidth=0.5)
    axes[1].set_title('Residuals (Actual − Forecast)')
    axes[1].set_ylabel('Error')

    plt.tight_layout()
    plt.savefig(PLOT_DIR / '06_best_model.png', dpi=120)
    plt.close()
    print(f"✓ Saved: 06_best_model.png")


def save_outputs(test, forecasts, results):
    # Save metrics
    results.to_csv(OUT_DIR / 'results.csv', index=False)
    print(f"✓ Saved: outputs/results.csv")

    # Save forecasts
    forecast_df = pd.DataFrame({'date': test.index, 'actual': test['sales'].values})
    for name, pred in forecasts.items():
        forecast_df[name] = pred
    forecast_df.to_csv(OUT_DIR / 'forecasts.csv', index=False)
    print(f"✓ Saved: outputs/forecasts.csv")


def main():
    print("DEMAND FORECASTING PROJECT")
    print("=" * 60)
    train, test = load_and_split()
    forecasts = run_all_models(train, test)
    results = build_results_table(test, forecasts)

    print("\n" + "=" * 60)
    print("RESULTS (sorted by RMSE — lower is better)")
    print("=" * 60)
    print(results.to_string(index=False))

    best = results.iloc[0]['model']
    print(f"\n🏆 Best model: {best}")

    plot_forecast_comparison(train, test, forecasts)
    plot_best_model(test, forecasts, best)
    save_outputs(test, forecasts, results)

    print("\n✓ Done. All outputs in outputs/")


if __name__ == '__main__':
    main()
