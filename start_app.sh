#!/bin/bash

# Supply Chain Demand Forecasting - Frontend Launcher

echo "🚀 Supply Chain Demand Forecasting Dashboard"
echo "=============================================="
echo ""

# Check if data files exist
if [ ! -f "data/sales_data.csv" ]; then
    echo "⚠️  Data files not found. Running pipeline first..."
    echo ""
    python 01_generate_data.py
    python 02_eda.py
    python 03_forecasting.py
    echo ""
    echo "✅ Pipeline complete!"
    echo ""
fi

echo "📊 Launching Streamlit app..."
echo ""
echo "   🔗 Open your browser at: http://localhost:8501"
echo ""
echo "   Navigation Guide:"
echo "   ├─ 🏠 Overview (project flow)"
echo "   ├─ 📊 Data Generation (understanding the data)"
echo "   ├─ 🔍 Exploratory Analysis (EDA & patterns)"
echo "   ├─ 🤖 Forecasting Models (7 models explained)"
echo "   ├─ 📈 Results & Comparison (who won)"
echo "   └─ 💡 Key Insights (lessons learned)"
echo ""
echo "   Press Ctrl+C to stop the app"
echo ""
echo "=============================================="
echo ""

streamlit run app.py --server.headless=false
