import os
import pandas as pd
import numpy as np
from faker import Faker
import random

np.random.seed(42)
random.seed(42)
fake = Faker()
Faker.seed(42)

# Basic colors, guaranteed baseline, no cost premium
basic_colors = ['1', '1B', '2', '613']

# Fashion colors, cost more to produce
fashion_colors = [
    'Flamboyage Auburn', 'Flamboyage Blonde', 'Flamboyage Chocolate', 'Flamboyage Mocha',
    'Flamboyage Sand', 'T1B/27', 'T1B/30', 'T1B/BG',
    'HL280/44', 'Balayage Copper', 'Balayage Gold', 'Balayage Hazel', 'Pink'
]

# Color codes for SKUs
color_code_map = {
    "1": "1", "1B": "1B", "2": "2", "613": "613",
    "Flamboyage Auburn": "FLAUB",
    "Flamboyage Blonde": "FLBLD",
    "Flamboyage Chocolate": "FLCHO",
    "Flamboyage Mocha": "FLMOC",
    "Flamboyage Sand": "FLSAN",
    "T1B/27": "T1B27",
    "T1B/30": "T1B30",
    "T1B/BG": "T1BBG",
    "HL280/44": "HL280",
    "Balayage Copper": "BACOP",
    "Balayage Gold": "BAGLD",
    "Balayage Hazel": "BAHAZ",
    "Pink": "PINK"
}

# (num_styles, min_cost, max_cost)
categories = {
    "Wigs":        (7, 15, 40),
    "Lace Wigs":   (8, 35, 90),
    "Weaves":      (7, 20, 55),
    "Braids":      (6, 10, 30)
}

category_codes = {
    "Wigs": "WIG",
    "Lace Wigs": "LACE",
    "Weaves": "WEAV",
    "Braids": "BRAI"
}

# Variant count distribution
# Right-skewed: most styles offer 3-6 colors, a few "hero" styles go up to 12
variant_counts = list(range(2, 13))
variant_weights = [5, 10, 15, 15, 15, 10, 8, 7, 6, 5, 4]
variant_weights = np.array(variant_weights) / sum(variant_weights)

def build_color_list(num_colors):
    """
    Guarantees every style includes '1' and '1B'.
    Once a style has room for 4+ colors, it also guarantees '2' and '613'
    before drawing any fashion colors.
    """
    colors = []
    guaranteed_order = ['1', '1B', '2', '613']
    for c in guaranteed_order:
        if len(colors) < num_colors:
            colors.append(c)

    remaining_slots = num_colors - len(colors)
    if remaining_slots > 0:
        fashion_pick = random.sample(fashion_colors, k=min(remaining_slots, len(fashion_colors)))
        colors.extend(fashion_pick)

    return colors

products = []

style_textures = ["Body Wave", "Straight", "Deep Wave", "Curly", "Water Wave",
                   "Kinky Straight", "Loose Wave", "Yaki Straight"]
style_formats = {
    "Wigs": ["Full Wig", "Bob Wig", "Pixie Wig"],
    "Lace Wigs": ["Lace Front Wig", "360 Lace Wig", "Deep Lace Part", "Lace Closure Wig"],
    "Weaves": ["Bundle with Closure", "Clip-In Weave", "Drawstring Cap"],
    "Braids": ["Loop Braid", "Crochet Braid", "Pre-Stretched Braids"]
}

for category, (num_styles, min_cost, max_cost) in categories.items():
    used_names = set()
    cat_code = category_codes[category]

    for style_num in range(1, num_styles + 1):
        while True:
            texture = random.choice(style_textures)
            fmt = random.choice(style_formats[category])
            style_name = f"{texture} {fmt}"
            if style_name not in used_names:
                used_names.add(style_name)
                break

        base_cost = round(np.random.uniform(min_cost, max_cost), 2)

        # Fashion color cost is about $3 higher than base cost, decided ONCE per style
        fashion_cost = round(base_cost + np.random.uniform(2.5, 3.5), 2)

        num_colors = np.random.choice(variant_counts, p=variant_weights)
        colors_for_style = build_color_list(num_colors)

        style_code = f"{cat_code}-{style_num:02d}"  # e.g. WIG-03

        for color in colors_for_style:
            color_code = color_code_map[color]
            sku = f"{style_code}-{color_code}"  # e.g. WIG-03-613

            cost = base_cost if color in basic_colors else fashion_cost
            products.append([sku, style_name, category, color, cost])

products_df = pd.DataFrame(
    products,
    columns=["sku", "product_name", "category", "color", "cost_of_goods"]
)

print(f"Total SKUs: {products_df.shape[0]}")
print(f"Base styles: {products_df['product_name'].nunique()}")
print(products_df.groupby('category').size())
print(products_df.groupby('product_name')['sku'].apply(list))
print(products_df.head(15))

os.makedirs("data", exist_ok=True)
products_df.to_csv("data/products.csv", index=False)
print("Saved to data/products.csv")