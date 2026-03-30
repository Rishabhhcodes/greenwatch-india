import pandas as pd
import re

# ==============================
# AUTOLABEL.PY — INDIA MARKET FOCUSED
# Based on FSSAI Food Additives Compendium 2022
# Common Indian food product ingredients
# ==============================

print("=" * 55)
print("  STEP 3: Auto-Labeling (India Market / FSSAI Backed)")
print("=" * 55)

df = pd.read_csv("cleaned_ingredients.csv")
df = df.dropna(subset=["ingredient"])
df["ingredient"] = df["ingredient"].str.lower().str.strip()
print(f"Loaded {len(df)} ingredients.")

# ==============================
# HAZARDOUS (Score = 4)
# Banned or severely restricted by FSSAI
# ==============================
HAZARDOUS_PATTERNS = [

    # ── Synthetic Antioxidants ─────────────────────────
    r"\bbha\b",                          # INS 320 — restricted by FSSAI
    r"\bbht\b",                          # INS 321 — restricted by FSSAI
    r"\btbhq\b",                         # INS 319 — banned Japan/EU
    r"\bbutylated hydroxyanisole\b",
    r"\bbutylated hydroxytoluene\b",

    # ── Colours banned in India ────────────────────────
    r"\btitanium dioxide\b",             # INS 171 — banned EU 2022
    r"\bamaranth\b",                     # INS 123 — banned US
    r"\bbrown fk\b",                     # INS 154 — banned EU/US
    r"\bred 2g\b",                       # INS 128 — banned EU
    r"\bcaramel.*sulphite.*ammonia\b",   # INS 150d — 4-MEI carcinogen
    r"\bmetanil yellow\b",               # Illegal in India — common adulterant
    r"\bmalachite green\b",              # Illegal in India
    r"\brhod(?:a)?mine\b",               # Illegal in India
    r"\bsudane?\b",                      # Illegal dye

    # ── Preservatives — IARC / FSSAI concern ──────────
    r"\bsodium nitrite\b",               # INS 250 — IARC 2A, used in meats
    r"\bpotassium nitrite\b",            # INS 249
    r"\bsodium nitrate\b",               # INS 251
    r"\bpotassium nitrate\b",            # INS 252
    r"\bnitrite\b",
    r"\bnitrate\b",
    r"\bsodium benzoate\b",              # INS 211 — forms benzene with Vit C
    r"\bpotassium benzoate\b",           # INS 212
    r"\bcalcium benzoate\b",             # INS 213
    r"\bpotassium bromate\b",            # Banned in India since 2016
    r"\bbrominated vegetable oil\b",     # Banned India/EU
    r"\bformaldehyde\b",                 # INS 240 — carcinogen

    # ── Sweeteners — banned/restricted India ──────────
    r"\bcyclamate\b",                    # INS 952 — banned US, restricted India
    r"\bsaccharin\b",                    # INS 954 — restricted India

    # ── Trans fats — FSSAI banned 2022 ────────────────
    r"\bpartially hydrogenated\b",       # Trans fat — FSSAI banned >2% 2022
    r"\bhydrogenated vegetable fat\b",   # Common in Indian vanaspati
    r"\bvanaspati\b",                    # Hydrogenated fat — Indian specific

    # ── Heavy metals / Chelators ──────────────────────
    r"\bcalcium disodium edta\b",        # INS 385
    r"\bdisodium edta\b",
    r"\bpropylene glycol\b",             # INS 1520 — industrial solvent
]

