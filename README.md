# 🌿 GreenWatch India

### Detecting Greenwashing in Food Products using NLP & Machine Learning 🇮🇳

---

## 🚀 Overview

**GreenWatch India** is an AI-powered web application that analyzes packaged food products and detects **misleading health and “natural” claims (greenwashing)**.

It uses:

* 🧠 Machine Learning (ingredient risk classification)
* 🔍 NLP (claim detection from labels & taglines)
* 🇮🇳 FSSAI-based rules for Indian market relevance

👉 The goal is to help consumers **understand what’s really inside their food**.

---

## 🎯 Problem Statement

Many food products claim:

* “100% Natural”
* “No Preservatives”
* “Healthy”

…but actually contain:

* Artificial additives
* Harmful preservatives
* Synthetic colors & flavor enhancers

➡️ This misleading marketing is called **Greenwashing**.

---

## 💡 Solution

GreenWatch India:

1. Extracts product claims (labels + tagline)
2. Analyzes ingredients using ML + rule-based system
3. Calculates a **Greenwash Score (0–100)**
4. Provides a clear verdict:

| Score Range | Verdict                |
| ----------- | ---------------------- |
| 0–25        | ✅ Clean / Honest       |
| 26–50       | 🟡 Mildly Suspicious   |
| 51–75       | ⚠️ Likely Greenwashing |
| 76–100      | 🚨 Strong Greenwashing |

---

## 🧠 How It Works

### 🔹 1. Claim Detection (NLP)

* Detects marketing claims like:

  * “natural”
  * “organic”
  * “no preservatives”
* Uses regex-based NLP tuned for Indian labels

---

### 🔹 2. Ingredient Risk Analysis (ML)

* Uses a trained model (TF-IDF + classifier)
* Classifies each ingredient into:

  * 🟢 Safe
  * 🟡 Moderate
  * 🟠 Moderately High
  * 🔴 Hazardous

---

### 🔹 3. Greenwash Scoring

Combines:

* Ingredient harm
* Claim intensity
* Claim vs reality mismatch
* Additives count
* Hazardous ingredients

---

### 🔹 4. Output

* Ingredient breakdown
* Risk levels
* Final score
* Verdict

---

## 🛠 Tech Stack

* **Frontend:** Streamlit
* **Backend:** Python
* **ML:** Scikit-learn (TF-IDF + Classifier)
* **Data:** OpenFoodFacts + FSSAI Guidelines
* **Visualization:** Plotly

---

## 📂 Project Structure

```
greenwatch-india/
│
├── app.py                  # Streamlit UI
├── analyze_product.py      # Core scoring logic
├── product_risk.py         # ML-based ingredient analysis
├── greenwash_detector.py   # Claim detection (NLP)
│
├── extract_ingredients.py  # Data extraction
├── clean_ingredients.py    # Data cleaning
├── autolabel.py            # Auto-labeling
├── train_model.py          # Model training
│
├── harm_model.pkl
├── vectorizer.pkl
├── label_encoder.pkl
│
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation & Setup

### 🔹 1. Clone Repository

```bash
git clone https://github.com/your-username/greenwatch-india.git
cd greenwatch-india
```

---

### 🔹 2. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 🔹 3. Run the App

```bash
streamlit run app.py
```

---

## 🔄 Model Training Pipeline (Optional)

Run only if you want to retrain:

```bash
python extract_ingredients.py
python clean_ingredients.py
python autolabel.py
python train_model.py
```

---

## 🧪 Example Use Case

### Input:

* Ingredients:
  `maida, sugar, palm oil, MSG, tartrazine, sodium benzoate`
* Claims:
  `no preservatives, natural, healthy`

### Output:

```
Greenwash Score: 72 / 100  
Verdict: ⚠️ Likely Greenwashing
```

---

## 🌐 Deployment

Deployed using **Render** with Streamlit.

---

## 🎓 Academic Context

* 🎓 B.Tech Minor Project
* 🏫 KIIT University
* 📅 Year: 2026

---

## 🚀 Future Improvements

* 📱 Barcode scanning (real-time product detection)
* 🌍 Mobile app version
* 🤖 Advanced NLP using transformers (BERT)
* 🧾 Product comparison feature
* 🛒 Integration with e-commerce platforms

---

## 👨‍💻 Author

**Rishabh Patel**
B.Tech Student | Aspiring Builder 🚀

---

## ⭐ Support

If you found this useful:
👉 Star the repo
👉 Share with others

---

## ⚠️ Disclaimer

This tool provides **informational insights only** and does not replace professional dietary advice.
