import re
import pickle
import numpy as np

# ==============================
# STEP 5: Product Risk Analyzer
# DO NOT run directly.
# This file is imported by analyze_product.py
# ==============================

# ── Load Model Files ───────────────────────────────────
try:
    model      = pickle.load(open("harm_model.pkl",    "rb"))
    vectorizer = pickle.load(open("vectorizer.pkl",     "rb"))
    le         = pickle.load(open("label_encoder.pkl",  "rb"))
except FileNotFoundError as e:
    raise FileNotFoundError(
        f"\n❌ Model file not found: {e}"
        "\n   Please run train_model.py first."
    )

HARM_SCORE_MAP = {
    "hazardous": 4, "moderately high": 3,
    "moderate": 2,  "safe": 1,
}

HARM_EMOJI = {
    "hazardous": "🔴", "moderately high": "🟠",
    "moderate":  "🟡", "safe": "🟢",
}


def split_ingredients(ingredient_string):
    """
    Splits raw ingredient string into individual items.
    e.g. "sugar (45%), palm oil, cocoa (15%)"
      -> ["sugar", "palm oil", "cocoa"]
    """
    parts = re.split(r",|;|\(|\)|\bcontains\b", str(ingredient_string).lower())
    cleaned = []
    for p in parts:
        p = re.sub(r"\d+\.?\d*\s*%", "", p)
        p = re.sub(r"\d+", "", p)
        p = re.sub(r"[^a-zA-Z\s]", "", p)
        p = p.strip()
        if len(p) > 2:
            cleaned.append(p)
    return cleaned


def classify_ingredient(ingredient):
    """
    Uses trained ML model to classify one ingredient.
    Returns (harm_level, confidence)
    """
    vec        = vectorizer.transform([ingredient])
    pred       = model.predict(vec)[0]
    proba      = model.predict_proba(vec)[0]
    confidence = round(float(np.max(proba)), 2)
    harm_level = le.inverse_transform([pred])[0]
    return harm_level, confidence


def analyze_ingredients(ingredient_string):
    """
    Analyzes all ingredients in a product string.

    INPUT:
        "sugar (45%), palm oil, cocoa, milk powder, carrageenan"

    OUTPUT:
        dict with per-ingredient results + summary stats
    """
    ingredients = split_ingredients(ingredient_string)

    if not ingredients:
        return {
            "error":             "No ingredients could be parsed.",
            "per_ingredient":    {},
            "avg_harm_score":    0,
            "worst_ingredient":  None,
            "harm_distribution": {},
            "total_ingredients": 0,
        }

    per_ingredient = {}
    harm_scores    = []
    distribution   = {"safe": 0, "moderate": 0, "moderately high": 0, "hazardous": 0}
    worst_score    = 0
    worst_name     = None

    for ing in ingredients:
        harm_level, confidence = classify_ingredient(ing)

        # 🔥 RULE-BASED BOOSTING (NO WEIGHT CHANGE)
        if "artificial" in ing:
            harm_level = "moderately high"

        if "tartrazine" in ing:
            harm_level = "moderately high"

        if "benzoate" in ing:
            harm_level = "hazardous"

        if "msg" in ing or "monosodium" in ing:
            harm_level = "moderately high"

        if "inosinate" in ing:
            harm_level = "moderately high"


        score = HARM_SCORE_MAP.get(harm_level, 2)

        per_ingredient[ing] = {
            "harm_level": harm_level,
            "harm_score": score,
            "confidence": confidence,
            "emoji":      HARM_EMOJI[harm_level],
        }

        harm_scores.append(score)
        distribution[harm_level] += 1

        if score > worst_score:
            worst_score = score
            worst_name  = ing

    return {
        "per_ingredient":    per_ingredient,
        "avg_harm_score":    round(float(np.mean(harm_scores)), 2),
        "worst_ingredient":  worst_name,
        "worst_score":       worst_score,
        "harm_distribution": distribution,
        "total_ingredients": len(ingredients),
    }


# ── Quick test if run directly ─────────────────────────
if __name__ == "__main__":
    test = "sugar (45%), palm oil, cocoa, milk powder, natural flavor, carrageenan"
    print(f"Test input: {test}\n")
    result = analyze_ingredients(test)

    for ing, data in result["per_ingredient"].items():
        print(f"  {data['emoji']}  {ing:<30} → {data['harm_level']} (conf: {data['confidence']})")

    print(f"\nAvg Harm Score : {result['avg_harm_score']} / 4.0")
    print(f"Worst Ingredient: {result['worst_ingredient']}")
    print(f"Distribution   : {result['harm_distribution']}")