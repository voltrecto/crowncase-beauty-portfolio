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

orders = []
for i in range(NUM_ORDERS):
    order_id = f"ORD-{100000 + i}"
    sku = np.random.choice(skus, p=sku_weights)
    channel = random.choice(channels)
    units_sold = np.random.randint(1, 4)

    orders.append([order_id, sku, channel, units_sold])

orders_df = pd.DataFrame(orders, columns=["order_id", "sku", "channel", "units_sold"])

print(orders_df.shape)
print(orders_df["sku"].value_counts().head(10))
print(orders_df["sku"].value_counts().tail(10))