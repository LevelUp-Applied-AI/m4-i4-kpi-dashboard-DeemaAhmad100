# KPI Framework - Amman Digital Market

## KPI 1
- **Name:** Total Revenue
- **Definition:** Total revenue generated from all completed orders after excluding cancelled orders and suspicious quantities.
- **Formula:** SUM(quantity * unit_price)
- **Data source:** order_items.quantity, products.unit_price, orders.status
- **Baseline value:** 48701.5 JOD
- **Interpretation:** Shows the overall financial performance of the marketplace.

## KPI 2
- **Name:** Revenue by City
- **Definition:** Total revenue broken down by customer city (cohort segmentation).
- **Formula:** SUM(quantity * unit_price) GROUP BY city
- **Data source:** customers.city, order_items.quantity, products.unit_price
- **Baseline value:** Amman is the highest contributor
- **Interpretation:** Helps identify which cities generate the most sales.

## KPI 3
- **Name:** Monthly Revenue Trend
- **Definition:** Total revenue generated per month (time-based).
- **Formula:** SUM(revenue) GROUP BY order_month
- **Data source:** orders.order_date, order_items.quantity, products.unit_price
- **Baseline value:** Showing consistent upward trend
- **Interpretation:** Tracks business growth over time.

## KPI 4
- **Name:** Month-over-Month Growth Rate
- **Definition:** Percentage change in revenue compared to previous month (time-based).
- **Formula:** ((Current Month Revenue - Previous Month Revenue) / Previous Month Revenue) * 100
- **Data source:** Monthly Revenue
- **Baseline value:** +151.68% in the most recent month
- **Interpretation:** Indicates strong recent growth momentum.

## KPI 5
- **Name:** Revenue by Product Category
- **Definition:** Total revenue contribution from each product category.
- **Formula:** SUM(quantity * unit_price) GROUP BY category
- **Data source:** products.category, order_items.quantity, products.unit_price
- **Baseline value:** Books is the top performing category
- **Interpretation:** Identifies the strongest and weakest product categories.

### Statistical Validation

**Test 1: One-way ANOVA**
- H0: No significant difference in revenue between categories
- H1: There is a significant difference
- Test: One-way ANOVA
- p-value: extremely small
- Interpretation: Revenue differs significantly between product categories.

**Test 2: Independent t-test**
- H0: No difference in average order value between Amman and other cities
- H1: There is a difference
- Test: Welch's t-test
- p-value: 0.195
- Interpretation: Average order value is statistically similar across cities.