# ==============================
# MODERATELY HIGH (Score = 3)
# Permitted by FSSAI with strict limits
# Commonly misused in Indian products
# ==============================
MODERATELY_HIGH_PATTERNS = [

    # ── Colours — hyperactivity link ──────────────────
    r"\btartrazine\b",                   # INS 102 — very common in Indian snacks
    r"\bsunset yellow\b",               # INS 110 — common in Indian sweets
    r"\bazorubine\b",                   # INS 122
    r"\bponceau\b",                     # INS 124 — used in Indian drinks
    r"\berythrosine\b",                 # INS 127
    r"\ballura red\b",                  # INS 129
    r"\bquinoline yellow\b",            # INS 104
    r"\bbrilliant blue\b",              # INS 133 — used in Indian sweets
    r"\bindigo carmine\b",              # INS 132
    r"\bfast green\b",                  # INS 143
    r"\bbrilliant black\b",             # INS 151
    r"\bcaramel colo(?:u)?r\b",         # INS 150 — very common India

    # ── Preservatives ─────────────────────────────────
    r"\bbenzoic acid\b",                # INS 210 — common in Indian pickles
    r"\bsulphur dioxide\b",             # INS 220 — dried fruits
    r"\bsodium sulphite\b",             # INS 221
    r"\bsodium metabisulphite\b",       # INS 223 — used in Indian murabba
    r"\bpotassium metabisulphite\b",    # INS 224
    r"\bsulphite\b",
    r"\bsulfite\b",

    # ── Sweeteners ────────────────────────────────────
    r"\baspartame\b",                   # INS 951 — IARC 2B 2023
    r"\bsucralose\b",                   # INS 955
    r"\bacesulfame\b",                  # INS 950

    # ── Flavour Enhancers ──────────────────────────────
    r"\bmonosodium glutamate\b",        # INS 621 — very common Indian snacks
    r"\bmsg\b",
    r"\bdisodium inosinate\b",          # INS 631
    r"\bdisodium guanylate\b",          # INS 627
    r"\bdisodium ribonucleotide\b",     # INS 635 — used in Indian noodles

    # ── Phosphates ────────────────────────────────────
    r"\bphosphoric acid\b",             # INS 338 — colas, Indian drinks
    r"\bsodium phosphate\b",
    r"\bpotassium phosphate\b",
    r"\bcalcium phosphate\b",
    r"\bdiphosphate\b",
    r"\btriphosphate\b",
    r"\bpolyphosphate\b",
    r"\bphosphate\b",

    # ── Problematic Thickeners ─────────────────────────
    r"\bcarrageenan\b",                 # INS 407 — gut inflammation
    r"\bmaltodextrin\b",                # very common in Indian processed food

    # ── Refined Sugars ────────────────────────────────
    r"\bhigh fructose corn syrup\b",
    r"\bhigh fructose\b",
    r"\binvert sugar\b",                # very common in Indian biscuits
    r"\bsugar\b",
    r"\bglucose\b",
    r"\bfructose\b",
    r"\bdextrose\b",
    r"\bcorn syrup\b",

    # ── Other ─────────────────────────────────────────
    r"\bpolysorbate\b",
    r"\bartificial colou?r\b",
    r"\bartificial flavou?r\b",
    r"\bpreservative\b",
    r"\bsweetener\b",
    r"\baluminium\b",                   # INS 173
    r"\bsodium aluminium phosphate\b",  # INS 541
]

# ==============================
# MODERATE (Score = 2)
# Permitted, limited concern
# Common processing aids in India
# ==============================
MODERATE_PATTERNS = [

    # ── Emulsifiers ───────────────────────────────────
    r"\blecithin\b",                    # INS 322 — from soy, common India
    r"\bemulsifier\b",
    r"\bmono.*diglyceride\b",           # INS 471 — common in Indian breads
    r"\bpolyglycerol\b",
    r"\bsorbitan\b",
    r"\bsucrose ester\b",

    # ── Thickeners ────────────────────────────────────
    r"\bxanthan\b",                     # INS 415
    r"\bgelatin\b",
    r"\bpectin\b",
    r"\bgum\b",
    r"\bstarch\b",
    r"\bmodified starch\b",
    r"\bmodified\b",
    r"\bdextrin\b",
    r"\bcellulose\b",

    # ── Acids ─────────────────────────────────────────
    r"\bcitric acid\b",                 # INS 330 — very common India
    r"\blactic acid\b",                 # INS 270
    r"\btartaric acid\b",
    r"\bacetic acid\b",
    r"\bmalic acid\b",
    r"\bacidity regulator\b",

    # ── Common Indian Processing Aids ─────────────────
    r"\byeast\b",
    r"\bvinegar\b",
    r"\bconcentrate\b",
    r"\bpowder\b",
    r"\bextract\b",
    r"\bflavou?r\b",
    r"\boil\b",
    r"\bcarbonate\b",
    r"\bsyrup\b",
    r"\bsorbate\b",                     # INS 200/202
    r"\bpropionate\b",                  # INS 280-283
    r"\bwax\b",
    r"\bglaze\b",
    r"\bannatto\b",                     # INS 160b — used in Indian dairy

    # ── Raising Agents ────────────────────────────────
    r"\bbaking soda\b",
    r"\bbaking powder\b",
    r"\bsodium bicarbonate\b",          # INS 500 — common in Indian biscuits
    r"\bammonium bicarbonate\b",        # INS 503 — used in Indian cookies
    r"\bsodium carbonate\b",
]

