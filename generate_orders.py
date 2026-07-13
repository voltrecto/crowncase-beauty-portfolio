import pandas as pd
import numpy as np
import random
import math
import os

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

# generated date range in 2024 - 2025
all_dates = pd.date_range(start="2024-01-01", end="2025-12-31", freq="D")

def build_day_weights(dates, curve):
    weights = np.array([curve[d.month] for d in dates], dtype=float)
    return weights / weights.sum()

day_weights_by_group = {
    group: build_day_weights(all_dates, curve)
    for group, curve in seasonality_curves.items()
}

# setting prices to nearest 0.99
def round_to_99(price):
    return math.floor(price) + 0.99

cost_min = products_df["cost_of_goods"].min()
cost_max = products_df["cost_of_goods"].max()

sku_to_website_price = {}
sku_to_fbm_price = {}

# website price is nearest 0.99 of about 30% gross profit margin. fbm price is higher based on cost
for sku, cost in zip(products_df["sku"], products_df["cost_of_goods"]):
    website_price = round_to_99(cost * 1.43)
    fbm_premium = 1 + (cost - cost_min) / (cost_max - cost_min) * (5 - 1)
    fbm_price = round_to_99(website_price + fbm_premium)
    sku_to_website_price[sku] = website_price
    sku_to_fbm_price[sku] = fbm_price

# lookup dictionaries for fee and shipping from channels.csv
channels_df = pd.read_csv("data/channels.csv")
channel_to_fee_pct = dict(zip(channels_df["channel"], channels_df["avg_fee_pct"]))
channel_to_shipping = dict(zip(channels_df["channel"], channels_df["avg_shipping_cost"]))

orders = []
for i in range(NUM_ORDERS):
    order_id = f"ORD-{100000 + i}"
    sku = np.random.choice(skus, p=sku_weights)
    category = sku_to_category[sku]
    seasonal_group = category_seasonal_group[category]
    order_date = np.random.choice(all_dates, p=day_weights_by_group[seasonal_group])
    channel = random.choice(channels)
    units_sold = np.random.randint(1, 4)
    unit_price = sku_to_website_price[sku] if channel == "Website" else sku_to_fbm_price[sku]
    discount_amount = round(unit_price * 0.10, 2) if np.random.random() < 0.10 else 0.0
    shipping_cost = channel_to_shipping[channel]
    platform_fee = round(unit_price * units_sold * channel_to_fee_pct[channel], 2)
    return_flag = np.random.random() < 0.08

    orders.append([order_id, order_date, sku, channel, units_sold, unit_price, discount_amount, shipping_cost, platform_fee, return_flag])

orders_df = pd.DataFrame(orders, columns=["order_id", "order_date", "sku", "channel", "units_sold", "unit_price", "discount_amount", "shipping_cost", "platform_fee", "return_flag"])

# randomply pick 5% orders and replace their discount amount or shipping cost with nan
null_discount_idx = np.random.choice(orders_df.index, size=int(len(orders_df) * 0.05), replace=False)
orders_df.loc[null_discount_idx, "discount_amount"] = np.nan

null_shipping_idx = np.random.choice(orders_df.index, size=int(len(orders_df) * 0.05), replace=False)
orders_df.loc[null_shipping_idx, "shipping_cost"] = np.nan

# randomly pick 5% orders and replace channel with incorrect casings
channel_variants = {
    "Website": ["website", "WEBSITE", "WebSite"],
    "Amazon FBM": ["amazon fbm", "AMAZON FBM", "Amazon fbm"]
}

messy_channel_idx = np.random.choice(orders_df.index, size=int(len(orders_df) * 0.05), replace=False)
for idx in messy_channel_idx:
    original = orders_df.loc[idx, "channel"]
    orders_df.loc[idx, "channel"] = random.choice(channel_variants[original])

# randomly pick 2% orders and replace their dates with incorrect format
orders_df["order_date"] = orders_df["order_date"].dt.strftime("%Y-%m-%d")

messy_date_idx = np.random.choice(orders_df.index, size=int(len(orders_df) * 0.02), replace=False)
for idx in messy_date_idx:
    date_obj = pd.to_datetime(orders_df.loc[idx, "order_date"])
    orders_df.loc[idx, "order_date"] = date_obj.strftime("%m/%d/%Y")

# randomly pick 15 rows to duplicate
dup_rows = orders_df.sample(n=15)
orders_df = pd.concat([orders_df, dup_rows], ignore_index=True)

print(orders_df.shape)
print(orders_df.isnull().sum())
print(orders_df["channel"].value_counts())
print(orders_df["order_date"].head(20).tolist())

os.makedirs("data", exist_ok=True)
orders_df.to_csv("data/orders.csv", index=False)
print("Saved to data/orders.csv")
