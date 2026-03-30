import re

# ==============================
# GREEN CLAIM DETECTOR — INDIA FOCUSED
# Detects greenwashing claims common in
# Indian food product marketing
# ==============================

# ── Indian Label Claims ────────────────────────────────
# Official certifications used in India
LABEL_CLAIMS = [
    # FSSAI certifications
    r"\bfssai\s*approved\b",
    r"\bfssai\s*certified\b",
    r"\beat\s*right\b",                 # FSSAI Eat Right label

    # Organic / Natural claims
    r"\borganic\b",
    r"\bjaivik\b",                      # Organic in Hindi
    r"\bpgS certified\b",               # India organic cert
    r"\bnpop\b",                        # National Programme Organic Production
    r"\bnatural\b",
    r"\b100%\s*natural\b",
    r"\ball\s*natural\b",
    r"\bpure\b",
    r"\bshudh\b",                       # Pure in Hindi
    r"\bshuddh\b",

    # Diet claims
    r"\bvegan\b",
    r"\bvegetarian\b",
    r"\bno\s*onion\s*no\s*garlic\b",    # Common Indian Jain claim
    r"\bjain\b",
    r"\bgluten[\s-]?free\b",
    r"\bsugar[\s-]?free\b",
    r"\bno\s*added\s*sugar\b",
    r"\bdiabetic[\s-]?friendly\b",
    r"\blow\s*fat\b",
    r"\bfat[\s-]?free\b",
    r"\blow\s*calorie\b",
    r"\bzero\s*calorie\b",

    # Additive claims
    r"\bno\s*preservative\b",
    r"\bno\s*artificial\s*colou?r\b",
    r"\bno\s*artificial\s*flavou?r\b",
    r"\bno\s*msg\b",
    r"\bno\s*added\s*preservative\b",
    r"\bpreservative[\s-]?free\b",
    r"\bchemical[\s-]?free\b",
    r"\badditive[\s-]?free\b",
    r"\bno\s*maida\b",                  # India specific — no refined flour
    r"\bno\s*trans\s*fat\b",
    r"\bzero\s*trans\s*fat\b",

    # Health claims
    r"\bhigh\s*protein\b",
    r"\bprotein\s*rich\b",
    r"\bhigh\s*fibre\b",
    r"\bfibre\s*rich\b",
    r"\bmultigrain\b",
    r"\bwhole\s*grain\b",
    r"\bwhole\s*wheat\b",
    r"\bnut[\s-]?free\b",

    # Indian traditional claims
    r"\bayurvedic\b",
    r"\bherbal\b",
    r"\btraditional\b",
    r"\bdesi\b",                        # Local/traditional in Hindi
    r"\bghar\s*jaisa\b",                # Homemade like in Hindi
    r"\bpradakshina\b",
    r"\bkadha\b",                       # Traditional herbal drink

    # Religious / ethical
    r"\bhalal\b",
    r"\bkosher\b",
    r"\bnon[\s-]?gmo\b",
    r"\bfair[\s-]?trade\b",
    r"\bno\s*preservatives?\b",
    r"\bwithout\s*preservatives?\b",
    r"\bpreservative\s*free\b",
]

