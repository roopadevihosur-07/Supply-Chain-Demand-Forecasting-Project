# 📊 Supply Chain Demand Forecasting - Interactive Frontend Guide

## Getting Started

### Launch the App

```bash
cd /Users/roopakeerthiraj/Documents/SupplyChainProject
streamlit run app.py
```

The app will open at: **http://localhost:8501**

### Stop the App

Press `Ctrl+C` in the terminal where Streamlit is running.

---

## Navigation Overview

Use the sidebar on the left to switch between 6 main sections:

### 🏠 **Overview** — Project at a Glance
**What you'll learn:**
- High-level project flow (Data → EDA → Models → Evaluation)
- Key supply chain concepts
- Why demand forecasting matters
- Dataset statistics (1,096 days of sales data)

**Interactive elements:**
- View key metrics: mean sales, std deviation, min/max
- Understand the business impact

**Takeaway:** Demand forecasting is the backbone of supply chain — small improvements save millions.

---

### 📊 **Data Generation** — How Synthetic Data is Built

**What you'll learn:**
- The components that make realistic sales data
- How trend, seasonality, and promotions work
- Data statistics and distributions

**Sections:**
1. **Data Components** — breakdown of what's in the data
   - Linear trend: +30 units over 3 years
   - Weekly seasonality: weekend peaks
   - Yearly seasonality: Q4 holiday lift (60% surge)
   - Random promotions: ~30 campaigns over 3 years
   - Gaussian noise

2. **Full Time Series Plot** — interactive visualization
   - Zoom in/out to see different patterns
   - Red dots show promotion days
   - Notice the upward trend and seasonal peaks

3. **Data Sample** — raw dataframe (first 20 rows)
   - Columns: date, sales, promo, day_of_week, month, is_weekend

4. **Distribution & Patterns**
   - Sales histogram: shows it's roughly bell-shaped
   - Day-of-week breakdown: weekends clearly higher

**Takeaway:** Real retail data has multiple overlapping patterns. Simple models that miss even one pattern fail badly.

---

### 🔍 **Exploratory Analysis** — Understanding Data Patterns

**What you'll learn:**
- Stationarity testing (why it matters for ARIMA)
- Time series decomposition
- Autocorrelation patterns
- Seasonal effects

**Key Tests:**
1. **Augmented Dickey-Fuller (ADF) Test**
   - ADF Statistic: -3.8978
   - p-value: 0.0021 ✅ (< 0.05 = stationary)
   - **What it means:** The series is stationary → safe to use ARIMA models without differencing

2. **Decomposition Plot**
   - Shows 4 components:
     - **Original:** Raw data with all patterns mixed
     - **Trend:** Long-term upward movement (~30 units/3yr)
     - **Seasonal:** Repeating weekly pattern
     - **Residual:** Noise and anomalies after removing trend/seasonality

3. **ACF/PACF Plot** (Autocorrelation)
   - **ACF:** correlation with lagged versions
   - **PACF:** direct correlation only
   - **Reading it:** Spike at lag 7 = weekly seasonality
   - **Use for:** Determining ARIMA parameters (p, d, q)

4. **Seasonal Patterns Plot**
   - Day-of-week effect: weekends peak
   - Monthly effect: some variation
   - Yearly effect: Q4 holiday surge

**Takeaway:** Decomposition reveals the hidden structure. Models must capture all patterns.

---

### 🤖 **Forecasting Models** — The 7 Competitors

**What you'll learn:**
- How each model works
- Pros and cons of each approach
- When to use each model
- Why train-test splitting matters

**The 7 Models:**

| Model | How It Works | Best For | Limitation |
|-------|-------------|----------|-----------|
| **Naive** | Predicts: last value | Baseline only | Ignores seasonality |
| **Seasonal Naive** | Predicts: value from 7 days ago | Weekly patterns | Misses yearly seasonality |
| **Moving Average** | Averages last N observations | Smoothing noise | Slow to react to changes |
| **Holt-Winters** | Level + Trend + Seasonality smoothing | Stable patterns | Can't use external data |
| **SARIMA** | Autoregressive + Integrated + MA + Seasonal | Statistical rigor | Complex tuning needed |
| **Prophet** | Trend + Seasonality + Holidays (Meta) | Business data | Less for short horizons |
| **XGBoost** | Gradient-boosted trees with features | Complex patterns | Needs feature engineering |

