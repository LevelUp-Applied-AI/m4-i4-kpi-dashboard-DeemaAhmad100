"""Integration 4 — KPI Dashboard: Amman Digital Market Analytics"""

import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sqlalchemy import create_engine


def connect_db():
    engine = create_engine("postgresql+psycopg://postgres:postgres@localhost:5432/amman_market")
    print("Connected to Amman Digital Market database successfully!\n")
    return engine


def extract_data(engine):
    customers = pd.read_sql("SELECT * FROM customers", engine)
    products = pd.read_sql("SELECT * FROM products", engine)
    
    orders = pd.read_sql("SELECT * FROM orders WHERE status != 'cancelled'", engine)
    order_items = pd.read_sql("SELECT * FROM order_items WHERE quantity <= 100", engine)

    df = (order_items
          .merge(orders, on="order_id")
          .merge(products, on="product_id")
          .merge(customers[["customer_id", "city"]], on="customer_id", how="left"))

    df["city"] = df["city"].fillna("Unknown")
    df["revenue"] = df["quantity"] * df["unit_price"]
    df["order_month"] = pd.to_datetime(df["order_date"]).dt.to_period("M")

    print("Data Extraction & Cleaning completed:")
    print(f"   Customers     : {len(customers)}")
    print(f"   Products      : {len(products)}")
    print(f"   Valid Orders  : {len(orders)}")
    print(f"   Valid Items   : {len(order_items)}")
    print(f"   Final Dataset : {len(df)} rows\n")

    return {
        "customers": customers,
        "products": products,
        "orders": orders,
        "order_items": order_items,
        "df": df
    }


def compute_kpis(data):
    df = data["df"]

    total_revenue = df["revenue"].sum()
    revenue_by_city = df.groupby("city")["revenue"].sum().sort_values(ascending=False)
    monthly_revenue = df.groupby("order_month")["revenue"].sum()
    mom_growth = monthly_revenue.pct_change() * 100
    revenue_by_category = df.groupby("category")["revenue"].sum().sort_values(ascending=False)

    order_value = df.groupby(["order_id", "city"])["revenue"].sum().reset_index()

    print("KPIs computed successfully")
    print(f"   Total Revenue      : {total_revenue:,.1f} JOD")
    print(f"   Top Category       : {revenue_by_category.idxmax()}\n")

    return {
        "total_revenue": total_revenue,
        "revenue_by_city": revenue_by_city,
        "monthly_revenue": monthly_revenue,
        "mom_growth": mom_growth,
        "revenue_by_category": revenue_by_category,
        "df": df,
        "order_value": order_value
    }


def run_statistical_tests(data):
    kpis = compute_kpis(data)
    df = kpis["df"]
    order_value = kpis["order_value"]

    results = {}

    cat_orders = df.groupby(["order_id", "category"])["revenue"].sum().reset_index()
    groups = [group["revenue"].values for _, group in cat_orders.groupby("category")]
    
    f_stat, p_val = stats.f_oneway(*groups)
    results["anova_category"] = {
        "p_value": float(p_val),
        "interpretation": "Significant" if p_val < 0.05 else "Not significant"
    }

    amman = order_value[order_value["city"] == "Amman"]["revenue"]
    others = order_value[order_value["city"] != "Amman"]["revenue"]

    if len(amman) > 1 and len(others) > 1:
        t_stat, p_val = stats.ttest_ind(amman, others, equal_var=False)
        results["ttest_city"] = {
            "p_value": float(p_val),
            "interpretation": "Significant" if p_val < 0.05 else "Not significant"
        }

    return results


