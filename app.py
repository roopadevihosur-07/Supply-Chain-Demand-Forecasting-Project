import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image

# Page config
st.set_page_config(
    page_title="Supply Chain Forecasting",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .section-header {
        font-size: 1.8rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 3px solid #1f77b4;
        padding-bottom: 0.5rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .flow-box {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 3px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    try:
        sales_data = pd.read_csv('data/sales_data.csv')
        sales_data['date'] = pd.to_datetime(sales_data['date'])
        results = pd.read_csv('outputs/results.csv')
        forecasts = pd.read_csv('outputs/forecasts.csv')
        return sales_data, results, forecasts
    except FileNotFoundError:
        st.error("Data files not found. Please run the pipeline first.")
        return None, None, None

# Load images
@st.cache_data
def load_images():
    plots_dir = Path('outputs/plots')
    images = {}
    for img_file in sorted(plots_dir.glob('*.png')):
        images[img_file.stem] = Image.open(img_file)
    return images

# Sidebar Navigation
st.sidebar.markdown("# 📚 Navigation")
page = st.sidebar.radio(
    "Select a section:",
    ["🏠 Overview", "📊 Data Generation", "🔍 Exploratory Analysis",
     "🤖 Forecasting Models", "📈 Results & Comparison", "💡 Key Insights"]
)

sales_data, results, forecasts = load_data()

if sales_data is None:
    st.stop()

images = load_images()

# ============================================================================
# PAGE 1: OVERVIEW
# ============================================================================
if page == "🏠 Overview":
    st.markdown('<div class="main-header">📊 Supply Chain Demand Forecasting Project</div>',
                unsafe_allow_html=True)

    st.markdown("""
    This is a complete **time-series forecasting pipeline** that demonstrates how to build,
    evaluate, and compare demand forecasting models for supply chain management.
    """)

    # Project Flow Diagram
    st.markdown('<div class="section-header">Project Pipeline Flow</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="flow-box">
            <h3>1️⃣ Data Generation</h3>
            <p>Create synthetic retail sales data with:</p>
            <ul>
                <li>Linear trend (+30 units/3 yrs)</li>
                <li>Weekly seasonality</li>
                <li>Yearly seasonality (Q4 peak)</li>
                <li>Random promotions</li>
                <li>Realistic noise</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="flow-box">
            <h3>2️⃣ EDA & Analysis</h3>
            <p>Understand the data:</p>
            <ul>
                <li>Summary statistics</li>
                <li>Stationarity testing</li>
                <li>Autocorrelation (ACF/PACF)</li>
                <li>Seasonal decomposition</li>
                <li>Visual patterns</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="flow-box">
            <h3>3️⃣ Model Comparison</h3>
            <p>Train 7 different models:</p>
            <ul>
                <li>Naive baselines</li>
                <li>Exponential smoothing</li>
                <li>ARIMA family</li>
                <li>Prophet (Meta)</li>
                <li>XGBoost ML</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # Key Concepts
    st.markdown('<div class="section-header">Why This Matters for Supply Chain</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("""
        **Forecast Accuracy**
        - Small improvements save millions
        - 1% MAPE improvement = huge cost savings
        - Scale matters: Walmart saves $100M+ per 1%
        """)

    with col2:
        st.warning("""
        **Forecast Bias**
        - Underforcasting → Stockouts
        - Overforcasting → Excess inventory
        - Often more dangerous than total error
        """)

    with col3:
        st.success("""
        **Model Selection**
        - Must beat naive baselines
        - Match seasonality structure
        - Consider operational constraints
        """)

    # Project Statistics
    st.markdown('<div class="section-header">Dataset Overview</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Days", f"{len(sales_data):,}")
    with col2:
        st.metric("Date Range", f"{sales_data['date'].min().date()} to {sales_data['date'].max().date()}")
    with col3:
        st.metric("Mean Daily Sales", f"{sales_data['sales'].mean():.1f} units")
    with col4:
        st.metric("Std Deviation", f"{sales_data['sales'].std():.1f} units")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Min Sales", f"{sales_data['sales'].min():.0f} units")
    with col2:
        st.metric("Max Sales", f"{sales_data['sales'].max():.0f} units")
    with col3:
        st.metric("Promo Days", f"{sales_data['promo'].sum():.0f} ({sales_data['promo'].mean()*100:.1f}%)")

# ============================================================================
# PAGE 2: DATA GENERATION
# ============================================================================
elif page == "📊 Data Generation":
    st.markdown('<div class="section-header">Data Generation Process</div>', unsafe_allow_html=True)

    st.markdown("""
    The synthetic dataset simulates realistic retail sales with multiple components:
    """)

    # Components explanation
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📈 Data Components")
        st.markdown("""
        - **Level**: Baseline sales around 135 units/day
        - **Trend**: Gradual increase of ~30 units over 3 years
        - **Seasonality**:
          - Weekly: Weekend peaks
          - Yearly: Q4 holiday lift (60%+ higher)
        - **Promotions**: ~30 random 3-day campaigns
        - **Noise**: Gaussian random variation
        """)

    with col2:
        st.subheader("📊 Statistics")
        stats_data = {
            'Metric': ['Count', 'Mean', 'Std Dev', 'Min', '25%', '50%', '75%', 'Max'],
            'Value': [
                f"{len(sales_data)}",
                f"{sales_data['sales'].mean():.2f}",
                f"{sales_data['sales'].std():.2f}",
                f"{sales_data['sales'].min():.0f}",
                f"{sales_data['sales'].quantile(0.25):.0f}",
                f"{sales_data['sales'].median():.0f}",
                f"{sales_data['sales'].quantile(0.75):.0f}",
                f"{sales_data['sales'].max():.0f}"
            ]
        }
        st.dataframe(pd.DataFrame(stats_data), use_container_width=True)

    # Full series visualization
    st.subheader("Full Time Series")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=sales_data['date'],
        y=sales_data['sales'],
        mode='lines',
        name='Sales',
        line=dict(color='#1f77b4', width=1.5),
        hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Sales: %{y:.0f}<extra></extra>'
    ))

    # Highlight promo days
    promo_data = sales_data[sales_data['promo'] == 1]
    fig.add_trace(go.Scatter(
        x=promo_data['date'],
        y=promo_data['sales'],
        mode='markers',
        name='Promotion Days',
        marker=dict(color='red', size=6, opacity=0.6),
        hovertemplate='<b>%{x|%Y-%m-%d}</b> (PROMO)<br>Sales: %{y:.0f}<extra></extra>'
    ))

    fig.update_layout(
        title='Complete Sales Time Series (2022-2024)',
        xaxis_title='Date',
        yaxis_title='Daily Sales (units)',
        hovermode='x unified',
        height=400,
        template='plotly_white'
    )
    st.plotly_chart(fig, use_container_width=True)

    # Raw data preview
    st.subheader("Data Sample (First 20 rows)")
    st.dataframe(sales_data.head(20), use_container_width=True)

    # Distribution plot
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Sales Distribution")
        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=sales_data['sales'],
            nbinsx=50,
            name='Sales',
            marker_color='#1f77b4'
        ))
        fig.update_layout(
            xaxis_title='Daily Sales',
            yaxis_title='Frequency',
            height=300,
            template='plotly_white'
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Sales by Day of Week")
        dow_sales = sales_data.groupby('day_of_week')['sales'].mean()
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=days,
            y=dow_sales.values,
            marker_color=['#1f77b4' if i < 5 else '#ff7f0e' for i in range(7)],
            text=[f'{v:.0f}' for v in dow_sales.values],
            textposition='auto',
        ))
        fig.update_layout(
            yaxis_title='Average Sales',
            height=300,
            template='plotly_white'
        )
        st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# PAGE 3: EXPLORATORY ANALYSIS
# ============================================================================
elif page == "🔍 Exploratory Analysis":
    st.markdown('<div class="section-header">Exploratory Data Analysis</div>', unsafe_allow_html=True)

    # Stationarity Test Results
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📋 Stationarity Test (ADF)")
        st.markdown("""
        **Augmented Dickey-Fuller Test Result:**
        - ADF Statistic: **-3.8978**
        - p-value: **0.0021**
        - Critical Value (5%): -2.8642

        ✅ **Series is STATIONARY** (reject H0)

        **Interpretation:**
        - Mean, variance are constant over time
        - Safe to use in ARIMA models without differencing
        - Trend and seasonality are manageable patterns
        """)

    with col2:
        st.info("""
        **Why Stationarity Matters:**
        - ARIMA assumes stationary data
        - Non-stationary data leads to spurious correlations
        - The ADF test checks for "unit root"
        - p-value < 0.05 means stationary
        - Our series is stationary → can use ARIMA safely
        """)

    # Display EDA plots
    st.markdown('<div class="section-header">Visualization Gallery</div>', unsafe_allow_html=True)

    if '01_full_series' in images:
        st.subheader("1️⃣ Full Series with Trend")
        st.image(images['01_full_series'], use_container_width=True)
        st.caption("Shows the complete 3-year time series with upward trend and seasonal pattern")

    if '02_decomposition' in images:
        st.subheader("2️⃣ Time Series Decomposition")
        st.image(images['02_decomposition'], use_container_width=True)
        st.caption("""
        **Components breakdown:**
        - **Original**: Raw data with all patterns
        - **Trend**: Long-term upward movement
        - **Seasonal**: Repeating weekly pattern
        - **Residual**: Noise and anomalies after removing trend & seasonality
        """)

    if '03_acf_pacf' in images:
        st.subheader("3️⃣ Autocorrelation Analysis (ACF/PACF)")
        st.image(images['03_acf_pacf'], use_container_width=True)
        st.markdown("""
        **ACF (Autocorrelation Function):**
        - Shows correlation at different lags
        - Significant spike at lag 7 → weekly seasonality
        - Gradual decline → trend component

        **PACF (Partial Autocorrelation):**
        - Direct correlation only
        - Helps determine AR order for ARIMA
        - Used to identify autoregressive relationships
        """)

    if '04_seasonal_patterns' in images:
        st.subheader("4️⃣ Seasonal Patterns")
        st.image(images['04_seasonal_patterns'], use_container_width=True)
        st.caption("""
        **Patterns observed:**
        - Weekly effect: Weekend peaks (Saturday-Sunday)
        - Monthly effect: Some monthly variation
        - Yearly effect: Strong Q4 peak (holiday season)
        - These patterns help models make better predictions
        """)

# ============================================================================
# PAGE 4: FORECASTING MODELS
# ============================================================================
elif page == "🤖 Forecasting Models":
    st.markdown('<div class="section-header">7 Forecasting Models</div>', unsafe_allow_html=True)

    st.markdown("We compare 7 models ranging from naive baselines to advanced ML techniques:")

    # Model descriptions
    models_info = {
        "Naive": {
            "description": "Predicts: last observed value",
            "pros": ["Simple baseline", "Fast"],
            "cons": ["Ignores seasonality", "No trend"],
            "when": "Baseline comparison only"
        },
        "Seasonal Naive": {
            "description": "Predicts: value from 7 days ago",
            "pros": ["Captures weekly seasonality", "Simple"],
            "cons": ["Misses yearly seasonality", "No trend"],
            "when": "Quick weekly forecasts"
        },
        "Moving Average": {
            "description": "Averages last N observations",
            "pros": ["Smooths noise", "Interpretable"],
            "cons": ["Slow to change", "Fixed window"],
            "when": "Noisy data smoothing"
        },
        "Holt-Winters": {
            "description": "Exponential smoothing: level + trend + seasonality",
            "pros": ["Captures all components", "Proven"],
            "cons": ["Can't use external regressors", "Parameter tuning"],
            "when": "Stable seasonal patterns"
        },
        "SARIMA": {
            "description": "ARIMA + seasonal ARIMA (p,d,q)×(P,D,Q,s)",
            "pros": ["Powerful autoregressive model", "Theoretical foundation"],
            "cons": ["Complex parameter selection", "Linear only"],
            "when": "High statistical rigor needed"
        },
        "Prophet": {
            "description": "Meta's decomposable: trend + seasonality + holidays",
            "pros": ["Handles changepoints", "Robust to outliers", "Easy to use"],
            "cons": ["Less suitable for short horizons"],
            "when": "Business time series with holidays"
        },
        "XGBoost": {
            "description": "Gradient-boosted trees with engineered features",
            "pros": ["Non-linear", "External regressors", "Flexible"],
            "cons": ["Needs feature engineering", "Black box", "Can't extrapolate"],
            "when": "Complex patterns with known features"
        }
    }

    # Display model cards
    cols = st.columns(2)
    for idx, (name, info) in enumerate(models_info.items()):
        with cols[idx % 2]:
            st.markdown(f"""
            <div class="metric-card">
                <h4>{name}</h4>
                <p><strong>{info['description']}</strong></p>
                <details>
                    <summary><strong>Pros & Cons</strong></summary>
                    <ul>
                        <li><strong>Pros:</strong> {', '.join(info['pros'])}</li>
                        <li><strong>Cons:</strong> {', '.join(info['cons'])}</li>
                        <li><strong>When to use:</strong> {info['when']}</li>
                    </ul>
                </details>
            </div>
            """, unsafe_allow_html=True)

    # Train/Test Split explanation
    st.markdown('<div class="section-header">Train-Test Split Strategy</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.warning("""
        **❌ WRONG: Random shuffle**
        - Breaks temporal order
        - Future data leaks to past
        - Unrealistic metrics
        - Models look better than they are
        """)

    with col2:
        st.success("""
        **✅ RIGHT: Chronological split**
        - Last N days = test set
        - Earlier data = training
        - Respects time direction
        - Realistic performance estimate
        """)

    # Show train/test timeline
    train_end = pd.to_datetime('2024-11-01')
    test_start = pd.to_datetime('2024-11-02')
    test_end = sales_data['date'].max()

    fig = go.Figure()

    # Training period
    train_mask = sales_data['date'] <= train_end
    fig.add_trace(go.Scatter(
        x=sales_data.loc[train_mask, 'date'],
        y=sales_data.loc[train_mask, 'sales'],
        mode='lines',
        name='Training Set',
        line=dict(color='#2ecc71', width=2),
    ))

    # Test period
    test_mask = sales_data['date'] >= test_start
    fig.add_trace(go.Scatter(
        x=sales_data.loc[test_mask, 'date'],
        y=sales_data.loc[test_mask, 'sales'],
        mode='lines',
        name='Test Set',
        line=dict(color='#e74c3c', width=2),
    ))

    fig.update_layout(
        title='Train-Test Split (Chronological)',
        xaxis_title='Date',
        yaxis_title='Daily Sales',
        height=350,
        template='plotly_white',
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Training Period", f"{train_mask.sum()} days")
    with col2:
        st.metric("Test Period", f"{test_mask.sum()} days")
    with col3:
        st.metric("Split Date", "2024-11-01")

# ============================================================================
# PAGE 5: RESULTS & COMPARISON
# ============================================================================
elif page == "📈 Results & Comparison":
    st.markdown('<div class="section-header">Model Performance Results</div>', unsafe_allow_html=True)

    # Results table
    st.subheader("Metrics Comparison (sorted by RMSE)")
    results_display = results.copy()
    results_display['Rank'] = range(1, len(results_display) + 1)
    st.dataframe(
        results_display[['Rank', 'model', 'MAE', 'RMSE', 'MAPE (%)', 'Bias']],
        use_container_width=True,
        hide_index=True
    )

    # Metrics explanation
    st.markdown('<div class="section-header">Understanding the Metrics</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("""
        **MAE (Mean Absolute Error)**
        - Average absolute error
        - Same units as data
        - Formula: mean(|y - ŷ|)
        - Best for: Interpretability
        - Lower is better
        """)

    with col2:
        st.info("""
        **RMSE (Root Mean Sq Error)**
        - Penalizes large errors more
        - Same units as data
        - Formula: √mean((y - ŷ)²)
        - Best for: Stockout costs
        - Lower is better
        """)

    with col3:
        st.info("""
        **MAPE (Mean Absolute % Error)**
        - Percentage error
        - Scale-free (good for comparison)
        - Formula: mean(|y - ŷ|/y) × 100
        - Best for: Comparing SKUs
        - Lower is better
        """)

    col1, col2 = st.columns(2)
    with col1:
        st.warning("""
        **Bias (Mean Error)**
        - Are we over/underforcasting?
        - Formula: mean(ŷ - y)
        - Positive bias: Overforecasting
        - Negative bias: Underforecasting
        - **Most dangerous metric!**
        """)

    with col2:
        st.success("""
        **Why Bias Matters**
        - Positive bias → Excess inventory
        - Negative bias → Stockouts, lost sales
        - Can hide in low MAE/RMSE
        - Operational impact > statistical error
        - Always check bias first
        """)

    # Performance visualization
    st.markdown('<div class="section-header">Visual Comparison</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        # RMSE comparison
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=results.sort_values('RMSE')['model'],
            y=results.sort_values('RMSE')['RMSE'],
            marker_color=['#27ae60' if i == 0 else '#3498db' for i in range(len(results))],
            text=[f"{v:.1f}" for v in results.sort_values('RMSE')['RMSE']],
            textposition='auto',
        ))
        fig.update_layout(
            title='RMSE by Model (Lower is Better)',
            yaxis_title='RMSE',
            xaxis_title='Model',
            height=350,
            template='plotly_white',
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # MAPE comparison
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=results.sort_values('MAPE (%)')['model'],
            y=results.sort_values('MAPE (%)')['MAPE (%)'],
            marker_color=['#27ae60' if i == 0 else '#3498db' for i in range(len(results))],
            text=[f"{v:.1f}%" for v in results.sort_values('MAPE (%)')['MAPE (%)']],
            textposition='auto',
        ))
        fig.update_layout(
            title='MAPE by Model (Lower is Better)',
            yaxis_title='MAPE (%)',
            xaxis_title='Model',
            height=350,
            template='plotly_white',
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

    # Bias analysis
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Bias Analysis (Overfcast vs Underfcast)")
        fig = go.Figure()
        colors = ['#e74c3c' if x < 0 else '#3498db' for x in results['Bias']]
        fig.add_trace(go.Bar(
            x=results.sort_values('Bias')['model'],
            y=results.sort_values('Bias')['Bias'],
            marker_color=colors,
            text=[f"{v:.1f}" for v in results.sort_values('Bias')['Bias']],
            textposition='auto',
        ))
        fig.add_hline(y=0, line_dash="dash", line_color="black")
        fig.update_layout(
            title='Bias by Model',
            yaxis_title='Bias (Mean Error)',
            xaxis_title='Model',
            height=350,
            template='plotly_white',
            annotations=[
                dict(text='Underfcast →', x=0.02, y=0.98, xref='paper', yref='paper',
                     showarrow=False, bgcolor='#ffe8e8', bordercolor='#e74c3c', borderwidth=1),
                dict(text='Overfcast →', x=0.98, y=0.98, xref='paper', yref='paper',
                     showarrow=False, bgcolor='#e8f4ff', bordercolor='#3498db', borderwidth=1, xanchor='right')
            ]
        )
        st.plotly_chart(fig, use_container_width=True)

    with col1:
        st.markdown("""
        **Key Insight:**

        Most models show **negative bias** (-15 to -37), meaning they
        **systematically underforecast**. Why?

        The test set (Nov-Dec) includes Q4 holiday season:
        - Sales surge 60%+ above normal
        - Models without yearly seasonality miss it
        - Prophet captures it → wins!

        **Lesson:** Match model seasonality structure to data
        """)

    # Forecast comparison plot
    st.markdown('<div class="section-header">Forecast Comparison</div>', unsafe_allow_html=True)
    if '05_forecast_comparison' in images:
        st.image(images['05_forecast_comparison'], use_container_width=True)
        st.caption("All 7 models' predictions vs actual test values (Nov-Dec 2024)")

# ============================================================================
# PAGE 6: KEY INSIGHTS
# ============================================================================
elif page == "💡 Key Insights":
    st.markdown('<div class="section-header">Key Learnings & Insights</div>', unsafe_allow_html=True)

    # Winner announcement
    st.success("""
    🏆 **WINNER: Prophet**
    - MAPE: 7.79% (best accuracy)
    - RMSE: 23.97
    - Bias: -0.81 (nearly unbiased)
    """)

    # Key insights
    st.markdown('<div class="section-header">1. Why Prophet Won</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **Prophet's Advantages:**
        - Explicitly models **yearly seasonality** by default
        - Includes **changepoint detection** for trend shifts
        - **Robust to outliers** (holiday spikes)
        - Decomposes: trend + seasonality + holidays
        - Easy to add external regressors
        """)

    with col2:
        st.image(images['06_best_model'] if '06_best_model' in images else None,
                use_container_width=True)
        st.caption("Prophet's forecast on test set with confidence intervals")

    # Lesson about seasonality
    st.markdown('<div class="section-header">2. Seasonality Structure Determines Winner</div>',
                unsafe_allow_html=True)

    comparison_data = {
        'Model': ['Prophet', 'XGBoost', 'Seasonal Naive', 'SARIMA'],
        'Weekly Seasonality': ['✅', '✅ (day_of_week)', '✅', '✅'],
        'Yearly Seasonality': ['✅', '✅ (month, day_of_year)', '❌', '⚠️ (extra tuning)'],
        'Captured Q4 Surge': ['✅ Yes', '✅ Yes', '❌ No', '❌ No'],
        'MAPE': [7.79, 10.57, 21.78, 17.55]
    }

    st.dataframe(pd.DataFrame(comparison_data), use_container_width=True)

    st.warning("""
    **Key Insight:** The test period (Nov-Dec) is Q4 holiday season with 60%+ sales surge.

    Models that don't capture **yearly seasonality** systematically underforecast and lose.

    **Lesson for real projects:**
    - Audit your data for ALL relevant seasonalities (daily, weekly, monthly, yearly)
    - Choose models that can represent those periodicities
    - Don't assume weekly seasonality is enough
    """)

    # Bias lesson
    st.markdown('<div class="section-header">3. Bias is More Dangerous Than Error</div>',
                unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.error("""
        **Negative Bias Problem (Most models)**

        Bias: -15 to -37 units/day

        **Operational Impact:**
        - Regularly run out of stock
        - Lost sales, angry customers
        - Need emergency expediting
        - Carries huge costs

        MAE might be reasonable, but bias hides the real problem!
        """)

    with col2:
        st.info("""
        **Why This Happens**

        Underforecasting in Q4 is catastrophic:
        - Can't suddenly produce enough stock
        - Procurement is already locked in
        - Expediting fees are expensive
        - Lost sales = lost revenue

        **Better to overestimate for seasonal peaks**
        than to underestimate (inventory > lost sales)
        """)

    # Extensions
    st.markdown('<div class="section-header">4. How to Make This Better</div>',
                unsafe_allow_html=True)

    st.markdown("""
    1. **Add walk-forward validation** — measure stability over time, not just one test window
    2. **Hyperparameter tuning** — optimize SARIMA, XGBoost with systematic grid search
    3. **External regressors** — add holiday calendars, marketing spend, competitor actions
    4. **Probabilistic forecasts** — quantile predictions for safety stock calculations
    5. **Hierarchical forecasting** — forecast at SKU level, reconcile to category/region
    6. **Real data** — swap synthetic data for Kaggle competitions or real retail datasets
    7. **Business metrics** — compute inventory cost, stockout cost, safety stock needed
    """)

    # Recommended reading
    st.markdown('<div class="section-header">Recommended Learning Resources</div>',
                unsafe_allow_html=True)

    resources = {
        'Book': [
            'Forecasting: Principles & Practice (Hyndman)',
            'Supply Chain Management (Chopra & Meindl)',
            'Deep Learning for Time Series (Bengio et al.)'
        ],
        'Competition': [
            'M5 Forecasting (Kaggle)',
            'Rossmann Store Sales',
            'Corporación Favorita'
        ],
        'Concept': [
            'ARIMA/SARIMA models',
            'Prophet documentation',
            'Time series cross-validation'
        ]
    }

    for category, items in resources.items():
        with st.expander(f"📚 {category}"):
            for item in items:
                st.write(f"• {item}")

    # Summary
    st.markdown('<div class="section-header">Summary: What You Now Understand</div>',
                unsafe_allow_html=True)

    st.success("""
    ✅ **Supply Chain Concepts**
    - Why demand forecasting drives everything downstream
    - How forecast accuracy translates to cost savings
    - Why bias is operationally dangerous

    ✅ **Time Series Analysis**
    - How to decompose series into components
    - Stationarity testing and differencing
    - ACF/PACF for model selection

    ✅ **Model Selection**
    - When to use naive, exponential smoothing, ARIMA, Prophet, XGBoost
    - How to match model structure to data patterns
    - The importance of proper train/test splitting

    ✅ **Metrics & Evaluation**
    - MAE, RMSE, MAPE — when to use each
    - Why bias matters more than total error
    - How to validate models realistically

    **Next Steps:** Apply these concepts to real data!
    """)

st.sidebar.markdown("---")
st.sidebar.markdown("""
### 📊 Project Info
**Demand Forecasting Pipeline**
- 3 years of synthetic retail data
- 7 forecasting models
- Complete EDA analysis
- Real-world supply chain lessons

**Tech Stack:**
- Python, Pandas, Statsmodels
- Prophet, XGBoost, Scikit-learn
- Streamlit (this dashboard!)

**Built for:** Learning & understanding
""")