**Train-Test Split Visualization:**
- Shows why **chronological split** is critical
- ❌ Random shuffle: leaks future data (unrealistic metrics)
- ✅ Chronological: last 60 days = test, earlier = training
- Training: Jan 2022 - Oct 2024 (1,036 days)
- Testing: Nov 2 - Dec 31, 2024 (60 days)

**Takeaway:** Model choice depends on data patterns. ARIMA needs stationarity. Prophet needs seasonality structure. XGBoost needs features.

---

### 📈 **Results & Comparison** — Who Won?

**What you'll learn:**
- Model performance metrics
- What MAE, RMSE, MAPE, and Bias mean
- Why Prophet won
- The danger of bias

**Metrics Explained:**

1. **MAE (Mean Absolute Error)**
   - Formula: `mean(|y - ŷ|)`
   - Interpretation: Average error in original units
   - Use when: Explaining to non-technical people
   - Units: Same as sales (units)

2. **RMSE (Root Mean Squared Error)**
   - Formula: `√mean((y - ŷ)²)`
   - Interpretation: Penalizes large errors more
   - Use when: Stockouts cost more than overforecasting
   - Units: Same as sales (units)

3. **MAPE (Mean Absolute Percentage Error)**
   - Formula: `mean(|y - ŷ|/y) × 100`
   - Interpretation: Percentage error (scale-free)
   - Use when: Comparing across different SKUs
   - Units: Percentage (%)

4. **Bias (Mean Error)**
   - Formula: `mean(ŷ - y)`
   - **Positive Bias** (+): Overforecasting → Excess inventory
   - **Negative Bias** (−): Underforecasting → Stockouts!
   - **⚠️ Most dangerous metric:** Can hide in good MAE

**Results Table (sorted by RMSE):**
```
Model             MAE     RMSE    MAPE    Bias
Prophet          14.17   23.97    7.79   -0.81  ✅ Winner
XGBoost          18.05   25.16   10.57  -16.19
Naive            16.78   26.10    9.52   -3.55
Holt-Winters     18.49   30.22    9.94  -16.67
SARIMA           30.96   40.08   17.55  -30.89
Moving Avg       36.69   44.89   20.74  -36.69
Seasonal Naive   37.78   46.51   21.78  -37.02
```

**Key Insight:**
- Prophet won with **MAPE = 7.79%** (best accuracy)
- But notice: many models have **negative bias** (−15 to −37)
- This means they **systematically underforecast**
- Why? Test period is Nov-Dec = Q4 holiday season = 60% sales surge
- Models without yearly seasonality completely miss it!

**Visualization:**
- Bar charts comparing RMSE, MAPE, and Bias
- Forecast comparison plot: all 7 predictions vs actuals
- Best model plot: Prophet's predictions with confidence intervals

**Takeaway:** Bias matters more than total error. Underforecasting during peak seasons is catastrophic.

---

### 💡 **Key Insights** — What to Remember

**What you'll learn:**
- Why Prophet won
- Why seasonality structure determines the winner
- The operational danger of bias
- How to improve the project
- Resources for deeper learning

**The Core Lessons:**

1. **Seasonality Structure Wins**
   - Prophet captured yearly seasonality → won
   - Models without it lost (Naive, Seasonal Naive, basic SARIMA)
   - XGBoost won too because it had month/day_of_year features
   - **Lesson:** Always match model to data periodicity

2. **Bias is More Dangerous Than Error**
   - Negative bias (underforecasting) is operational nightmare
   - Means stockouts, lost sales, emergency expediting
   - Positive bias (overforecasting) means excess inventory
   - Low MAE doesn't hide bad bias
   - **Lesson:** Always check bias first

3. **Model Stability Over Single Window**
   - Evaluated on only one test period (Nov-Dec)
   - Real production needs walk-forward validation
   - Test at each step as time advances
   - **Lesson:** Validate like you'll deploy

4. **External Regressors Matter**
   - Could add: holiday calendar, marketing spend, competitor actions
   - Would improve predictions significantly
   - Prophet and XGBoost can handle them naturally
   - **Lesson:** Don't ignore domain knowledge

**Extensions to Try:**
1. Walk-forward validation (test stability over time)
2. Hyperparameter tuning (optimize each model)
3. External regressors (add business context)
4. Probabilistic forecasts (quantile predictions for safety stock)
5. Hierarchical forecasting (SKU → category → region)
6. Real data (swap synthetic for Kaggle M5 or Rossmann)
7. Business metrics (compute actual inventory cost impact)

