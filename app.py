import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from analyze_product import analyze_product

# ══════════════════════════════════════════════════════
# PAGE CONFIG  — must be absolute first call
# ══════════════════════════════════════════════════════
st.set_page_config(page_title="GreenWatch India", page_icon="🌿", layout="wide")

# ══════════════════════════════════════════════════════
# SESSION STATE  — initialise before anything else
# ══════════════════════════════════════════════════════
_DEFAULTS = {
    "dark_mode": False,
    "pname": "", "gname": "", "ingr": "",
    "labs": "", "tag": "", "addn": 0,
}
for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ══════════════════════════════════════════════════════
# SIDEBAR — theme toggle lives here (always visible,
#            never conflicts with page layout)
# ══════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    st.markdown("---")
    # Toggle stored in session state key directly
    st.toggle(
        "🌙 Dark Mode",
        key="dark_mode",          # directly bound to session state
    )
    st.markdown("---")
    st.markdown(
        "<small style='color:#888;'>GreenWatch India<br>"
        "Minor Project · KIIT · 2026</small>",
        unsafe_allow_html=True,
    )

# ══════════════════════════════════════════════════════
# THEME COLOURS  — evaluated AFTER toggle updates state
# ══════════════════════════════════════════════════════
IS_DARK = st.session_state["dark_mode"]   # fresh read every rerun

if IS_DARK:
    BG      = "#0e1117"
    CARD    = "#1a1f2e"
    CARD2   = "#222736"
    BORDER  = "#2e3650"
    TEXT    = "#e8eaf6"
    TEXT2   = "#9ba3c4"
    GREEN   = "#4caf7d"
    GREENS  = "#1a2e25"
    WARN    = "#f07840"
    RED     = "#e05050"
    YELLOW  = "#f0c040"
    HERO    = "linear-gradient(135deg,#0e1117 0%,#1a2e25 50%,#0e1117 100%)"
    STRIP   = "#141922"
    SHADOW  = "0 4px 20px rgba(0,0,0,0.35)"
    HARMBG  = "#3a1a1a"
    HARMBRD = "#e05050"
    HARMTXT = "#e05050"
else:
    BG      = "#f0f7f2"
    CARD    = "#ffffff"
    CARD2   = "#e4f0e8"
    BORDER  = "#b8d8c4"
    TEXT    = "#12271a"
    TEXT2   = "#3a5f46"
    GREEN   = "#1e6b3a"
    GREENS  = "#d4eddf"
    WARN    = "#b84c1a"
    RED     = "#9b1c1c"
    YELLOW  = "#856404"
    HERO    = "linear-gradient(135deg,#d4eddf 0%,#f0f7f2 50%,#c8e6d4 100%)"
    STRIP   = "#dff0e6"
    SHADOW  = "0 4px 20px rgba(30,107,58,0.12)"
    HARMBG  = "#fde8e8"
    HARMBRD = "#9b1c1c"
    HARMTXT = "#9b1c1c"

# ══════════════════════════════════════════════════════
# GLOBAL CSS
# ══════════════════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {{
    font-family: 'DM Sans', sans-serif;
}}
.stApp {{
    background: {BG} !important;
}}
.block-container {{
    padding: 0 !important;
    max-width: 100% !important;
}}
header[data-testid="stHeader"] {{
    background: transparent !important;
}}
#MainMenu, footer {{
    display: none !important;
}}

/* sidebar */
section[data-testid="stSidebar"] {{
    background: {CARD} !important;
    border-right: 1px solid {BORDER} !important;
}}
section[data-testid="stSidebar"] * {{
    color: {TEXT} !important;
}}

/* inputs */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stNumberInput > div > div > input {{
    background: {CARD2} !important;
    border: 1.5px solid {BORDER} !important;
    border-radius: 10px !important;
    color: {TEXT} !important;
}}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {{
    border-color: {GREEN} !important;
    box-shadow: 0 0 0 3px {GREEN}22 !important;
}}
label {{
    color: {TEXT2} !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
}}

/* buttons */
.stButton > button {{
    border-radius: 100px !important;
    border: 1.5px solid {BORDER} !important;
    background: {CARD} !important;
    color: {TEXT} !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    transition: all 0.2s !important;
}}
.stButton > button:hover {{
    border-color: {GREEN} !important;
    color: {GREEN} !important;
}}

/* dataframe */
div[data-testid="stDataFrame"] {{
    border: 1.5px solid {BORDER} !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}}