# ── Indian Tagline Claims ──────────────────────────────
# Common marketing language in Indian food ads
TAGLINE_CLAIMS = [
    # Health / nature language
    r"\bnatural\b",
    r"\bhealthy\b",
    r"\bpure\b",
    r"\bshudh\b",
    r"\bclean\b",
    r"\bgoodness\b",
    r"\bnourishing\b",
    r"\bnutritious\b",
    r"\bwholesome\b",
    r"\bwellness\b",

    # Indian specific marketing
    r"\bghar\s*ka\s*khana\b",           # Home cooked food
    r"\bmaata\s*ke\s*haath\b",          # Mother's hands (homemade feel)
    r"\bpyaar\s*se\s*banaya\b",         # Made with love
    r"\bdadi\s*ki\s*recipe\b",          # Grandmother's recipe
    r"\bnani\s*ki\s*recipe\b",
    r"\btraditional\s*recipe\b",
    r"\bauthentic\b",
    r"\bpradampurana\b",
    r"\bpurana\s*zaika\b",              # Old taste
    r"\bdesh\s*ka\s*swad\b",            # Taste of the nation

    # Farm / nature language
    r"\bfarm[\s-]?fresh\b",
    r"\bstraight\s*from\s*farm\b",
    r"\bfresh\s*from\s*nature\b",
    r"\bnature['\u2019]?s\b",
    r"\bgreen\b",
    r"\beco[\s-]?friendly\b",
    r"\bsustainable\b",

    # Ingredient claims
    r"\breal\s*ingredients\b",
    r"\breal\s*spices\b",
    r"\breal\s*fruit\b",
    r"\breal\s*vegetables\b",
    r"\bno\s*nasties\b",
    r"\bfree\s*from\b",
    r"\bguilt[\s-]?free\b",
    r"\bclean\s*eating\b",
    r"\bsuperfood\b",
    r"\bpower\s*food\b",
    r"\benergy\s*food\b",
    r"\bimmunity\b",                    # Very common post-COVID India
    r"\bimmunity\s*boost\b",
    r"\brich\s*in\s*antioxidant\b",
    r"\brich\s*in\s*vitamin\b",
    r"\brich\s*in\s*protein\b",
    r"\brich\s*in\s*fibre\b",
    r"\bplant[\s-]?based\b",
    r"\bplant[\s-]?powered\b",
    r"\bartisanal\b",
    r"\bhandcrafted\b",
    r"\bsmall\s*batch\b",
    r"\bnatural\s*ingredients?\b",
    r"\btaste\s*bhi\s*health\s*bhi\b",
]

# ── Negation detection ─────────────────────────────────
NEGATIONS = [
    r"\bnot\b",
    r"\bnever\b",
    r"\bwithout\b",
    r"\bunnatural\b",
    r"\bnahi\b",                        # No in Hindi
]


def _has_negation_before(sentence, match_start, window=30):
    preceding = sentence[max(0, match_start - window): match_start]
    return any(re.search(n, preceding) for n in NEGATIONS)


def detect_claims(labels_text, tagline_text):
    """
    Detects green claims from Indian product labels + taglines.

    INPUT:
        labels_text  : "organic, no preservatives, vegan"
        tagline_text : "shudh aur natural, ghar jaisa swad"

    OUTPUT:
        dict with all claim info + numeric claim_score
    """
    labels_text  = str(labels_text).lower()  if labels_text  else ""
    tagline_text = str(tagline_text).lower() if tagline_text else ""

    label_claims   = []
    tagline_claims = []

    for p in LABEL_CLAIMS:
        m = re.search(p, labels_text)
        if m:
            label_claims.append(m.group().strip())

    for p in TAGLINE_CLAIMS:
        m = re.search(p, tagline_text)
        if m and not _has_negation_before(tagline_text, m.start()):
            tagline_claims.append(m.group().strip())

    all_claims  = list(set(label_claims + tagline_claims))
    claim_score = min(len(label_claims) * 15, 60) + min(len(tagline_claims) * 8, 40)

    return {
        "label_claims":   label_claims,
        "tagline_claims": tagline_claims,
        "all_claims":     all_claims,
        "total_claims":   len(all_claims),
        "claim_score":    min(claim_score, 100),
        "has_claims":     len(all_claims) > 0,
    }


if __name__ == "__main__":
    result = detect_claims(
        labels_text  = "organic, no preservatives, no msg, vegetarian",
        tagline_text = "shudh aur natural, ghar jaisa swad, immunity boost karo"
    )
    print("Label Claims  :", result["label_claims"])
    print("Tagline Claims:", result["tagline_claims"])
    print("Claim Score   :", result["claim_score"], "/ 100")