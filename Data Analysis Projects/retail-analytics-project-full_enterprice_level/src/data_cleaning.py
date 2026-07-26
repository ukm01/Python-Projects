import pandas as pd
from pathlib import Path

RAW_DATA_PATH = Path("data/raw")
PROCESSED_DATA_PATH = Path("data/processed")

customers = pd.read_csv(RAW_DATA_PATH / "customers.csv")
products = pd.read_csv(RAW_DATA_PATH / "products.csv")
stores = pd.read_csv(RAW_DATA_PATH / "stores.csv")
orders = pd.read_csv(RAW_DATA_PATH / "orders.csv")
returns = pd.read_csv(RAW_DATA_PATH / "returns.csv")

print("Customers:", customers.shape)
print("Products:", products.shape)
print("Stores:", stores.shape)
print("Orders:", orders.shape)
print("Returns:", returns.shape)

# Check columns

print(orders.columns)

print(orders.isnull().sum())

orders["order_date"] = pd.to_datetime(orders["order_date"])
returns["return_date"] = pd.to_datetime(returns["return_date"])

orders["year"] = orders["order_date"].dt.year
orders["month"] = orders["order_date"].dt.month
orders["month_name"] = orders["order_date"].dt.month_name()

orders.to_csv(PROCESSED_DATA_PATH / "orders_cleaned.csv", index=False)
customers.to_csv(PROCESSED_DATA_PATH / "customers_cleaned.csv", index=False)
products.to_csv(PROCESSED_DATA_PATH / "products_cleaned.csv", index=False)
stores.to_csv(PROCESSED_DATA_PATH / "stores_cleaned.csv", index=False)
returns.to_csv(PROCESSED_DATA_PATH / "returns_cleaned.csv", index=False)
print("\nCleaning completed successfully.")




