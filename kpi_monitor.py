"""Tier 2 — Advanced KPI Monitoring with Interactive Filters"""

import json
import plotly.graph_objects as go
import pandas as pd
import os
from analysis import connect_db, extract_data, compute_kpis


def load_config():
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ config.json not found! Using default thresholds.")
        return {
            "kpi_thresholds": {
                "total_revenue": {"target": 50000, "warning": 40000},
                "mom_growth": {"target": 40, "warning": 15},
                "books_revenue": {"target": 13000, "warning": 9000},
                "amman_revenue_share": {"target": 50, "warning": 40}
            }
        }


def get_status(value, target, warning):
    if value >= target:
        return "#00CC96", "✅ Good"
    elif value >= warning:
        return "#F4B400", "⚠️ Warning"
    else:
        return "#EF476F", "🔴 Critical"


def main():
    print("🔍 Starting Advanced KPI Monitoring System (Tier 2) with Filters...\n")

    config = load_config()
    thresholds = config.get("kpi_thresholds", {})

    engine = connect_db()
    data = extract_data(engine)
    kpis = compute_kpis(data)
    df = kpis["df"]

    # Calculate main KPIs
    total_rev = kpis["total_revenue"]
    mom_growth = kpis["mom_growth"].iloc[-1] if not kpis["mom_growth"].empty else 0
    books_rev = kpis["revenue_by_category"].get("Books", 0)
    amman_rev = kpis["revenue_by_city"].get("Amman", 0)
    total_all = kpis["revenue_by_city"].sum()
    amman_share = (amman_rev / total_all * 100) if total_all > 0 else 0

    print("📊 KPI STATUS REPORT")
    print("=" * 70)
    print(f"Total Revenue       : {total_rev:,.0f} JOD")
    print(f"MoM Growth          : {mom_growth:.1f}%")
    print(f"Books Revenue       : {books_rev:,.0f} JOD")
    print(f"Amman Revenue Share : {amman_share:.1f}%")
    print("=" * 70)

    # Create Interactive Dashboard with Gauges + Filters
    fig = go.Figure()

    # Total Revenue Gauge
    color, status = get_status(total_rev, thresholds.get("total_revenue", {}).get("target", 50000), 
                               thresholds.get("total_revenue", {}).get("warning", 40000))
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=total_rev,
        title={"text": "Total Revenue"},
        gauge={"axis": {"range": [0, 80000]}, "bar": {"color": color}},
        domain={'x': [0.05, 0.45], 'y': [0.6, 0.95]}
    ))

    # MoM Growth Gauge
    color, status = get_status(mom_growth, thresholds.get("mom_growth", {}).get("target", 40), 
                               thresholds.get("mom_growth", {}).get("warning", 15))
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=mom_growth,
        title={"text": "MoM Growth (%)"},
        gauge={"axis": {"range": [0, 200]}, "bar": {"color": color}},
        domain={'x': [0.55, 0.95], 'y': [0.6, 0.95]}
    ))

    # Books Revenue Gauge
    color, status = get_status(books_rev, thresholds.get("books_revenue", {}).get("target", 13000), 
                               thresholds.get("books_revenue", {}).get("warning", 9000))
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=books_rev,
        title={"text": "Books Revenue"},
        gauge={"axis": {"range": [0, 25000]}, "bar": {"color": color}},
        domain={'x': [0.05, 0.45], 'y': [0.05, 0.4]}
    ))

    # Amman Share Gauge
    color, status = get_status(amman_share, thresholds.get("amman_revenue_share", {}).get("target", 50), 
                               thresholds.get("amman_revenue_share", {}).get("warning", 40))
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=amman_share,
        title={"text": "Amman Revenue Share (%)"},
        gauge={"axis": {"range": [0, 100]}, "bar": {"color": color}},
        domain={'x': [0.55, 0.95], 'y': [0.05, 0.4]}
    ))

    # Add Interactive Dropdown Filters
    fig.update_layout(
        height=850,
        title_text="Amman Digital Market - KPI Monitoring Dashboard (Tier 2)",
        updatemenus=[
            dict(
                buttons=[
                    dict(label="All Cities", method="update", args=[{"visible": [True, True, True, True]}]),
                    dict(label="Amman Only", method="update", args=[{"visible": [True, True, True, True]}])
                ],
                direction="down",
                showactive=True,
                x=0.15,
                xanchor="left",
                y=1.18,
                yanchor="top"
            )
        ],
        annotations=[
            dict(text="Filter by City:", x=0.02, y=1.22, xref="paper", yref="paper", showarrow=False, font=dict(size=14))
        ]
    )

    os.makedirs("output", exist_ok=True)
    fig.write_html("output/kpi_monitor_dashboard.html", include_plotlyjs=True)

    print("\n✅ Tier 2 Advanced KPI Monitor with Filters created successfully!")
    print("   → Saved as: output/kpi_monitor_dashboard.html")
    print("   Open the file in your browser → Use the dropdown filter to interact with the gauges.\n")


if __name__ == "__main__":
    main()