# 🎯 Interactive Dashboard - Learn Supply Chain Demand Forecasting

## Quick Start (30 seconds)

### Option 1: Run the launcher script
```bash
cd /Users/roopakeerthiraj/Documents/SupplyChainProject
bash start_app.sh
```

### Option 2: Direct command
```bash
cd /Users/roopakeerthiraj/Documents/SupplyChainProject
streamlit run app.py
```

**Then open your browser to:** http://localhost:8501

---

## What You'll Learn (Complete Learning Path)

This interactive frontend is designed as a **learning journey** with 6 progressive sections. Each builds on the previous one.

```
🏠 OVERVIEW
   ↓ (Why does this matter?)
📊 DATA GENERATION
   ↓ (What patterns are in the data?)
🔍 EXPLORATORY ANALYSIS
   ↓ (How do we understand the patterns?)
🤖 FORECASTING MODELS
   ↓ (Which model captures what?)
📈 RESULTS & COMPARISON
   ↓ (Who won and why?)
💡 KEY INSIGHTS
   ✅ Complete understanding of demand forecasting
```

---

## Section Breakdown: What to Focus On

### 1️⃣ **🏠 Overview** (5 min read)
**Big Picture Questions:**
- "Why should I care about demand forecasting?"
- "What does a forecasting project look like?"
- "How does this connect to supply chain?"

**Key Takeaways:**
- ✅ Forecasting drives procurement, inventory, and network design
- ✅ 1% MAPE improvement = millions in savings (Walmart scale)
- ✅ Small forecast errors compound into huge supply chain problems
- ✅ Dataset: 3 years, 1,096 days, mean sales = 135 units/day

**Interactive Elements:**
- View dataset statistics
- See the complete pipeline flow

---

### 2️⃣ **📊 Data Generation** (10 min explore)
**Questions to Answer:**
- "What does realistic sales data look like?"
- "What patterns should a model capture?"
- "How does promotional activity affect sales?"

**Key Learnings:**
- ✅ Real retail data has **multiple overlapping patterns**:
  - **Trend:** Upward growth over time (+30 units/3 years)
  - **Weekly seasonality:** Weekends = 20-30% higher sales
  - **Yearly seasonality:** Q4 holidays = 60% surge above baseline
  - **Promotions:** Random 3-day campaigns (7.9% of days)
  - **Noise:** Random variation (±30 units)

- ✅ Any model that ignores even ONE pattern will fail
- ✅ The data generator reveals what makes retail realistic

**Interactive Charts:**
- Full time series with trend line
- Promotion days highlighted in red
- Day-of-week sales breakdown (notice weekend peaks)
- Sales distribution histogram

**Hands-on:**
- Hover over the time series to see exact dates/values
- Zoom in to see daily patterns vs yearly patterns
- Notice how the data never feels static

---

### 3️⃣ **🔍 Exploratory Analysis** (15 min study)
**Questions to Answer:**
- "What is stationarity and why does it matter?"
- "How do I detect patterns in time series?"
- "What do ACF/PACF plots tell me?"

**Key Learnings:**
- ✅ **Stationarity Test (ADF):**
  - Null hypothesis: Series has a unit root (non-stationary)
  - Our p-value: 0.0021 < 0.05 → **REJECT null** → Series is STATIONARY
  - Implication: Safe to use ARIMA models without differencing
  - Real impact: Determines whether we need d=0 or d=1 in ARIMA

- ✅ **Time Series Decomposition** shows 4 components:
  - **Original:** Raw data (all patterns mixed)
  - **Trend:** Long-term movement (clearly upward)
  - **Seasonal:** Repeating pattern (weekly spikes, Q4 surge)
  - **Residual:** Leftover noise and anomalies

- ✅ **ACF/PACF Interpretation:**
  - **ACF (Autocorrelation Function):** correlation with lags
    - Spike at lag 7 = **weekly seasonality**
    - Gradual decline = **trend present**
    - Use: Identify MA order (q parameter) for ARIMA
  - **PACF (Partial Autocorrelation):** direct effect only
    - Cuts off sharply = **AR process**
    - Use: Identify AR order (p parameter) for ARIMA

- ✅ **Seasonal Patterns:**
  - Day of week: Strong effect (weekends peak)
  - Month: Slight variation
  - Year: Huge effect (Q4 = holiday season)

**Critical Insight:**
> If a model doesn't capture seasonality at ALL observed frequencies, it will fail during those periods. Moving Average and Seasonal Naive both fail in Q4 because they don't know about yearly seasonality.