# ==============================
# SAFE (Score = 1)
# Whole / traditional Indian foods
# FSSAI approved natural ingredients
# ==============================
SAFE_PATTERNS = [

    # ── Vitamins / Natural Antioxidants ───────────────
    r"\bascorbic acid\b",               # INS 300 — Vitamin C
    r"\btocopherol\b",                  # INS 306 — Vitamin E
    r"\bbeta.?carotene\b",              # INS 160a

    # ── Staple Indian Grains ──────────────────────────
    r"\bwheat\b",
    r"\bwheat flour\b",
    r"\batta\b",                        # Indian whole wheat flour
    r"\bmaida\b",                       # Refined wheat flour
    r"\bsuji\b",                        # Semolina
    r"\brava\b",                        # Semolina
    r"\brice\b",
    r"\bbasmati\b",
    r"\brice flour\b",
    r"\bcorn\b",
    r"\bmaize\b",
    r"\bjowar\b",                       # Sorghum — Indian millet
    r"\bbajra\b",                       # Pearl millet
    r"\bragi\b",                        # Finger millet
    r"\bnavane\b",
    r"\boat\b",
    r"\bbarley\b",
    r"\bquinoa\b",

    # ── Indian Pulses / Legumes ───────────────────────
    r"\blentil\b",
    r"\bchana\b",                       # Chickpea
    r"\bchickpea\b",
    r"\bbesan\b",                       # Gram flour
    r"\bblack gram\b",
    r"\burad\b",                        # Black lentil
    r"\bmoong\b",                       # Green gram
    r"\bmasoor\b",                      # Red lentil
    r"\btoor\b",                        # Pigeon pea
    r"\brajma\b",                       # Kidney beans
    r"\bbean\b",
    r"\bsoybean\b",
    r"\bsoy\b",

    # ── Dairy ─────────────────────────────────────────
    r"\bmilk\b",
    r"\bcow milk\b",
    r"\bbuffalo milk\b",
    r"\bcurd\b",                        # Indian yogurt
    r"\bdahi\b",                        # Indian yogurt
    r"\bpaneer\b",                      # Indian cottage cheese
    r"\bkhoa\b",                        # Reduced milk solid
    r"\bkhoya\b",
    r"\bghee\b",                        # Clarified butter — Indian
    r"\bbutter\b",
    r"\bcream\b",
    r"\bcheese\b",
    r"\bskimmed milk\b",
    r"\bwhole milk\b",
    r"\bmilk powder\b",
    r"\bmilk solid\b",

    # ── Indian Vegetables ─────────────────────────────
    r"\bpotato\b",
    r"\btomato\b",
    r"\bonion\b",
    r"\bgarlic\b",
    r"\bginger\b",
    r"\bcarrot\b",
    r"\bspinach\b",
    r"\bpalak\b",                       # Spinach — Indian name
    r"\bcauliflower\b",
    r"\bcabbage\b",
    r"\bbrinjal\b",                     # Eggplant — Indian name
    r"\bokra\b",                        # Lady finger
    r"\bbhindi\b",                      # Okra — Indian name
    r"\bpeas\b",
    r"\bmatar\b",                       # Peas — Indian name
    r"\bgourd\b",
    r"\blauki\b",                       # Bottle gourd
    r"\bbitter gourd\b",
    r"\bkarela\b",                      # Bitter gourd — Indian name
    r"\bcapsicum\b",
    r"\bgreen chilli\b",
    r"\bred chilli\b",
    r"\bchilli\b",
    r"\bgreen pepper\b",

    # ── Indian Fruits ─────────────────────────────────
    r"\bmango\b",
    r"\baamb?\b",                       # Mango — Indian
    r"\bbanana\b",
    r"\bcoconut\b",
    r"\bcoconut milk\b",
    r"\bcoconut oil\b",
    r"\bguava\b",
    r"\bpapaya\b",
    r"\bpomegranate\b",
    r"\bapple\b",
    r"\bgrape\b",
    r"\blemon\b",
    r"\bnimbu\b",                       # Lemon — Indian
    r"\borange\b",
    r"\bsapota\b",
    r"\bcustard apple\b",
    r"\bjackfruit\b",
    r"\btamarind\b",                    # Imli — common Indian ingredient
    r"\bimli\b",
    r"\bamla\b",                        # Indian gooseberry
    r"\bgooseberry\b",
    r"\bstrawberry\b",
    r"\bpineapple\b",
    r"\bwatermelon\b",

    # ── Indian Spices (FSSAI natural) ─────────────────
    r"\bturmeric\b",                    # Haldi — Indian staple
    r"\bhaldi\b",
    r"\bcumin\b",
    r"\bjeera\b",                       # Cumin — Indian
    r"\bcoriander\b",
    r"\bdhania\b",                      # Coriander — Indian
    r"\bcardamom\b",
    r"\belaichi\b",                     # Cardamom — Indian
    r"\bcinnamon\b",
    r"\bdalchini\b",                    # Cinnamon — Indian
    r"\bclove\b",
    r"\blavan\b",
    r"\bnutmeg\b",
    r"\bjaiphal\b",                     # Nutmeg — Indian
    r"\bblack pepper\b",
    r"\bkali mirch\b",                  # Black pepper — Indian
    r"\bpepper\b",
    r"\bmirch\b",                       # Chilli — Indian
    r"\bmustard\b",
    r"\brai\b",                         # Mustard — Indian
    r"\bfenugreek\b",
    r"\bmethi\b",                       # Fenugreek — Indian
    r"\basafoetida\b",
    r"\bhing\b",                        # Asafoetida — Indian
    r"\bsaffron\b",
    r"\bkesar\b",                       # Saffron — Indian
    r"\bajwain\b",                      # Carom seeds — Indian
    r"\bcarom\b",
    r"\bstar anise\b",
    r"\bfennel\b",
    r"\bsaunf\b",                       # Fennel seeds — Indian
    r"\bgaram masala\b",                # Indian spice blend
    r"\bchaat masala\b",
    r"\bsambar powder\b",
    r"\brasam powder\b",
    r"\bherb\b",
    r"\bspice\b",
    r"\bmasala\b",

    # ── Nuts & Seeds ──────────────────────────────────
    r"\bcashew\b",                      # Kaju — Indian
    r"\bkaju\b",
    r"\balmond\b",
    r"\bbadaam\b",                      # Almond — Indian
    r"\bpeanut\b",
    r"\bmungphali\b",                   # Peanut — Indian
    r"\bgroundnut\b",
    r"\bpistachio\b",
    r"\bpista\b",                       # Pistachio — Indian
    r"\bwalnut\b",
    r"\bakhrot\b",                      # Walnut — Indian
    r"\bsesame\b",
    r"\btil\b",                         # Sesame — Indian
    r"\bsunflower seed\b",
    r"\bflax seed\b",
    r"\bchia\b",
    r"\bpoppy seed\b",
    r"\bkhas khas\b",                   # Poppy seeds — Indian

    # ── Sweeteners (natural) ──────────────────────────
    r"\bhoney\b",
    r"\bshahad\b",                      # Honey — Indian
    r"\bjaggery\b",                     # Gud — traditional Indian sweetener
    r"\bgud\b",
    r"\bgur\b",
    r"\bstevia\b",                      # INS 960 — natural sweetener
    r"\bxylitol\b",                     # INS 967
    r"\berythritol\b",                  # INS 968
    r"\bmisri\b",                       # Rock sugar — Indian
    r"\bkhand\b",                       # Unrefined sugar — Indian

    # ── Other Natural Ingredients ─────────────────────
    r"\bwater\b",
    r"\begg\b",
    r"\bchicken\b",
    r"\bmutton\b",                      # Common Indian meat
    r"\bgoat\b",
    r"\bfish\b",
    r"\bprawn\b",
    r"\bshrimp\b",
    r"\bsalt\b",
    r"\brock salt\b",
    r"\bsendha namak\b",                # Rock salt — Indian
    r"\bcocoa\b",
    r"\bchocolate\b",
    r"\bvanilla\b",
    r"\bcoffee\b",
    r"\btea\b",
    r"\brose water\b",                  # Common Indian ingredient
    r"\bkewra\b",                       # Kewra water — Indian
    r"\bkevda\b",
    r"\bvinegar\b",
]

