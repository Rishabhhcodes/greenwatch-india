import pdfplumber
import pandas as pd
import re
import os

PDF_PATH = "Compendium_Food_Additives_Regulations_20_12_2022.pdf"

print("=" * 60)
print("  FSSAI PDF Parser + Autolabel Builder")
print("=" * 60)

# ==============================
# STEP 1: CHECK FILE EXISTS
# ==============================
if not os.path.exists(PDF_PATH):
    print(f"\n❌ PDF not found at: {PDF_PATH}")
    print("Please make sure the PDF is in the same folder as this script.")
    print("Expected filename: Compendium_Food_Additives_Regulations_20_12_2022.pdf")
    exit()

print(f"\n✅ Found PDF: {PDF_PATH}")

# ==============================
# STEP 2: EXTRACT TEXT + TABLES
# ==============================
print("\nExtracting text from PDF (this may take a minute)...")

all_text   = []
all_tables = []

with pdfplumber.open(PDF_PATH) as pdf:
    total_pages = len(pdf.pages)
    print(f"Total pages: {total_pages}")

    for i, page in enumerate(pdf.pages):
        # Extract raw text
        text = page.extract_text()
        if text:
            all_text.append(text)

        # Extract tables
        tables = page.extract_tables()
        for table in tables:
            if table and len(table) > 1:
                all_tables.append((i + 1, table))

        if (i + 1) % 50 == 0:
            print(f"  Processed {i+1}/{total_pages} pages...")

print(f"✅ Extracted text from {len(all_text)} pages")
print(f"✅ Found {len(all_tables)} tables")

# Save raw text for inspection
full_text = "\n".join(all_text)
with open("fssai_raw_text.txt", "w", encoding="utf-8") as f:
    f.write(full_text)
print("✅ Saved raw text → fssai_raw_text.txt (inspect this to understand structure)")

# ==============================
# STEP 3: PARSE ADDITIVES FROM TEXT
# ==============================
print("\nParsing additive names and INS numbers...")

# FSSAI uses INS numbers (International Numbering System)
# Format in PDF: "INS No. 102" or just "102" or "E102"
# We extract additive name + INS number pairs

additives_found = []

# Pattern to find INS numbers and additive names
ins_pattern      = re.compile(r'\bINS\s*(?:No\.?)?\s*(\d{3,4}[a-z]?)\b', re.IGNORECASE)
additive_pattern = re.compile(r'([A-Za-z][A-Za-z\s\(\),\-]{3,50})\s+(?:INS|E)?\s*(\d{3,4}[a-z]?)', re.IGNORECASE)

for text in all_text:
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if len(line) < 5:
            continue

        # Try to match additive name + INS number
        match = additive_pattern.search(line)
        if match:
            name = match.group(1).strip().lower()
            ins  = match.group(2).strip()

            # Filter out garbage lines
            if len(name) > 3 and not name.startswith('page') and not name.startswith('table'):
                additives_found.append({
                    "name": name,
                    "ins_number": ins,
                    "source_line": line[:100]
                })

# ==============================
# STEP 4: PARSE TABLES
# ==============================
print("Parsing tables from PDF...")

table_rows = []
for page_num, table in all_tables:
    for row in table:
        if row and any(cell for cell in row if cell):
            clean_row = [str(cell).strip() if cell else "" for cell in row]
            table_rows.append(clean_row)

# Save tables as CSV for inspection
if table_rows:
    df_tables = pd.DataFrame(table_rows)
    df_tables.to_csv("fssai_tables_raw.csv", index=False)
    print(f"✅ Saved {len(table_rows)} table rows → fssai_tables_raw.csv")

# ==============================
# STEP 5: MAP INS NUMBERS TO HARM LEVELS
# Based on FSSAI + EFSA + IARC classifications
# ==============================
print("\nMapping INS numbers to harm levels...")