hr {{
    border-color: {BORDER} !important;
    margin: 24px 0 !important;
}}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# EXAMPLE PRODUCTS
# ══════════════════════════════════════════════════════
EXAMPLES = {
    "🍜 Instant Noodles": {
        "pname": "Masala Magic Instant Noodles", "gname": "Instant Noodles",
        "ingr":  "maida, palm oil, salt, sugar, monosodium glutamate, tartrazine, sodium benzoate, artificial flavor, disodium inosinate",
        "labs":  "no preservatives, natural masala, vegetarian",
        "tag":   "taste bhi health bhi, natural ingredients, ghar jaisa swad", "addn": 6,
    },
    "🍪 Glucose Biscuit": {
        "pname": "Shakti Glucose Biscuit", "gname": "Biscuit",
        "ingr":  "wheat flour, sugar, palm oil, invert syrup, sodium bicarbonate, ammonium bicarbonate, calcium phosphate, artificial flavor",
        "labs":  "whole grain, high energy, no artificial colors",
        "tag":   "wholesome goodness, healthy snack for kids, real wheat nutrition", "addn": 4,
    },
    "🥛 Pure Ghee": {
        "pname": "Amul Pure Ghee", "gname": "Ghee",
        "ingr":  "cow milk ghee", "labs": "", "tag": "", "addn": 0,
    },
    "🧃 Fruit Drink": {
        "pname": "Nature's Best Fruit Drink", "gname": "Fruit Beverage",
        "ingr":  "water, sugar, high fructose corn syrup, tartrazine, sunset yellow, sodium benzoate, artificial flavor, citric acid",
        "labs":  "organic, natural, no preservatives, real fruit",
        "tag":   "100% natural fruit goodness, healthy and refreshing", "addn": 5,
    },
    "🍫 Choco Spread": {
        "pname": "GreenLife Choco Spread", "gname": "Chocolate Spread",
        "ingr":  "sugar, palm oil, cocoa, milk powder, soy lecithin, vanillin",
        "labs":  "organic, no preservatives, vegan",
        "tag":   "eco-friendly natural spread, wholesome ingredients", "addn": 2,
    },
    "🌾 Plain Oats": {
        "pname": "Farm Fresh Rolled Oats", "gname": "Breakfast Cereal",
        "ingr":  "oats, water, honey, salt, cinnamon",
        "labs":  "", "tag": "", "addn": 0,
    },
}

