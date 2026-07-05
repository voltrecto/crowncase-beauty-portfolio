import os
import pandas as pd

channels_data = [
    {"channel": "Website", "avg_fee_pct": 0.00, "avg_shipping_cost": 6.50},
    {"channel": "Amazon FBM", "avg_fee_pct": 0.15, "avg_shipping_cost": 6.50}
]

channels_df = pd.DataFrame(channels_data)
print(channels_df)

os.makedirs("data", exist_ok=True)
channels_df.to_csv("data/channels.csv", index=False)
print("Saved to data/channels.csv")