import pandas as pd
import numpy as np
import random

np.random.seed(42)
random.seed(42)

products_df = pd.read_csv("data/products.csv")
skus = products_df["sku"].tolist()
num_skus = len(skus)

# Random popularity weighting
raw_popularity = np.random.exponential(scale=1.0, size=num_skus)
sku_weights = raw_popularity / raw_popularity.sum()

channels = ["Website", "Amazon FBM"]
NUM_ORDERS = 10000

# wigs generally have higher sales during holiday season, weaves during tax season and braids during summer
category_seasonal_group = {
    "Wigs": "holiday",
    "Lace Wigs": "holiday",
    "Weaves": "tax_season",
    "Braids": "summer"
}

seasonality_curves = {
    "holiday":    {1: 0.6, 2: 0.65, 3: 0.8, 4: 0.9, 5: 0.95, 6: 1.0, 7: 1.0, 8: 1.0, 9: 1.1, 10: 1.4, 11: 1.8, 12: 1.9},
    "tax_season": {1: 0.7, 2: 1.6,  3: 1.9, 4: 1.5, 5: 0.9,  6: 0.75, 7: 0.75, 8: 0.8, 9: 0.85, 10: 0.9, 11: 1.0, 12: 1.1},
    "summer":     {1: 0.7, 2: 0.75, 3: 0.85, 4: 0.9, 5: 1.1, 6: 1.7, 7: 1.9, 8: 1.8, 9: 1.2, 10: 0.9, 11: 0.8, 12: 0.85}
}

sku_to_category = dict(zip(products_df["sku"], products_df["category"]))

all_dates = pd.date_range(start="2024-01-01", end="2025-12-31", freq="D")

def build_day_weights(dates, curve):
    weights = np.array([curve[d.month] for d in dates], dtype=float)
    return weights / weights.sum()

day_weights_by_group = {
    group: build_day_weights(all_dates, curve)
    for group, curve in seasonality_curves.items()
}


orders = []
for i in range(NUM_ORDERS):
    order_id = f"ORD-{100000 + i}"
    sku = np.random.choice(skus, p=sku_weights)
    category = sku_to_category[sku]
    seasonal_group = category_seasonal_group[category]
    order_date = np.random.choice(all_dates, p=day_weights_by_group[seasonal_group])
    channel = random.choice(channels)
    units_sold = np.random.randint(1, 4)

    orders.append([order_id, order_date, sku, channel, units_sold])

orders_df = pd.DataFrame(orders, columns=["order_id", "order_date", "sku", "channel", "units_sold"])

print(orders_df.shape)
print(orders_df["sku"].value_counts().head(10))
print(orders_df["sku"].value_counts().tail(10))