**Recommended Reading:**
- *Forecasting: Principles & Practice* (Hyndman & Athanasopoulos) — canonical reference
- *Supply Chain Management* (Chopra & Meindl) — business context
- M5 Kaggle Competition Papers — real-world learnings

**Takeaway:** You now understand the complete demand forecasting pipeline. Apply it to real data next.

---

## Interactive Features

### Hover for Details
- Streamlit charts support hover tooltips
- Plotly charts (interactive): zoom, pan, hover for exact values

### Filter & Explore
- Sidebar controls let you navigate through sections
- Each page loads fresh data and recalculates

### Export Data
- Right-click dataframes to download as CSV
- Screenshots of plots work in your browser

---

## What Each Visualization Teaches

| Plot | What It Shows | Lesson |
|------|---------------|--------|
| Full Series | Complete 3-year timeline | Trend and seasonality are real and strong |
| Decomposition | Trend, seasonal, residual separately | Each component has a role; models must handle all |
| ACF/PACF | Autocorrelation at different lags | Lag-7 spike proves weekly seasonality; use for ARIMA tuning |
| Seasonal Patterns | Day-of-week, month, year effects | Multiple periodicities matter; simple models fail |
| Forecast Comparison | All 7 models vs actual test values | Winner didn't just have low MAE — it captured Q4 surge |
| Best Model (Prophet) | Prophet's predictions & confidence intervals | Good models are honest about uncertainty |

---

## Quick Reference: The Supply Chain Connection

**Why this project matters to supply chain:**

```
Demand Forecast
    ↓
Procurement Plan (order how much & when)
    ↓
Production Schedule (when to make it)
    ↓
Inventory Targets (safety stock, reorder points)
    ↓
Network Design (where to put warehouses)
    ↓
Financial Impact (carries costs, expediting fees, lost sales)
```

**A 1% MAPE improvement:**
- Walmart scale: saves $100M+
- Small company scale: saves $1M+
- Your company: calculate based on volume

**The Bias Trap:**
- Model says MAPE = 8%, looks good
- But bias = −25 (systematic underforecasting)
- You'll stock out every month
- Financial impact: worse than higher MAPE model with lower bias

---

## Troubleshooting

### App won't load at localhost:8501
```bash
# Check if port is in use
lsof -i :8501

# Kill Streamlit if stuck
pkill -f streamlit

# Restart
streamlit run app.py
```

### Plots won't display
- Ensure output files exist: `outputs/plots/*.png`
- Run the pipeline: `python 01_generate_data.py && python 02_eda.py && python 03_forecasting.py`

### Data not showing
- Check: `data/sales_data.csv` exists
- Check: `outputs/results.csv` and `outputs/forecasts.csv` exist
- Run: `python 01_generate_data.py` to regenerate

---

## Next Steps

1. ✅ Understand each section of the frontend
2. 📚 Read the recommended resources
3. 💻 Try the extensions (hyperparameter tuning, real data, external regressors)
4. 📊 Apply to your own dataset
5. 📈 Measure business impact (inventory cost, stockout reduction)

---

## Project Architecture

```
SupplyChainProject/
├── 01_generate_data.py      → Synthetic sales data
├── 02_eda.py                → Analysis & plots
├── 03_forecasting.py        → 7 models & metrics
├── app.py                   → ← YOU ARE HERE (Interactive Frontend)
├── requirements.txt         → Dependencies
├── data/
│   └── sales_data.csv       → Generated data
├── outputs/
│   ├── results.csv          → Model metrics
│   ├── forecasts.csv        → Predictions
│   └── plots/               → All visualizations
└── README.md                → Original docs
```

---

## Questions to Ask Yourself

As you explore each section, think about:

1. **Data Section:**
   - What patterns do you see?
   - Which component (trend, seasonality) is strongest?

2. **EDA Section:**
   - Why is stationarity important?
   - What does the ACF/PACF tell you about ARIMA order?

3. **Models Section:**
   - Which models could capture weekly seasonality?
   - Which could capture yearly seasonality?
   - Why does train-test order matter?

4. **Results Section:**
   - Why did Prophet win?
   - What does negative bias mean operationally?
   - Which metric would you optimize if you were a supply chain director?

5. **Insights Section:**
   - How would you add external regressors?
   - What data would you add if you could?
   - How would you measure financial impact?

---

**Happy learning! 📊**