# ══════════════════════════════════════════════════════
# HERO SVG  — plain string concat, never nested f-string
# ══════════════════════════════════════════════════════
svg = "".join([
    f'<svg viewBox="0 0 420 260" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:400px;display:block;margin:0 auto;">',
    f'<rect x="8" y="8" width="404" height="244" rx="18" fill="{CARD}" stroke="{BORDER}" stroke-width="1.5"/>',
    f'<rect x="32" y="32" width="110" height="150" rx="8" fill="{GREENS}"/>',
    f'<ellipse cx="87" cy="66" rx="18" ry="22" fill="{GREEN}" opacity="0.8" transform="rotate(-15,87,66)"/>',
    f'<line x1="87" y1="88" x2="87" y2="50" stroke="{GREEN}" stroke-width="2.5" stroke-linecap="round"/>',
    f'<line x1="87" y1="72" x2="100" y2="63" stroke="{GREEN}" stroke-width="1.5" stroke-linecap="round"/>',
    f'<line x1="87" y1="63" x2="74" y2="55" stroke="{GREEN}" stroke-width="1.5" stroke-linecap="round"/>',
    f'<rect x="37" y="104" width="98" height="18" rx="5" fill="{GREEN}"/>',
    '<text x="86" y="116" text-anchor="middle" font-family="DM Sans" font-size="8" font-weight="700" fill="white">100% NATURAL</text>',
    f'<rect x="37" y="130" width="98" height="44" rx="4" fill="{CARD2}"/>',
    f'<text x="86" y="142" text-anchor="middle" font-family="DM Sans" font-size="6" fill="{TEXT2}">Ingredients:</text>',
    f'<text x="86" y="153" text-anchor="middle" font-family="DM Sans" font-size="5.5" fill="{WARN}">Sugar, Palm Oil, Tartrazine</text>',
    f'<text x="86" y="163" text-anchor="middle" font-family="DM Sans" font-size="5.5" fill="{WARN}">Sodium Benzoate, MSG...</text>',
    f'<path d="M155 118 L188 118" stroke="{TEXT2}" stroke-width="1.5" stroke-dasharray="4,3"/>',
    f'<polygon points="188,114 196,118 188,122" fill="{TEXT2}"/>',
    f'<rect x="200" y="32" width="204" height="196" rx="10" fill="{GREENS}"/>',
    f'<text x="302" y="54" text-anchor="middle" font-family="Playfair Display" font-size="10" font-weight="700" fill="{TEXT}">GreenWatch Score</text>',
    f'<circle cx="302" cy="110" r="38" fill="none" stroke="{CARD2}" stroke-width="7"/>',
    f'<circle cx="302" cy="110" r="38" fill="none" stroke="{WARN}" stroke-width="7" stroke-dasharray="190" stroke-dashoffset="48" stroke-linecap="round" transform="rotate(-90,302,110)"/>',
    f'<text x="302" y="105" text-anchor="middle" font-family="Playfair Display" font-size="18" font-weight="800" fill="{WARN}">78</text>',
    f'<text x="302" y="118" text-anchor="middle" font-family="DM Sans" font-size="7" fill="{TEXT2}">/100</text>',
    f'<rect x="210" y="162" width="184" height="20" rx="5" fill="{WARN}" opacity="0.2"/>',
    f'<text x="302" y="175" text-anchor="middle" font-family="DM Sans" font-size="8" font-weight="700" fill="{WARN}">STRONG GREENWASHING</text>',
    f'<rect x="210" y="190" width="58" height="13" rx="6" fill="{GREEN}" opacity="0.25"/>',
    f'<text x="239" y="200" text-anchor="middle" font-family="DM Sans" font-size="6" fill="{GREEN}">organic</text>',
    f'<rect x="274" y="190" width="118" height="13" rx="6" fill="{GREEN}" opacity="0.25"/>',
    f'<text x="333" y="200" text-anchor="middle" font-family="DM Sans" font-size="6" fill="{GREEN}">no preservatives</text>',
    f'<text x="218" y="220" font-family="DM Sans" font-size="7" fill="{WARN}">Tartrazine · Sodium Benzoate detected</text>',
    '</svg>',
])

# ══════════════════════════════════════════════════════
# HERO
# ══════════════════════════════════════════════════════
h1, h2 = st.columns([3, 2])

with h1:
    st.markdown(f"""
<div style="background:{HERO};padding:52px 48px 44px;border-bottom:1px solid {BORDER};">
  <p style="font-family:'Playfair Display',serif;font-size:3rem;font-weight:800;color:{TEXT};margin:0;line-height:1.1;">
    🌿 GreenWatch<br><span style="color:{GREEN};">India</span>
  </p>
  <p style="font-size:1rem;color:{TEXT2};margin:14px 0 0;font-weight:300;max-width:500px;line-height:1.65;">
    Exposing misleading food labels using NLP &amp; Machine Learning.
    Know what&#39;s really inside your food — before you buy it.
  </p>
  <div style="display:flex;gap:10px;margin-top:24px;flex-wrap:wrap;">
    <span style="background:{GREENS};color:{GREEN};border:1px solid {BORDER};border-radius:100px;padding:5px 14px;font-size:0.78rem;font-weight:600;">🔬 FSSAI 2022 Backed</span>
    <span style="background:{GREENS};color:{GREEN};border:1px solid {BORDER};border-radius:100px;padding:5px 14px;font-size:0.78rem;font-weight:600;">🇮🇳 India Focused</span>
    <span style="background:{GREENS};color:{GREEN};border:1px solid {BORDER};border-radius:100px;padding:5px 14px;font-size:0.78rem;font-weight:600;">🤖 ML Powered</span>
    <span style="background:{GREENS};color:{GREEN};border:1px solid {BORDER};border-radius:100px;padding:5px 14px;font-size:0.78rem;font-weight:600;">🌐 OpenFoodFacts</span>
  </div>
</div>
""", unsafe_allow_html=True)

with h2:
    st.markdown(f"""
<div style="background:{HERO};padding:32px;display:flex;align-items:center;justify-content:center;border-bottom:1px solid {BORDER};min-height:280px;">
  {svg}
</div>
""", unsafe_allow_html=True)

