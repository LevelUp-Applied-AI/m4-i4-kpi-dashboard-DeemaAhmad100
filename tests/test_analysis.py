"""Tests for the KPI dashboard analysis."""

import pytest
import pandas as pd
from analysis import connect_db, extract_data, compute_kpis, run_statistical_tests


def test_extraction_returns_dataframes():
    """Connect to the database, extract data, and verify the result is a dict of DataFrames."""
    engine = connect_db()
    data_dict = extract_data(engine)
    
    # Check it's a dictionary
    assert isinstance(data_dict, dict), "extract_data should return a dictionary"
    
    # Check it contains the 4 expected tables + df
    expected_keys = ["customers", "products", "orders", "order_items", "df"]
    for key in expected_keys:
        assert key in data_dict, f"Missing key: {key}"
    
    # Check all values are pandas DataFrames
    for key, df in data_dict.items():
        assert isinstance(df, pd.DataFrame), f"{key} should be a pandas DataFrame"
    
    # Check we have cleaned data (no cancelled orders, no quantity > 100)
    assert (data_dict["orders"]["status"] != "cancelled").all(), "Cancelled orders were not filtered"
    assert (data_dict["order_items"]["quantity"] <= 100).all(), "Quantities > 100 were not filtered"


def test_kpi_computation_returns_expected_keys():
    """Compute KPIs and verify the result contains all expected KPI names."""
    engine = connect_db()
    data = extract_data(engine)
    kpis = compute_kpis(data)
    
    # Check it's a dictionary
    assert isinstance(kpis, dict), "compute_kpis should return a dictionary"
    
    # Your 5 KPIs + supporting data
    expected_keys = [
        "total_revenue",
        "revenue_by_city",
        "monthly_revenue",
        "mom_growth",
        "revenue_by_category",
        "df",
        "order_value"
    ]
    
    for key in expected_keys:
        assert key in kpis, f"Missing KPI key: {key}"
    
    # Check total_revenue is a number
    assert isinstance(kpis["total_revenue"], (int, float)), "total_revenue should be numeric"


def test_statistical_test_returns_pvalue():
    """Run statistical tests and verify results include p-values."""
    engine = connect_db()
    data = extract_data(engine)
    results = run_statistical_tests(data)
    
    assert isinstance(results, dict), "run_statistical_tests should return a dictionary"
    assert len(results) >= 2, "Should run at least 2 statistical tests"
    
    # Check at least one test has a p-value
    has_pvalue = False
    for test_name, result in results.items():
        if "p_value" in result:
            pval = result["p_value"]
            assert isinstance(pval, (int, float)), f"p_value in {test_name} should be numeric"
            assert 0 <= pval <= 1, f"p_value in {test_name} should be between 0 and 1"
            has_pvalue = True
    
    assert has_pvalue, "At least one test should return a p-value"


# ====================== Additional Basic Checks ======================

from pathlib import Path

def test_analysis_script_exists():
    assert Path("analysis.py").exists(), "analysis.py not found"


def test_analysis_script_has_functions():
    """Verify analysis.py defines the required function signatures."""
    content = Path("analysis.py").read_text()
    required = ["def connect_db", "def extract_data", "def compute_kpis",
                "def run_statistical_tests", "def create_visualizations", "def create_interactive_dashboard", "def main"]
    for func in required:
        assert func in content, f"analysis.py is missing function: {func}"


def test_kpi_framework_exists():
    path = Path("kpi_framework.md")
    assert path.exists(), "kpi_framework.md not found"
    content = path.read_text()
    assert len(content) > 400, "kpi_framework.md appears too short — make sure all 5 KPIs are filled"


def test_executive_summary_exists():
    path = Path("EXECUTIVE_SUMMARY.md")
    assert path.exists(), "EXECUTIVE_SUMMARY.md not found"
    content = path.read_text()
    assert len(content) > 300, "EXECUTIVE_SUMMARY.md appears too short"


def test_schema_and_seed_present():
    assert Path("schema.sql").exists(), "schema.sql not found"
    assert Path("seed_data.sql").exists(), "seed_data.sql not found"

    # -------------------------------
# Tier 1: Interactive Dashboard with Plotly
# -------------------------------
def create_interactive_dashboard(kpis):
    """Create an interactive Plotly dashboard and save as HTML"""
    import plotly.express as px
    from plotly.subplots import make_subplots
    import plotly.graph_objects as go
    
    df = kpis["df"]
    
    # Create a 2x2 subplot figure
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "Monthly Revenue Trend",
            "Month-over-Month Growth",
            "Revenue by Product Category",
            "Revenue by City"
        ),
        vertical_spacing=0.15,
        horizontal_spacing=0.1
    )

    # 1. Monthly Revenue Trend (Line)
    monthly = kpis["monthly_revenue"].reset_index()
    monthly["order_month"] = monthly["order_month"].astype(str)
    fig.add_trace(
        go.Scatter(x=monthly["order_month"], y=monthly["revenue"], 
                   mode='lines+markers', name="Monthly Revenue"),
        row=1, col=1
    )

    # 2. MoM Growth (Bar)
    mom = kpis["mom_growth"].reset_index()
    mom["order_month"] = mom["order_month"].astype(str)
    fig.add_trace(
        go.Bar(x=mom["order_month"], y=mom["mom_growth"], name="MoM Growth"),
        row=1, col=2
    )

    # 3. Revenue by Category (Bar)
    cat_df = kpis["revenue_by_category"].reset_index()
    fig.add_trace(
        px.bar(cat_df, x="revenue", y="category", orientation='h').data[0],
        row=2, col=1
    )

    # 4. Revenue by City (Bar)
    city_df = kpis["revenue_by_city"].reset_index()
    fig.add_trace(
        px.bar(city_df, x="city", y="revenue").data[0],
        row=2, col=2
    )

    # Update layout
    fig.update_layout(
        height=900,
        width=1200,
        title_text="Amman Digital Market - Interactive KPI Dashboard",
        showlegend=False,
        template="plotly_white"
    )

    fig.update_xaxes(tickangle=45)

    # Save as standalone HTML
    fig.write_html("output/dashboard.html", include_plotlyjs=True)
    
    print("✅ Interactive Plotly Dashboard created successfully!")
    print("   → Saved as: output/dashboard.html")
    print("   You can open this file in any browser (has hover, zoom, and filters)\n")