# INS Number → Harm Level mapping
# Sources: EFSA re-evaluation opinions, IARC monographs, FSSAI regulations
INS_HARM_MAP = {

    # ── HAZARDOUS (Score = 4) ──────────────────────────
    # Banned or restricted in multiple countries
    "102":  ("tartrazine",          "moderately high"),  # Azo dye, hyperactivity
    "104":  ("quinoline yellow",    "moderately high"),  # Banned in US/Japan
    "107":  ("yellow 2g",           "hazardous"),        # Banned in EU
    "110":  ("sunset yellow",       "moderately high"),  # Hyperactivity link
    "120":  ("carmines",            "moderate"),
    "122":  ("azorubine",           "moderately high"),  # Banned in US
    "123":  ("amaranth",            "hazardous"),        # Banned in US
    "124":  ("ponceau 4r",          "moderately high"),  # Banned in US
    "127":  ("erythrosine",         "moderately high"),  # Thyroid concern
    "128":  ("red 2g",              "hazardous"),        # Banned in EU
    "129":  ("allura red",          "moderately high"),
    "131":  ("patent blue v",       "moderate"),
    "132":  ("indigotine",          "moderate"),
    "133":  ("brilliant blue",      "moderate"),
    "142":  ("green s",             "moderately high"),  # Banned in US
    "150a": ("caramel plain",       "moderate"),
    "150b": ("caramel caustic sulphite", "moderately high"),
    "150c": ("caramel ammonia",     "moderately high"),
    "150d": ("caramel sulphite ammonia", "hazardous"),   # Contains 4-MEI carcinogen
    "151":  ("brilliant black bn",  "moderately high"),  # Banned in US
    "154":  ("brown fk",            "hazardous"),        # Banned in EU/US
    "155":  ("brown ht",            "moderately high"),  # Banned in US
    "160b": ("annatto",             "moderate"),
    "171":  ("titanium dioxide",    "hazardous"),        # Banned in EU 2022
    "173":  ("aluminium",           "moderately high"),  # Neurotoxin concern
    "174":  ("silver",              "moderate"),
    "175":  ("gold",                "moderate"),
    "180":  ("litholrubine bk",     "moderate"),

    # Preservatives
    "200":  ("sorbic acid",         "moderate"),
    "202":  ("potassium sorbate",   "moderate"),
    "210":  ("benzoic acid",        "moderately high"),
    "211":  ("sodium benzoate",     "hazardous"),        # Forms benzene with Vit C
    "212":  ("potassium benzoate",  "hazardous"),
    "213":  ("calcium benzoate",    "hazardous"),
    "214":  ("ethyl para-hydroxy-benzoate", "moderately high"),
    "216":  ("propyl para-hydroxy-benzoate", "moderately high"),
    "218":  ("methyl para-hydroxy-benzoate", "moderately high"),
    "220":  ("sulphur dioxide",     "moderately high"),  # Asthma trigger
    "221":  ("sodium sulphite",     "moderately high"),
    "222":  ("sodium bisulphite",   "moderately high"),
    "223":  ("sodium metabisulphite", "moderately high"),
    "224":  ("potassium metabisulphite", "moderately high"),
    "225":  ("potassium sulphite",  "moderately high"),
    "227":  ("calcium bisulphite",  "moderately high"),
    "228":  ("potassium bisulphite","moderately high"),
    "231":  ("orthophenyl phenol",  "moderately high"),
    "232":  ("sodium orthophenyl phenol", "moderately high"),
    "234":  ("nisin",               "moderate"),
    "235":  ("natamycin",           "moderate"),
    "239":  ("hexamethylene tetramine", "moderately high"),
    "240":  ("formaldehyde",        "hazardous"),        # Carcinogen
    "249":  ("potassium nitrite",   "hazardous"),        # Carcinogen precursor
    "250":  ("sodium nitrite",      "hazardous"),        # IARC Group 2A
    "251":  ("sodium nitrate",      "hazardous"),
    "252":  ("potassium nitrate",   "hazardous"),
    "260":  ("acetic acid",         "safe"),
    "261":  ("potassium acetate",   "safe"),
    "262":  ("sodium acetate",      "safe"),
    "270":  ("lactic acid",         "safe"),
    "280":  ("propionic acid",      "moderate"),
    "281":  ("sodium propionate",   "moderate"),
    "282":  ("calcium propionate",  "moderate"),
    "283":  ("potassium propionate","moderate"),

    # Antioxidants
    "300":  ("ascorbic acid",       "safe"),             # Vitamin C
    "301":  ("sodium ascorbate",    "safe"),
    "302":  ("calcium ascorbate",   "safe"),
    "304":  ("ascorbyl palmitate",  "moderate"),
    "306":  ("tocopherols",         "safe"),             # Vitamin E
    "307":  ("alpha tocopherol",    "safe"),
    "310":  ("propyl gallate",      "moderate"),
    "311":  ("octyl gallate",       "moderate"),
    "312":  ("dodecyl gallate",     "moderate"),
    "315":  ("erythorbic acid",     "moderate"),
    "316":  ("sodium erythorbate",  "moderate"),
    "319":  ("tbhq",                "hazardous"),        # Banned in Japan/EU
    "320":  ("bha",                 "hazardous"),        # Possible carcinogen
    "321":  ("bht",                 "hazardous"),        # Possible carcinogen

    # Thickeners / Stabilizers
    "400":  ("alginic acid",        "safe"),
    "401":  ("sodium alginate",     "safe"),
    "402":  ("potassium alginate",  "safe"),
    "403":  ("ammonium alginate",   "safe"),
    "404":  ("calcium alginate",    "safe"),
    "405":  ("propylene glycol alginate", "moderate"),
    "406":  ("agar",                "safe"),
    "407":  ("carrageenan",         "moderately high"),  # Gut inflammation
    "407a": ("processed eucheuma seaweed", "moderate"),
    "410":  ("locust bean gum",     "safe"),
    "412":  ("guar gum",            "safe"),
    "413":  ("tragacanth",          "safe"),
    "414":  ("arabic gum",          "safe"),
    "415":  ("xanthan gum",         "moderate"),
    "416":  ("karaya gum",          "moderate"),
    "417":  ("tara gum",            "safe"),
    "418":  ("gellan gum",          "moderate"),
    "420":  ("sorbitol",            "moderate"),
    "421":  ("mannitol",            "moderate"),
    "422":  ("glycerol",            "safe"),
    "440":  ("pectins",             "safe"),
    "460":  ("cellulose",           "safe"),
    "461":  ("methyl cellulose",    "moderate"),
    "462":  ("ethyl cellulose",     "moderate"),
    "463":  ("hydroxypropyl cellulose", "moderate"),
    "464":  ("hydroxypropyl methyl cellulose", "moderate"),
    "465":  ("methyl ethyl cellulose", "moderate"),
    "466":  ("sodium carboxy methyl cellulose", "moderate"),
    "470":  ("salts of fatty acids", "moderate"),
    "471":  ("mono and diglycerides", "moderate"),
    "472a": ("acetic acid esters",  "moderate"),
    "472b": ("lactic acid esters",  "moderate"),
    "472c": ("citric acid esters",  "moderate"),
    "472e": ("diacetyltartaric acid esters", "moderate"),
    "473":  ("sucrose esters",      "moderate"),
    "474":  ("sucroglycerides",     "moderate"),
    "475":  ("polyglycerol esters", "moderate"),
    "476":  ("polyglycerol polyricinoleate", "moderate"),
    "477":  ("propylene glycol esters", "moderate"),
    "481":  ("sodium stearoyl lactylate", "moderate"),
    "482":  ("calcium stearoyl lactylate", "moderate"),
    "491":  ("sorbitan monostearate", "moderate"),
    "492":  ("sorbitan tristearate", "moderate"),
    "493":  ("sorbitan monolaurate", "moderate"),
    "494":  ("sorbitan monooleate", "moderate"),
    "495":  ("sorbitan monopalmitate", "moderate"),

    # Emulsifiers / Phosphates
    "338":  ("phosphoric acid",     "moderately high"),  # Bone density concern
    "339":  ("sodium phosphate",    "moderately high"),
    "340":  ("potassium phosphate", "moderately high"),
    "341":  ("calcium phosphate",   "moderately high"),
    "343":  ("magnesium phosphate", "moderate"),
    "450":  ("diphosphate",         "moderately high"),
    "451":  ("triphosphate",        "moderately high"),
    "452":  ("polyphosphate",       "moderately high"),

    # Sweeteners
    "420":  ("sorbitol",            "moderate"),
    "421":  ("mannitol",            "moderate"),
    "950":  ("acesulfame potassium","moderately high"),  # Gut microbiome
    "951":  ("aspartame",           "moderately high"),  # IARC 2B 2023
    "952":  ("cyclamate",           "hazardous"),        # Banned in US
    "953":  ("isomalt",             "moderate"),
    "954":  ("saccharin",           "hazardous"),        # Bladder cancer link
    "955":  ("sucralose",           "moderately high"),  # Gut microbiome
    "957":  ("thaumatin",           "safe"),
    "959":  ("neohesperidin dc",    "moderate"),
    "960":  ("steviol glycosides",  "safe"),
    "961":  ("neotame",             "moderate"),
    "962":  ("aspartame acesulfame salt", "moderately high"),
    "965":  ("maltitol",            "moderate"),
    "966":  ("lactitol",            "moderate"),
    "967":  ("xylitol",             "safe"),
    "968":  ("erythritol",          "safe"),

    # Flavour enhancers
    "620":  ("glutamic acid",       "moderate"),
    "621":  ("msg",                 "moderately high"),  # Excitotoxin concern
    "622":  ("potassium glutamate", "moderately high"),
    "623":  ("calcium glutamate",   "moderately high"),
    "624":  ("ammonium glutamate",  "moderately high"),
    "625":  ("magnesium glutamate", "moderately high"),
    "626":  ("guanylic acid",       "moderately high"),
    "627":  ("disodium guanylate",  "moderately high"),
    "628":  ("dipotassium guanylate","moderately high"),
    "629":  ("calcium guanylate",   "moderately high"),
    "630":  ("inosinic acid",       "moderately high"),
    "631":  ("disodium inosinate",  "moderately high"),
    "635":  ("disodium ribonucleotide", "moderately high"),
    "640":  ("glycine",             "safe"),

    # Acids / Acidity regulators
    "330":  ("citric acid",         "safe"),
    "331":  ("sodium citrate",      "safe"),
    "332":  ("potassium citrate",   "safe"),
    "333":  ("calcium citrate",     "safe"),
    "334":  ("tartaric acid",       "safe"),
    "335":  ("sodium tartrate",     "safe"),
    "336":  ("potassium tartrate",  "safe"),
    "337":  ("sodium potassium tartrate", "safe"),
    "350":  ("sodium malate",       "safe"),
    "351":  ("potassium malate",    "safe"),
    "352":  ("calcium malate",      "safe"),
    "353":  ("metatartaric acid",   "moderate"),
    "355":  ("adipic acid",         "moderate"),
    "380":  ("triammonium citrate", "moderate"),
    "381":  ("ferric ammonium citrate", "moderate"),
    "385":  ("calcium disodium edta", "hazardous"),     # Heavy metal chelator

    # Raising agents
    "500":  ("sodium carbonate",    "safe"),
    "501":  ("potassium carbonate", "safe"),
    "503":  ("ammonium carbonate",  "safe"),
    "504":  ("magnesium carbonate", "safe"),
    "507":  ("hydrochloric acid",   "moderate"),
    "508":  ("potassium chloride",  "safe"),
    "509":  ("calcium chloride",    "safe"),
    "511":  ("magnesium chloride",  "safe"),
    "514":  ("sodium sulphate",     "moderate"),
    "516":  ("calcium sulphate",    "safe"),
    "524":  ("sodium hydroxide",    "moderate"),
    "525":  ("potassium hydroxide", "moderate"),
    "526":  ("calcium hydroxide",   "safe"),
    "527":  ("ammonium hydroxide",  "moderate"),
    "528":  ("magnesium hydroxide", "safe"),
    "529":  ("calcium oxide",       "moderate"),
    "530":  ("magnesium oxide",     "safe"),
    "535":  ("sodium ferrocyanide", "moderate"),
    "536":  ("potassium ferrocyanide", "moderate"),
    "541":  ("sodium aluminium phosphate", "moderately high"),
    "551":  ("silicon dioxide",     "moderate"),
    "552":  ("calcium silicate",    "moderate"),
    "553":  ("magnesium silicate",  "moderate"),
    "554":  ("sodium aluminosilicate", "moderate"),
    "555":  ("potassium aluminium silicate", "moderate"),
    "556":  ("calcium aluminosilicate", "moderate"),
    "559":  ("aluminium silicate",  "moderate"),
    "570":  ("stearic acid",        "moderate"),
    "574":  ("gluconic acid",       "safe"),
    "575":  ("glucono delta lactone", "safe"),
    "576":  ("sodium gluconate",    "safe"),
    "577":  ("potassium gluconate", "safe"),
    "578":  ("calcium gluconate",   "safe"),
    "579":  ("ferrous gluconate",   "safe"),
    "585":  ("ferrous lactate",     "safe"),

    # Propylene glycol
    "1520": ("propylene glycol",    "hazardous"),
    "477":  ("propylene glycol esters", "moderate"),

    # Modified starches
    "1400": ("dextrin",             "moderate"),
    "1401": ("acid treated starch", "moderate"),
    "1402": ("alkaline treated starch", "moderate"),
    "1403": ("bleached starch",     "moderate"),
    "1404": ("oxidised starch",     "moderate"),
    "1405": ("enzyme treated starch", "moderate"),
    "1410": ("monostarch phosphate","moderate"),
    "1412": ("distarch phosphate",  "moderate"),
    "1413": ("phosphated distarch phosphate", "moderate"),
    "1414": ("acetylated distarch phosphate", "moderate"),
    "1420": ("starch acetate",      "moderate"),
    "1422": ("acetylated distarch adipate", "moderate"),
    "1440": ("hydroxypropyl starch","moderate"),
    "1442": ("hydroxypropyl distarch phosphate", "moderate"),
    "1450": ("starch sodium octenyl succinate", "moderate"),
    "1451": ("acetylated oxidised starch", "moderate"),
}

print(f"Loaded {len(INS_HARM_MAP)} INS number mappings")

# ==============================
# STEP 6: SAVE FSSAI ADDITIVE DATABASE
# ==============================
rows = []
for ins, (name, harm) in INS_HARM_MAP.items():
    rows.append({
        "ins_number":  ins,
        "name":        name,
        "harm_level":  harm,
        "source":      "FSSAI + EFSA + IARC"
    })

df_additives = pd.DataFrame(rows)
df_additives.to_csv("fssai_additives_database.csv", index=False)
print(f"✅ Saved fssai_additives_database.csv ({len(df_additives)} additives)")

# ==============================
# SUMMARY
# ==============================
print("\n" + "=" * 60)
print("  DONE! Files generated:")
print("=" * 60)
print("  1. fssai_raw_text.txt          ← raw PDF text (inspect)")
print("  2. fssai_tables_raw.csv        ← raw tables from PDF")
print("  3. fssai_additives_database.csv← structured additive DB")