# ── Info strip ─────────────────────────────────────────
st.markdown(f"""
<div style="background:{STRIP};padding:22px 48px;border-bottom:1px solid {BORDER};">
  <p style="font-family:'Playfair Display',serif;font-size:1rem;font-weight:700;color:{TEXT};margin:0 0 8px;">⚠️ What is Food Greenwashing?</p>
  <p style="font-size:0.88rem;color:{TEXT2};margin:0;line-height:1.8;max-width:950px;">
    Greenwashing is when food brands use terms like
    <strong style="color:{GREEN};">"natural", "organic", "shudh", or "no preservatives"</strong>
    on packaging — but the actual ingredients tell a different story. Products claiming to be natural while containing
    <strong style="color:{WARN};">Tartrazine (INS 102), Sodium Benzoate (INS 211), or MSG (INS 621)</strong>
    are misleading consumers. GreenWatch India detects this automatically.
  </p>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════
def section_head(title):
    st.markdown(
        f"<p style='font-family:Playfair Display,serif;font-size:1.35rem;"
        f"font-weight:700;color:{TEXT};margin:0 0 14px;padding-bottom:8px;"
        f"border-bottom:2px solid {BORDER};'>{title}</p>",
        unsafe_allow_html=True,
    )

# ══════════════════════════════════════════════════════
# MAIN CONTENT
# ══════════════════════════════════════════════════════
st.markdown("<div style='padding:32px 48px;max-width:1300px;margin:0 auto;'>",
            unsafe_allow_html=True)

# ── Example buttons ────────────────────────────────────
section_head("💡 Try an Example Indian Product")
ex_keys = list(EXAMPLES.keys())
for col, key in zip(st.columns(6), ex_keys):
    with col:
        if st.button(key, use_container_width=True, key=f"ex_{key}"):
            for k in ["pname", "gname", "ingr", "labs", "tag", "addn"]:
                st.session_state[k] = EXAMPLES[key][k]
            st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# ── Input form ─────────────────────────────────────────
section_head("📋 Enter Product Details")

c1, c2, c3 = st.columns([2, 2, 1])
with c1: st.text_input("Product Name",           placeholder="e.g. Maggi Masala Noodles", key="pname")
with c2: st.text_input("Generic Name / Category", placeholder="e.g. Instant Noodles, Biscuit", key="gname")
with c3: st.number_input("No. of Additives", min_value=0, max_value=50, step=1, key="addn")

st.text_area(
    "Ingredients (comma separated — as printed on pack)",
    placeholder="e.g. maida, palm oil, salt, sugar, monosodium glutamate, tartrazine, sodium benzoate",
    height=100, key="ingr",
)

c4, c5 = st.columns(2)
with c4: st.text_input("Labels / Certifications on Pack", placeholder="e.g. organic, no preservatives, vegetarian", key="labs")
with c5: st.text_input("Tagline / Marketing Text",        placeholder="e.g. shudh aur natural, ghar jaisa swad", key="tag")

st.markdown("<br>", unsafe_allow_html=True)
go_btn = st.button("🔍  Analyze for Greenwashing", type="primary")

# ══════════════════════════════════════════════════════
# RESULTS
# ══════════════════════════════════════════════════════
if go_btn:
    if not st.session_state["ingr"].strip():
        st.error("Please enter the ingredients to analyze.")
    else:
        with st.spinner("Analyzing against FSSAI database..."):
            res = analyze_product(
                product_name     = st.session_state["pname"] or "Unknown Product",
                generic_name     = st.session_state["gname"] or "Unknown Category",
                ingredients_text = st.session_state["ingr"],
                labels_text      = st.session_state["labs"],
                tagline_text     = st.session_state["tag"],
                additives_n      = st.session_state["addn"],
            )

        score = res["greenwash_score"]
        vc    = res["verdict_color"]

        sc_hex = {"green": GREEN,  "yellow": YELLOW, "orange": WARN,    "red": RED   }.get(vc, TEXT2)
        pr_hex = {"green":"#4caf7d","yellow":"#f0c040","orange":"#f07840","red":"#e05050"}.get(vc,"#888")
        sc_bg  = ({"green": GREENS,"yellow":"#2e2a10","orange":"#2e1a10","red":"#2e1010"}.get(vc, CARD2)
                  if IS_DARK else
                  {"green":"#d4eddf","yellow":"#fdf8de","orange":"#fdeede","red":"#fde8e8"}.get(vc, CARD2))

        st.markdown("<hr>", unsafe_allow_html=True)
        section_head("📊 Analysis Results")

        # ── Row 1: Score | Breakdown | Claims ──────────
        r1, r2, r3 = st.columns(3)

        with r1:
            st.markdown(f"""
<div style="background:{CARD};border:1.5px solid {BORDER};border-radius:16px;padding:28px;box-shadow:{SHADOW};text-align:center;min-height:260px;">
  <p style="font-family:'Playfair Display',serif;font-size:1.05rem;font-weight:700;color:{TEXT};margin:0 0 12px;">Greenwash Score</p>
  <p style="font-family:'Playfair Display',serif;font-size:4.5rem;font-weight:800;color:{sc_hex};margin:0;line-height:1;">{score}</p>
  <p style="font-size:0.78rem;font-weight:600;letter-spacing:0.1em;color:{TEXT2};margin:4px 0 14px;text-transform:uppercase;">out of 100</p>
  <div style="height:10px;background:{BORDER};border-radius:100px;overflow:hidden;max-width:220px;margin:0 auto 14px;">
    <div style="width:{score}%;height:100%;background:{pr_hex};border-radius:100px;"></div>
  </div>
  <div style="border-radius:10px;padding:12px 16px;font-size:0.95rem;font-weight:700;color:{sc_hex};border:1.5px solid {sc_hex};background:{sc_bg};">
    {res['verdict']}
  </div>
</div>""", unsafe_allow_html=True)

        with r2:
            items_html = ""
            for lbl, val in [
                ("🧪 Harm Score",  f"{res['harm_score_100']}/100"),
                ("⚡ Mismatch",    f"{res['mismatch_score']}/100"),
                ("📢 Claims",      f"{res['claim_score']}/100"),
                ("⚗️ Additives",  f"{res['additives_penalty']}/30"),
            ]:
                items_html += f"""
<div style="background:{CARD2};border-radius:10px;padding:12px 14px;border:1px solid {BORDER};">
  <div style="font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:{TEXT2};margin-bottom:4px;">{lbl}</div>
  <div style="font-size:1.4rem;font-weight:700;color:{TEXT};">{val}</div>
</div>"""

            st.markdown(f"""
<div style="background:{CARD};border:1.5px solid {BORDER};border-radius:16px;padding:28px;box-shadow:{SHADOW};min-height:260px;">
  <p style="font-family:'Playfair Display',serif;font-size:1.05rem;font-weight:700;color:{TEXT};margin:0 0 14px;">📐 Score Breakdown</p>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">{items_html}</div>
</div>""", unsafe_allow_html=True)

        with r3:
            # Build entire card as one string — fixes claims outside box bug
            claims_html = ""
            if res["all_claims"]:
                if res["label_claims"]:
                    claims_html += f'<p style="font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:{TEXT2};margin:0 0 8px;">From Labels</p>'
                    for c in res["label_claims"]:
                        claims_html += f'<span style="display:inline-block;background:{GREENS};color:{GREEN};border:1px solid {BORDER};border-radius:100px;padding:4px 12px;font-size:0.8rem;font-weight:600;margin:3px 3px 3px 0;">🏷 {c}</span>'
                if res["tagline_claims"]:
                    claims_html += f'<p style="font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:{TEXT2};margin:12px 0 8px;">From Tagline</p>'
                    for c in res["tagline_claims"]:
                        claims_html += f'<span style="display:inline-block;background:{GREENS};color:{GREEN};border:1px solid {BORDER};border-radius:100px;padding:4px 12px;font-size:0.8rem;font-weight:600;margin:3px 3px 3px 0;">💬 {c}</span>'
            else:
                claims_html = f'<p style="color:{TEXT2};font-size:0.88rem;margin:0;">No green claims detected.</p>'

            st.markdown(f"""
<div style="background:{CARD};border:1.5px solid {BORDER};border-radius:16px;padding:28px;box-shadow:{SHADOW};min-height:260px;">
  <p style="font-family:'Playfair Display',serif;font-size:1.05rem;font-weight:700;color:{TEXT};margin:0 0 14px;">🏷 Green Claims</p>
  {claims_html}
</div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Harmful alert ───────────────────────────────
        if res["harmful_ingredients"]:
            pills = "".join([
                f'<span style="display:inline-block;background:{HARMBG};color:{HARMTXT};border:1px solid {HARMBRD};border-radius:100px;padding:5px 14px;font-size:0.82rem;font-weight:700;margin:3px;">🔴 {i}</span>'
                for i in res["harmful_ingredients"]
            ])
            st.markdown(f"""
<div style="background:{HARMBG};border:1.5px solid {HARMBRD};border-radius:14px;padding:16px 22px;margin-bottom:16px;">
  <p style="font-weight:700;color:{HARMTXT};margin:0 0 10px;font-size:0.92rem;">⚠️ Harmful Ingredients — classified by FSSAI / EFSA / IARC</p>
  {pills}
</div>""", unsafe_allow_html=True)

        # ── Row 2: Table | Chart ────────────────────────
        t1, t2 = st.columns([3, 2])

        with t1:
            section_head("🧪 Full Ingredient Analysis")
            emap = {"hazardous": "🔴", "moderately high": "🟠", "moderate": "🟡", "safe": "🟢"}
            rows = [
                {
                    "Ingredient": ing.title(),
                    "Risk Level": f"{emap.get(d['harm_level'], '🟡')}  {d['harm_level'].title()}",
                    "Confidence": f"{int(d['confidence'] * 100)}%",
                }
                for ing, d in res["per_ingredient"].items()
            ]
            if rows:
                st.dataframe(
                    pd.DataFrame(rows),
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Ingredient": st.column_config.TextColumn("🧪 Ingredient", width="large"),
                        "Risk Level": st.column_config.TextColumn("⚠️ Risk Level", width="medium"),
                        "Confidence": st.column_config.TextColumn("📊 Confidence", width="small"),
                    },
                )

        with t2:
            section_head("🥧 Risk Distribution")
            dist  = res["harm_distribution"]
            total = res["total_ingredients"]

            if total > 0:
                fig = go.Figure(data=[go.Pie(
                    labels=list(dist.keys()),
                    values=list(dist.values()),
                    marker=dict(
                        colors=["#4caf7d", "#f0c040", "#f07840", "#e05050"],
                        line=dict(color="rgba(0,0,0,0)", width=0),
                    ),
                    hole=0.55,
                    textfont=dict(size=12, family="DM Sans"),
                    hovertemplate="<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>",
                )])
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    showlegend=True,
                    legend=dict(orientation="v", x=1.0, y=0.5,
                                font=dict(size=11, family="DM Sans", color=TEXT2)),
                    margin=dict(t=10, b=10, l=10, r=10),
                    height=280,
                    annotations=[dict(
                        text=f"<b>{total}</b><br>items",
                        x=0.38, y=0.5,
                        font_size=13, font_family="DM Sans", font_color=TEXT2,
                        showarrow=False,
                    )],
                )
                st.plotly_chart(fig, use_container_width=True,
                                config={"displayModeBar": False})

            meaning = (
                "makes significant green claims that its ingredients do not support — a clear sign of greenwashing." if score > 75 else
                "has concerning claims or ingredients that may mislead consumers." if score > 50 else
                "has minor discrepancies between its claims and ingredients." if score > 25 else
                "appears honest — its marketing aligns well with its actual ingredients."
            )
            st.markdown(f"""
<div style="background:{CARD};border:1.5px solid {BORDER};border-radius:14px;padding:18px 20px;margin-top:8px;box-shadow:{SHADOW};">
  <p style="font-family:'Playfair Display',serif;font-size:0.95rem;font-weight:700;color:{TEXT};margin:0 0 8px;">📖 What This Means</p>
  <p style="font-size:0.85rem;color:{TEXT2};line-height:1.7;margin:0;">
    A score of <strong style="color:{sc_hex};">{score}/100</strong> means this product {meaning}
  </p>
</div>""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════
st.markdown(f"""
<div style="text-align:center;padding:28px;color:{TEXT2};font-size:0.82rem;border-top:1px solid {BORDER};margin-top:40px;">
  <strong style="color:{TEXT};">GreenWatch India</strong> — NLP-based Food Greenwashing Detection<br>
  <span style="display:block;margin-top:5px;">
    FSSAI Compendium 2022 &nbsp;|&nbsp; EFSA Re-evaluation &nbsp;|&nbsp; IARC Monographs &nbsp;|&nbsp; OpenFoodFacts
  </span>
  <span style="display:block;margin-top:4px;font-size:0.75rem;">
    Minor Project · School of Computer Engineering · KIIT · March 2026
  </span>
</div>
""", unsafe_allow_html=True)