import pandas as pd
import pickle
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, ConfusionMatrixDisplay

print("=" * 55)
print("  STEP 4: Training Harm Classification Model")
print("=" * 55)

# ── Load Data ──────────────────────────────────────────
df = pd.read_csv("labeled_ingredients.csv")
df = df.dropna(subset=["ingredient", "harm_level"])
df["ingredient"] = df["ingredient"].astype(str)

print(f"Total samples: {len(df)}")
print("\nLabel distribution:")
print(df["harm_level"].value_counts())

# ── Encode Labels ──────────────────────────────────────
le = LabelEncoder()
df["label"] = le.fit_transform(df["harm_level"])
print(f"\nClasses: {list(le.classes_)}")

# ── Vectorize ──────────────────────────────────────────
print("\nVectorizing...")
vectorizer = TfidfVectorizer(
    ngram_range  = (1, 2),
    min_df       = 2,
    max_features = 10000,
    sublinear_tf = True,
)
X = vectorizer.fit_transform(df["ingredient"])
y = df["label"]

# ── Split ──────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"Train: {X_train.shape[0]} | Test: {X_test.shape[0]}")

# ── Train ──────────────────────────────────────────────
print("\nTraining Random Forest...")
model = RandomForestClassifier(
    n_estimators = 100,
    class_weight = "balanced",
    random_state = 42,
    n_jobs       = -1,
)
model.fit(X_train, y_train)

# ── Evaluate ───────────────────────────────────────────
y_pred = model.predict(X_test)
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=le.classes_))

# ── Cross Validation ───────────────────────────────────
print("Running 5-fold cross validation...")
cv_scores = cross_val_score(model, X, y, cv=5, scoring="f1_macro", n_jobs=-1)
print(f"CV F1: {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")

# ── Confusion Matrix ───────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 6))
ConfusionMatrixDisplay.from_predictions(
    y_test, y_pred,
    display_labels = le.classes_,
    ax             = ax,
    cmap           = "Blues"
)
plt.title("Harm Level Classification — Confusion Matrix")
plt.tight_layout()
plt.savefig("confusion_matrix.png", dpi=150)
plt.close()
print("✅ Saved confusion_matrix.png")

# ── Save Model Files ───────────────────────────────────
pickle.dump(model,      open("harm_model.pkl",    "wb"))
pickle.dump(vectorizer, open("vectorizer.pkl",     "wb"))
pickle.dump(le,         open("label_encoder.pkl",  "wb"))

print("✅ Saved harm_model.pkl")
print("✅ Saved vectorizer.pkl")
print("✅ Saved label_encoder.pkl")
print("\n✅ Training complete!")