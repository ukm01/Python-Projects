import pandas as pd
from pathlib import Path

PROCESSED_DATA_PATH = Path("data/processed")

orders = pd.read_csv(PROCESSED_DATA_PATH / "orders_cleaned.csv")
customers = pd.read_csv(PROCESSED_DATA_PATH / "customers_cleaned.csv")
products = pd.read_csv(PROCESSED_DATA_PATH / "products_cleaned.csv")
stores = pd.read_csv(PROCESSED_DATA_PATH / "stores_cleaned.csv")
returns = pd.read_csv(PROCESSED_DATA_PATH / "returns_cleaned.csv")

pd.set_option("display.float_format", "{:,.2f}".format)

print("===== BASIC BUSINESS KPIs =====")

total_revenue = orders["net_sales"].sum()
total_profit = orders["profit"].sum()
total_orders = orders["order_id"].nunique()
total_customers = orders["customer_id"].nunique()
total_quantity = orders["quantity"].sum()
profit_margin = (total_profit / total_revenue) * 100

print("Total Revenue:", f"{total_revenue:,.2f}")
print("Total Profit:", f"{total_profit:,.2f}")
print("Total Orders:", f"{total_orders:,}")
print("Total Customers:", f"{total_customers:,}")
print("Total Quantity Sold:", f"{total_quantity:,}")
print("Profit Margin:", f"{profit_margin:.2f}%")

print("\n===== REVENUE BY CHANNEL =====")

revenue_by_channel = (
    orders.groupby("channel", as_index=False)["net_sales"]
    .sum()
    .sort_values(by="net_sales", ascending=False)
)

print(revenue_by_channel)

print("\n===== TOP 10 PRODUCTS BY REVENUE =====")

orders_products = orders.merge(products, on="product_id", how="left")

top_products = (
    orders_products.groupby(["product_id", "product_name"], as_index=False)["net_sales"]
    .sum()
    .sort_values(by="net_sales", ascending=False)
    .head(10)
)

print(top_products)

print("\n===== REVENUE BY CATEGORY =====")

revenue_by_category = (
    orders_products.groupby("category", as_index=False)["net_sales"]
    .sum()
    .sort_values(by="net_sales", ascending=False)
)

print(revenue_by_category)

OUTPUT_PATH = Path("data/processed/analysis_outputs")
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

revenue_by_channel.to_csv(OUTPUT_PATH / "revenue_by_channel.csv", index=False)
top_products.to_csv(OUTPUT_PATH / "top_products_by_revenue.csv", index=False)
revenue_by_category.to_csv(OUTPUT_PATH / "revenue_by_category.csv", index=False)

print("\nAnalysis output files saved successfully.")

print("\n===== MONTHLY REVENUE TREND =====")

orders["order_date"] = pd.to_datetime(orders["order_date"])

monthly_revenue = (
    orders.groupby(["year", "month", "month_name"], as_index=False)
    .agg(
        revenue=("net_sales", "sum"),
        profit=("profit", "sum"),
        orders=("order_id", "nunique"),
        quantity_sold=("quantity", "sum")
    )
    .sort_values(by=["year", "month"])
)

print(monthly_revenue)


print("\n===== CUSTOMER SEGMENT PERFORMANCE =====")

orders_customers = orders.merge(customers, on="customer_id", how="left")

customer_segment_performance = (
    orders_customers.groupby("segment", as_index=False)
    .agg(
        revenue=("net_sales", "sum"),
        profit=("profit", "sum"),
        orders=("order_id", "nunique"),
        customers=("customer_id", "nunique")
    )
    .sort_values(by="revenue", ascending=False)
)

customer_segment_performance["avg_order_value"] = (
    customer_segment_performance["revenue"] / customer_segment_performance["orders"]
)

print(customer_segment_performance)


print("\n===== CITY WISE SALES =====")

orders_stores = orders.merge(stores, on="store_id", how="left")

city_sales = (
    orders_stores.groupby(["state", "city"], as_index=False)
    .agg(
        revenue=("net_sales", "sum"),
        profit=("profit", "sum"),
        orders=("order_id", "nunique")
    )
    .sort_values(by="revenue", ascending=False)
)

print(city_sales.head(10))


print("\n===== RETURN ANALYSIS =====")

total_returned_orders = returns["order_id"].nunique()
return_rate = (total_returned_orders / total_orders) * 100
total_refund_amount = returns["refund_amount"].sum()

print("Total Returned Orders:", f"{total_returned_orders:,}")
print("Return Rate:", f"{return_rate:.2f}%")
print("Total Refund Amount:", f"{total_refund_amount:,.2f}")

monthly_revenue.to_csv(OUTPUT_PATH / "monthly_revenue.csv", index=False)
customer_segment_performance.to_csv(OUTPUT_PATH / "customer_segment_performance.csv", index=False)
city_sales.to_csv(OUTPUT_PATH / "city_sales.csv", index=False)

return_summary = pd.DataFrame({
    "metric": ["Total Returned Orders", "Return Rate %", "Total Refund Amount"],
    "value": [total_returned_orders, round(return_rate, 2), round(total_refund_amount, 2)]
})

return_summary.to_csv(OUTPUT_PATH / "return_summary.csv", index=False)