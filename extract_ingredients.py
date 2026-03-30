import pandas as pd
import re
from collections import Counter

# ==============================
# CONFIGURATION
# ==============================
FILE_PATH  = "en.openfoodfacts.org.products.csv"
CHUNK_SIZE = 50000
TOP_N      = 5000

# ==============================
# COLUMNS — India relevant only
# Removed: environmental_score_grade, environmental_score_score,
#          nutriscore_grade, nutriscore_score, nova_group
# ==============================
COLUMNS_TO_USE = [
    "product_name",
    "generic_name",
    "brands",
    "categories",
    "labels_tags",
    "labels_en",
    "ingredients_text",
    "additives_n",
    "additives_en",
    "countries_tags",
    "pnns_groups_1",
    "main_category_en",
    "ingredients_analysis_tags",
]

ingredient_counter = Counter()
product_rows       = []
chunk_num          = 0

print("=" * 55)
print("  STEP 1: Extracting Data (India Market Focus)")
print("=" * 55)

for chunk in pd.read_csv(
    FILE_PATH,
    sep          = "\t",
    usecols      = COLUMNS_TO_USE,
    chunksize    = CHUNK_SIZE,
    low_memory   = False,
    on_bad_lines = "skip",
):
    chunk_num += 1
    chunk = chunk.dropna(subset=["ingredients_text"])
    chunk = chunk[chunk["ingredients_text"].str.strip() != ""]
    product_rows.append(chunk)

    for text in chunk["ingredients_text"]:
        parts = re.split(r",|;|\(|\)", str(text).lower())
        for p in parts:
            item = p.strip()
            if len(item) > 2:
                ingredient_counter[item] += 1

    print(f"  Processed chunk {chunk_num} ({chunk_num * CHUNK_SIZE:,} rows)...")

print("\nFinished reading file.")

# ── Save top ingredients ───────────────────────────────
top_ingredients = ingredient_counter.most_common(TOP_N)
df_ingredients  = pd.DataFrame(top_ingredients, columns=["ingredient", "frequency"])
df_ingredients.to_csv("top_5000ingredients.csv", index=False)
print(f"\n✅ Saved top_5000ingredients.csv")

# ── Save product data ──────────────────────────────────
df_products = pd.concat(product_rows, ignore_index=True)

def clean_label_col(text):
    if pd.isna(text): return ""
    text = str(text).lower()
    text = re.sub(r"en:", "", text)
    text = re.sub(r"[-_]", " ", text)
    text = re.sub(r"[^a-z\s,]", "", text)
    return text.strip()

df_products["labels_tags"]      = df_products["labels_tags"].apply(clean_label_col)
df_products["labels_en"]        = df_products["labels_en"].apply(clean_label_col)
df_products["categories"]       = df_products["categories"].apply(clean_label_col)
df_products["main_category_en"] = df_products["main_category_en"].apply(clean_label_col)
df_products["additives_en"]     = df_products["additives_en"].apply(clean_label_col)

df_products.rename(columns={
    "countries_tags": "country",
    "pnns_groups_1":  "food_group",
}, inplace=True)

df_products.to_csv("products_raw.csv", index=False)
print(f"✅ Saved products_raw.csv ({len(df_products):,} products)")
print("\nColumns saved:")
for col in df_products.columns:
    print(f"  • {col}")