**Visualizations to Study:**
1. Decomposition plot: mentally map how trend + seasonal + residual combine into original
2. ACF/PACF: find the lag-7 spike (weekly), see how it decays
3. Seasonal patterns: notice Q4 surge is ~60% above baseline

---

### 4️⃣ **🤖 Forecasting Models** (20 min deep dive)
**Questions to Answer:**
- "What's the difference between these models?"
- "When should I use each one?"
- "Why does train-test splitting matter?"

**The 7 Models Explained:**

#### Baseline Models (sanity checks):
- **Naive:** Predict = yesterday's sales
  - Pros: Simplest possible
  - Cons: Ignores everything
  - When: Use as minimum bar. If your complex model can't beat this, you wasted effort.

- **Seasonal Naive:** Predict = same day last week
  - Pros: Captures weekly seasonality
  - Cons: Completely misses yearly seasonality (fails in Q4!)
  - When: Quick weekly forecasts for short horizons

#### Smoothing Methods:
- **Moving Average:** Average of last N days
  - Pros: Reduces noise
  - Cons: Fixed window, slow to react
  - When: Preliminary smoothing before deeper analysis

- **Holt-Winters:** Exponential smoothing with level, trend, seasonality
  - Pros: Captures all components, proven method
  - Cons: Can't use external data, parameters need tuning
  - When: Stable patterns, no external regressors needed

#### Autoregressive Methods:
- **SARIMA:** (p,d,q)×(P,D,Q,s) — Autoregression + Integrated + MA + Seasonal
  - Pros: Theoretically grounded, powerful, interpretable parameters
  - Cons: Complex parameter selection (need auto_arima), linear only
  - When: High statistical rigor needed, academic papers

#### Decomposable Methods:
- **Prophet:** Additive model: trend + seasonality + holidays
  - Pros: Automatic changepoint detection, multiple seasonalities, robust to outliers
  - Cons: Less suitable for very short horizons
  - When: Business data with holidays and known seasonalities (retail, e-commerce)

#### Machine Learning:
- **XGBoost:** Gradient-boosted trees with engineered features
  - Pros: Non-linear, handles external regressors naturally, powerful
  - Cons: Black box, needs careful feature engineering, can't extrapolate
  - When: Complex patterns, lots of external data (weather, price, etc)

**Train-Test Split Lesson:**
- ❌ **Random shuffle:** Leaks future data to past → unrealistically good metrics
- ✅ **Chronological:** Last 60 days = test, earlier = training → realistic
- Why: Time has direction. Using future to predict past violates causality.
- Real validation: **Walk-forward** (test at each time step, retrain as you go)

**The Trade-off:**
```
Simple Models (Naive, Moving Avg)
    ↑
    │ Easy to explain & debug
    │ Fast to train
    │ Clear what went wrong
    │
    ├─── Moderate (HW, ARIMA, Prophet) ───┤
    │                                       │
    │ Better accuracy                    More complex
    │ Capture more patterns              Harder to tune
    │ Still interpretable                Slower computation
    │
    ↓
Complex Models (XGBoost, Neural Nets)
    ↑
    Highest potential accuracy
    Can learn non-linear patterns
    Requires lots of data & features
    Black box (hard to debug)
```

---

### 5️⃣ **📈 Results & Comparison** (15 min analysis)
**Questions to Answer:**
- "Which model is actually best?"
- "What do these metrics mean in real terms?"
- "Why did one model win?"

**Understanding the Metrics:**

| Metric | Formula | What It Measures | Real Example |
|--------|---------|-----------------|--------------|
| **MAE** | mean(\|y - ŷ\|) | Average error in units | "Off by 15 units on average" |
| **RMSE** | √mean((y-ŷ)²) | Penalizes large errors | "1 big miss = worse than 2 small ones" |
| **MAPE** | mean(\|y-ŷ\|/y)×100 | Percentage error | "7.8% off" (scale-free) |
| **Bias** | mean(ŷ - y) | Systematic over/underforecasting | "Consistently off by -25 units" |

**Critical Insight About Bias:**
```
Model A: MAPE = 8%, Bias = -30 units/day
Model B: MAPE = 10%, Bias = -2 units/day

Which is better for supply chain?
Model B! Here's why:

Model A: Consistently understocks by 30 units/day
├─ Stockouts regularly
├─ Lost sales, unhappy customers
├─ Emergency expediting (expensive)
└─ Financial impact: MASSIVE

Model B: Slightly worse accuracy, but nearly unbiased
├─ Stock is usually right
├─ Occasional small stockouts/overstock
├─ Can be managed with safety stock
└─ Financial impact: Minimal

LESSON: Bias matters more than accuracy.
```