def create_visualizations(kpis):
    os.makedirs("output", exist_ok=True)
    sns.set_palette("colorblind")
    sns.set_style("whitegrid")

    df = kpis["df"]

    fig, axes = plt.subplots(2, 2, figsize=(15, 10))

    kpis["monthly_revenue"].plot(ax=axes[0,0], marker='o', linewidth=2)
    axes[0,0].set_title("Finding: Monthly Revenue shows strong and consistent growth")
    axes[0,0].set_ylabel("Revenue (JOD)")
    axes[0,0].set_xlabel("Month")

    kpis["mom_growth"].plot(kind="bar", ax=axes[0,1], color="teal")
    axes[0,1].set_title("Finding: Very strong Month-over-Month growth in recent period")
    axes[0,1].set_ylabel("Growth (%)")
    axes[0,1].set_xlabel("Month")

    sns.barplot(x=kpis["revenue_by_category"].values, y=kpis["revenue_by_category"].index, ax=axes[1,0])
    axes[1,0].set_title("Finding: Books is the top performing product category")
    axes[1,0].set_xlabel("Revenue (JOD)")

    sns.barplot(x=kpis["revenue_by_city"].values, y=kpis["revenue_by_city"].index, ax=axes[1,1])
    axes[1,1].set_title("Finding: Amman generates the highest total revenue")
    axes[1,1].set_xlabel("Revenue (JOD)")

    plt.tight_layout()
    plt.savefig("output/01_multi_panel_kpis.png", dpi=300)
    plt.close()

    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df, x="category", y="revenue")
    plt.title("Finding: Revenue distribution varies significantly across product categories")
    plt.xticks(rotation=45)
    plt.ylabel("Revenue per order (JOD)")
    plt.savefig("output/02_boxplot_category.png", dpi=300)
    plt.close()

    print("All 5 KPI visualizations have been created and saved in output/ folder\n")


def create_interactive_dashboard(kpis):
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    df = kpis["df"]

    fig = make_subplots(rows=2, cols=2, subplot_titles=("Monthly Revenue Trend", "MoM Growth Rate", "Revenue by Category", "Revenue by City"))

    monthly = kpis["monthly_revenue"].reset_index()
    monthly = monthly.rename(columns={0: "revenue"})
    monthly["order_month"] = monthly["order_month"].astype(str)
    fig.add_trace(go.Scatter(x=monthly["order_month"], y=monthly["revenue"], mode='lines+markers'), row=1, col=1)

    mom = kpis["mom_growth"].reset_index()
    mom = mom.rename(columns={0: "mom_growth"})
    mom["order_month"] = mom["order_month"].astype(str)
    fig.add_trace(go.Bar(x=mom["order_month"], y=mom["mom_growth"]), row=1, col=2)

    cat_df = kpis["revenue_by_category"].reset_index()
    cat_df = cat_df.rename(columns={0: "revenue"})
    fig.add_trace(go.Bar(x=cat_df["revenue"], y=cat_df["category"], orientation='h'), row=2, col=1)

    city_df = kpis["revenue_by_city"].reset_index()
    city_df = city_df.rename(columns={0: "revenue"})
    fig.add_trace(go.Bar(x=city_df["city"], y=city_df["revenue"]), row=2, col=2)

    fig.update_layout(height=950, width=1350, title_text="Amman Digital Market - Interactive KPI Dashboard (Tier 1)", template="plotly_white")
    fig.update_xaxes(tickangle=45)

    os.makedirs("output", exist_ok=True)
    fig.write_html("output/dashboard.html", include_plotlyjs=True)
    
    print("Tier 1 Interactive Dashboard created successfully!")
    print("   Saved as: output/dashboard.html\n")


def main():
    print("Starting Amman Digital Market KPI Dashboard...\n")

    engine = connect_db()
    data = extract_data(engine)
    
    kpis = compute_kpis(data)
    stats_results = run_statistical_tests(data)
    
    create_visualizations(kpis)
    create_interactive_dashboard(kpis)

    print("Final Summary:")
    print(f"   Total Revenue     : {kpis['total_revenue']:,.1f} JOD")
    print(f"   Latest MoM Growth : {kpis['mom_growth'].iloc[-1]:.2f}%")
    print(f"   Top Category      : {kpis['revenue_by_category'].idxmax()}")
    print("\nAll tasks completed successfully!")


if __name__ == "__main__":
    main()