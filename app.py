"""Tier 3 — Multi-Page Analytical Report with Plotly Dash"""

import dash
from dash import dcc, html, Input, Output, callback
import plotly.express as px
import pandas as pd
from analysis import connect_db, extract_data, compute_kpis

app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Amman Digital Market - Analytics Dashboard"

# Load data once
engine = connect_db()
data = extract_data(engine)
kpis = compute_kpis(data)
df = kpis["df"]

# ====================== LAYOUT ======================
app.layout = html.Div([
    html.H1("Amman Digital Market - Analytics Dashboard", 
            style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '30px'}),

    dcc.Tabs(id="tabs", value='tab-1', children=[
        dcc.Tab(label='📊 KPI Overview', value='tab-1'),
        dcc.Tab(label='📈 Time Series Analysis', value='tab-2'),
        dcc.Tab(label='🗺️ Cohort Comparison', value='tab-3'),
    ]),

    html.Div(id='tabs-content', style={'padding': '20px'})
])

# ====================== CALLBACKS ======================
@callback(
    Output('tabs-content', 'children'),
    Input('tabs', 'value')
)
def render_content(tab):
    if tab == 'tab-1':
        # Page 1: KPI Overview with Gauges
        total_rev = kpis["total_revenue"]
        mom = kpis["mom_growth"].iloc[-1] if not kpis["mom_growth"].empty else 0
        books_rev = kpis["revenue_by_category"].get("Books", 0)

        return html.Div([
            html.H3("KPI Overview"),
            html.Div([
                dcc.Graph(figure=px.bar(x=["Total Revenue"], y=[total_rev], title="Total Revenue")),
                dcc.Graph(figure=px.bar(x=["MoM Growth"], y=[mom], title="Latest MoM Growth (%)")),
                dcc.Graph(figure=px.bar(x=kpis["revenue_by_category"].index, 
                                       y=kpis["revenue_by_category"].values, 
                                       title="Revenue by Category"))
            ], style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '20px'})
        ])

    elif tab == 'tab-2':
        # Page 2: Time Series
        monthly = kpis["monthly_revenue"].reset_index()
        monthly = monthly.rename(columns={0: "revenue"})
        monthly["order_month"] = monthly["order_month"].astype(str)

        fig = px.line(monthly, x="order_month", y="revenue", 
                      title="Monthly Revenue Trend", markers=True)
        
        return html.Div([
            html.H3("Time Series Analysis"),
            dcc.Graph(figure=fig)
        ])

    elif tab == 'tab-3':
        # Page 3: Cohort Comparison
        city_df = kpis["revenue_by_city"].reset_index()
        city_df = city_df.rename(columns={0: "revenue"})

        fig = px.bar(city_df, x="city", y="revenue", title="Revenue by City (Cohort)")

        return html.Div([
            html.H3("Cohort & City Comparison"),
            dcc.Graph(figure=fig),
            html.P("Drill-down: Select a city from the filter above to see more details (basic version)")
        ])


if __name__ == '__main__':
    print("🚀 Starting Multi-Page Dash Application (Tier 3)...")
    print("   Open your browser and go to: http://127.0.0.1:8050/")
    app.run(debug=True)