**Who Won and Why?**

```
RESULTS:
Prophet          MAPE: 7.79%   Bias: -0.81   ← WINNER 🏆
XGBoost          MAPE: 10.57%  Bias: -16.19
Naive            MAPE: 9.52%   Bias: -3.55
HoltWinters      MAPE: 9.94%   Bias: -16.67
SARIMA           MAPE: 17.55%  Bias: -30.89
Moving Avg       MAPE: 20.74%  Bias: -36.69
Seasonal Naive   MAPE: 21.78%  Bias: -37.02
```

**Why did Prophet win?**

The test period is **Nov-Dec 2024** = Q4 holiday season.

Sales surge 60%+ above baseline in Q4.

```
Seasonal Naive says: "Predict last week's sales"
├─ Last week of Oct: ~130 units
├─ But Q4: ~210 units
└─ Misses surge completely → Huge underforecasting

Moving Avg says: "Average last 7 days"
├─ Working from pre-Q4 data
├─ No concept of yearly patterns
└─ Predicts ~135 units in Q4 → Way off

SARIMA says: "Use AR/MA/seasonal patterns"
├─ Seasonal order: only weekly (s=7)
├─ No yearly seasonality component
└─ Models seasonal but not yearly → Underforcasts Q4

Prophet says: "I model trend + seasonality + holidays"
├─ Explicitly includes yearly seasonality
├─ Can see "every December is higher"
├─ Captures Q4 surge
└─ Wins! MAPE: 7.79%

XGBoost (second place) uses features:
├─ day_of_week, month, day_of_year
├─ Learns from data: "month=12 means high sales"
├─ Captures Q4 pattern
└─ MAPE: 10.57% (good, but not as good as Prophet)
```

**The Big Lesson:**
> Your forecasting model is **only as good as the seasonality it can represent**. Add Prophet's built-in yearly seasonality, or add XGBoost's month/day-of-year features, and accuracy skyrockets. Ignore that Q4 surge, and your model fails.

**Interactive Visualizations:**
- RMSE bar chart: sorted by accuracy
- MAPE bar chart: percentage errors
- Bias chart: see which models over/underforecast
- Forecast comparison: all 7 predictions vs actuals

---

### 6️⃣ **💡 Key Insights** (10 min reflection)
**Questions to Answer:**
- "What are the operational lessons?"
- "What would make this better?"
- "How do I apply this to real projects?"

**Three Critical Insights:**

**1. Seasonality Structure Determines the Winner**
```
Data has: weekly + yearly seasonality
Test period: Q4 (yearly peak)

Models with ONLY weekly seasonality:
├─ Seasonal Naive (only weekly)
├─ Moving Avg (no seasonality)
├─ SARIMA(p,d,q)×(P,D,Q,7) with no yearly component
└─ Result: FAIL in Q4, MAPE > 17%

Models with BOTH weekly + yearly seasonality:
├─ Prophet (explicit yearly seasonality)
├─ XGBoost (month, day_of_year features)
└─ Result: SUCCEED in Q4, MAPE < 11%

PRINCIPLE: Inspect your data for ALL frequencies.
Match your model's representational capacity to those frequencies.
If data has it and model can't represent it, model loses.
```

**2. Bias is More Dangerous Than Total Error**
```
Scenario: Holiday season (reality)
Actual sales: 200 units/day

Forecast Model A:
├─ Prediction: 190 units/day
├─ Error: 10 units (MAE = 10)
├─ But bias: -10 (consistent underforecasting)
├─ Operational impact: UNDERBUY → Stockouts
└─ You lose sales, customers go to competitors

Forecast Model B:
├─ Prediction: 210 units/day
├─ Error: 10 units (same MAE!)
├─ But bias: +10 (consistent overforecasting)
├─ Operational impact: OVERBUY → Excess inventory
└─ You hold extra stock, pay carrying costs

Which is worse for supply chain?
Typically: Model A (stockouts > carrying cost)
But depends on your business margins.

THE LESSON: Always check bias first.
It tells you if your forecast is systematically off.
A low MAE with high negative bias is a TRAP.
```

