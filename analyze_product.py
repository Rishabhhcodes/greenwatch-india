from product_risk import analyze_ingredients
from greenwash_detector import detect_claims

# ==============================
# MAIN GREENWASHING ANALYZER
# India Market Focused
# ==============================

def normalize_text(text):
    text = str(text).lower()
    text = text.replace("no preservatives", "no preservative")
    text = text.replace("natural ingredients", "natural")
    text = text.replace("taste bhi health bhi", "healthy")
    return text

def get_verdict(score):
    if score <= 25:   return "✅ Clean / Honest Product",         "green"
    elif score <= 50: return "🟡 Mildly Suspicious",              "yellow"
    elif score <= 75: return "⚠️  Likely Greenwashing",           "orange"
    else:             return "🚨 Strong Greenwashing Detected",    "red"


def analyze_product(
    product_name,
    generic_name,
    ingredients_text,
    labels_text,
    tagline_text,
    additives_n = 0,
):
    # ── Step 1: Detect claims ──────────────────────────
    labels_text  = normalize_text(labels_text)
    tagline_text = normalize_text(tagline_text)

    claims_result = detect_claims(labels_text, tagline_text)
    # ── Step 2: Analyze ingredients ───────────────────
    risk_result = analyze_ingredients(ingredients_text)

    # ── Step 3: Convert scores ─────────────────────────
    claim_score    = claims_result["claim_score"]
    harm_score_100 = round(((risk_result["avg_harm_score"] - 1) / 3) * 100, 1)

    # Mismatch = average of claim + harm
    # Old multiplicative formula capped out too low (~68 max)
    # New additive formula correctly reaches 75+ for greenwashing products
    mismatch_score = round(
        (claim_score + harm_score_100) / 2, 1
    ) if claim_score else 0

    # Additives penalty — 5 pts each, max 40
    ingredients_list = ingredients_text.lower().split(",")

    auto_additives = sum(
        1 for ing in ingredients_list
        if any(x in ing for x in [
            "msg",
            "monosodium",
            "benzoate",
            "tartrazine",
            "flavor",
            "inosinate"
        ])
    )

    # Take whichever is higher (user input OR detected)
    additives_n = max(additives_n, auto_additives)
    additives_penalty = min(int(additives_n or 0) * 5, 40)

    # Hazardous bonus — 5 pts per hazardous ingredient, max 20
    hazardous_count = sum(
        1 for d in risk_result["per_ingredient"].values()
        if d["harm_score"] == 4
    )
    hazardous_bonus = min(hazardous_count * 5, 20)

    # ── Step 4: Final greenwash score ──────────────────
    # Weights:
    #   40% ingredient harm
    #   25% claim vs reality mismatch
    #   15% green claims made
    #   10% additives penalty
    #   10% hazardous ingredient bonus
    greenwash_score = round(min(
        harm_score_100    * 0.40 +
        mismatch_score    * 0.25 +
        claim_score       * 0.15 +
        additives_penalty * 0.10 +
        hazardous_bonus   * 0.10,
        100
    ), 1)

    verdict, color = get_verdict(greenwash_score)

    harmful_ingredients = [
        ing for ing, d in risk_result["per_ingredient"].items()
        if d["harm_score"] >= 3
    ]

    return {
        # Product info
        "product_name":    product_name,
        "generic_name":    generic_name,
        "additives_n":     additives_n,

        # Claims
        "label_claims":    claims_result["label_claims"],
        "tagline_claims":  claims_result["tagline_claims"],
        "all_claims":      claims_result["all_claims"],
        "claim_score":     claim_score,

        # Ingredients
        "per_ingredient":      risk_result["per_ingredient"],
        "avg_harm_score":      risk_result["avg_harm_score"],
        "harm_distribution":   risk_result["harm_distribution"],
        "worst_ingredient":    risk_result["worst_ingredient"],
        "harmful_ingredients": harmful_ingredients,
        "total_ingredients":   risk_result["total_ingredients"],

        # Scores
        "harm_score_100":    harm_score_100,
        "mismatch_score":    mismatch_score,
        "additives_penalty": additives_penalty,
        "hazardous_bonus":   hazardous_bonus,
        "greenwash_score":   greenwash_score,

        # Verdict
        "verdict":       verdict,
        "verdict_color": color,
    }


def print_report(result):
    print("\n" + "=" * 56)
    print("        GREENWASHING ANALYSIS REPORT")
    print("=" * 56)
    print(f"  Product    : {result['product_name']}")
    print(f"  Category   : {result['generic_name']}")
    print(f"  Additives  : {result['additives_n']}")
    print("-" * 56)

    print("\n  GREEN CLAIMS DETECTED:")
    if result["all_claims"]:
        for c in result["label_claims"]:
            print(f"    🏷  [LABEL]   {c}")
        for c in result["tagline_claims"]:
            print(f"    💬 [TAGLINE] {c}")
    else:
        print("    None detected.")

    print("\n  INGREDIENT ANALYSIS:")
    for ing, data in result["per_ingredient"].items():
        print(f"    {data['emoji']}  {ing:<30} → {data['harm_level']}")

    print("\n  SCORES:")
    print(f"    Claims Score      : {result['claim_score']:>6.1f} / 100")
    print(f"    Harm Score        : {result['harm_score_100']:>6.1f} / 100")
    print(f"    Mismatch Score    : {result['mismatch_score']:>6.1f} / 100")
    print(f"    Additives Penalty : {result['additives_penalty']:>6.1f} / 40")
    print(f"    Hazardous Bonus   : {result['hazardous_bonus']:>6.1f} / 20")
    print()
    print(f"    ► GREENWASH SCORE  : {result['greenwash_score']:>5.1f} / 100")
    print(f"\n  VERDICT : {result['verdict']}")
    print("=" * 56)


if __name__ == "__main__":

    print("\n--- TEST 1: Instant Noodles ---")
    r1 = analyze_product(
        product_name     = "Masala Magic Instant Noodles",
        generic_name     = "Instant Noodles",
        ingredients_text = "maida, palm oil, salt, sugar, monosodium glutamate, tartrazine, sodium benzoate, artificial flavor, disodium inosinate, carrageenan, maltodextrin",
        labels_text      = "no preservatives, natural masala, vegetarian, organic, no artificial color",
        tagline_text     = "taste bhi health bhi, natural ingredients, ghar jaisa swad, shudh aur healthy",
        additives_n      = 8,
    )
    print_report(r1)

    print("\n--- TEST 2: Traditional Ghee ---")
    r2 = analyze_product(
        product_name     = "Amul Pure Ghee",
        generic_name     = "Ghee",
        ingredients_text = "cow milk ghee",
        labels_text      = "",
        tagline_text     = "",
        additives_n      = 0,
    )
    print_report(r2)