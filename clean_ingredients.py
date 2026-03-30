import pandas as pd
import re

print("=" * 55)
print("  STEP 2: Cleaning Ingredients")
print("=" * 55)

df = pd.read_csv("top_5000ingredients.csv")
print(f"Loaded {len(df)} ingredients.")

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r"\d+\.?\d*\s*%", "", text)  # remove percentages
    text = re.sub(r"\d+", "", text)             # remove numbers
    text = re.sub(r"[^a-zA-Z\s]", "", text)    # remove symbols
    text = re.sub(r"\s+", " ", text)            # collapse spaces
    return text.strip()

df["ingredient"] = df["ingredient"].apply(clean_text)

# Filter garbage entries
df = df[df["ingredient"].str.len() > 2]
df = df[df["ingredient"].str.len() < 60]
df = df[df["ingredient"].str.strip() != ""]
df = df.drop_duplicates(subset=["ingredient"]).reset_index(drop=True)

print(f"After cleaning: {len(df)} ingredients remaining.")
print("\nSample:")
print(df["ingredient"].head(10).tolist())

df.to_csv("cleaned_ingredients.csv", index=False)
print("\n✅ Saved cleaned_ingredients.csv")