HARM_SCORE_MAP = {
    "hazardous": 4, "moderately high": 3,
    "moderate": 2,  "safe": 1,
}

def classify(ingredient):
    ingredient = str(ingredient).lower().strip()
    for p in HAZARDOUS_PATTERNS:
        if re.search(p, ingredient): return "hazardous"
    for p in MODERATELY_HIGH_PATTERNS:
        if re.search(p, ingredient): return "moderately high"
    for p in MODERATE_PATTERNS:
        if re.search(p, ingredient): return "moderate"
    for p in SAFE_PATTERNS:
        if re.search(p, ingredient): return "safe"
    return "moderate"

df["harm_level"] = df["ingredient"].apply(classify)
df["harm_score"] = df["harm_level"].map(HARM_SCORE_MAP)

print("\nFinal Distribution:")
print(df["harm_level"].value_counts())
print(f"\nAverage harm score: {df['harm_score'].mean():.2f}")

df.to_csv("labeled_ingredients.csv", index=False)
print("\n✅ Saved labeled_ingredients.csv")
print("\nSources:")
print("  • FSSAI Food Additives Compendium 2022")
print("  • EFSA Re-evaluation Opinions 2010-2020")
print("  • IARC Monographs — WHO Carcinogen List")
print("  • FSS (Food Products Standards) Regulations India")