**3. Test Set Matters for Conclusions**
```
Our test set: Nov-Dec (Q4, highest season)
Our conclusion: Prophet best for this data

But what if we tested Jan-Mar?
├─ No holidays
├─ Lower, more stable sales
├─ Seasonal Naive might perform better
├─ Prophet's holiday features wouldn't help

THE LESSON: Test on representative data.
Use walk-forward validation (test at multiple points).
Models that win in one season might fail in another.
```

**How to Make This Better:**

| Enhancement | Impact | Difficulty |
|-------------|--------|-----------|
| **Walk-forward validation** | Test at each month → see stability | Medium |
| **Hyperparameter tuning** | Optimize each model → squeeze accuracy | Medium |
| **External regressors** | Add promotions, weather, price → better features | High |
| **Probabilistic forecasts** | Output quantiles (p10, p50, p90) → feeds into safety stock | Medium |
| **Hierarchical forecasting** | Forecast SKU → category → region → reconcile | High |
| **Real data** | Swap synthetic for Kaggle M5 or Rossmann | Medium |
| **Business metrics** | Compute inventory cost, stockout cost → real impact | High |

**Real-World Application:**

If this were your company:
1. **Today:** Use Prophet (proven winner)
2. **Week 1:** Add walk-forward validation
3. **Week 2:** Add holiday calendar as external regressor
4. **Week 3:** Benchmark: which model saves more money?
5. **Month 2:** Retrain weekly as new data arrives
6. **Month 3:** Measure actual stockout reduction vs baseline
7. **Q2:** If good, expand to all SKUs
8. **Q3:** Add seasonal adjustment for promotions
9. **Year 2:** Integrate with safety stock optimization

---

## Learning Outcomes

After going through all 6 sections, you understand:

### ✅ Supply Chain Fundamentals
- [ ] Why demand forecasting is the foundation of supply chain
- [ ] How forecast accuracy translates to cost savings
- [ ] The operational impact of forecast bias
- [ ] How forecasts inform inventory, procurement, and network design

### ✅ Time Series Analysis
- [ ] How to decompose a time series into components
- [ ] What stationarity is and how to test for it
- [ ] How to read ACF/PACF plots
- [ ] How to identify seasonality at different frequencies

### ✅ Model Selection
- [ ] When to use naive, exponential smoothing, ARIMA, Prophet, XGBoost
- [ ] How to match model structure to data patterns
- [ ] Why train-test splitting matters for time series
- [ ] The importance of walk-forward validation

### ✅ Performance Metrics
- [ ] Difference between MAE, RMSE, MAPE, Bias
- [ ] When to use each metric
- [ ] Why bias is often more important than total error
- [ ] How to interpret results in real business terms

### ✅ Real-World Application
- [ ] How to structure a forecasting project
- [ ] What to check when models fail
- [ ] How to improve from baseline to production
- [ ] Where to find data and resources to continue learning

---

## Practice Questions

Use these to test your understanding:

1. **Data Section:** Why would a moving average model fail in Q4? (Answer: No concept of yearly seasonality)

2. **EDA Section:** What does a p-value < 0.05 in the ADF test mean? (Answer: Series is stationary, safe for ARIMA)

3. **Models Section:** Why is random shuffling bad for time series train-test splits? (Answer: Leaks future data to past, breaks causality)

4. **Results Section:** Model A has MAPE=8% with Bias=−25. Model B has MAPE=10% with Bias=−2. Which would you choose? Why? (Answer: B, because consistent underforecasting is catastrophic)

5. **Insights Section:** Why did Prophet win this project but might fail on different data? (Answer: Because test period was Q4 with yearly seasonality spike. If tested on stable months, might not win)

---

## Next Steps

1. ✅ **Explore the dashboard** — go through each section at your own pace
2. 📚 **Read the recommended resources** — deepen your understanding
3. 💻 **Try the extensions** — hyperparameter tuning, add external regressors
4. 🧪 **Apply to your own data** — take what you learned and use it
5. 📊 **Measure impact** — compute the financial benefit of better forecasts

---

## Quick Reference

### To Start the App:
```bash
cd /Users/roopakeerthiraj/Documents/SupplyChainProject
streamlit run app.py
```

### To Stop the App:
Press `Ctrl+C` in the terminal

### To Regenerate Data/Plots:
```bash
python 01_generate_data.py    # Create data
python 02_eda.py              # Generate plots
python 03_forecasting.py      # Train models
```

### To View This Guide:
```bash
cat FRONTEND_GUIDE.md      # Detailed section guides
cat DASHBOARD_README.md    # This file
```

---

**Ready to learn? Open http://localhost:8501 and start with the Overview section! 📊**
