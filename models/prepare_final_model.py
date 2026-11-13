"""models/prepare_final_model.py — membuat final trained model untuk Sesi 4 dan Sesi 8.

Script ini menggantikan script fasilitator (bukan bagian sesi). Konfigurasinya dicocokkan dengan
angka di Buku Praktikum: holdout ROC-AUC 0,7887 · akurasi 0,7183 · F1 0,5786.

Jalankan sekali dari folder dashboard_course:  python models/prepare_final_model.py
Hasil: models/churn_model.joblib dan models/model_metadata.json
"""
import json
from pathlib import Path

import joblib
import pandas as pd
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "models"
SEED = 42

NUM = ["tenure_months", "monthly_charges", "total_charges", "num_complaints", "support_calls"]
CAT = ["region", "segment", "contract_type", "payment_method", "internet_service"]
FEATURES = NUM + CAT

df = pd.read_csv(ROOT / "data" / "customer_churn.csv")
X, y = df[FEATURES], df["churn"]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=SEED, stratify=y
)

# Preprocessing di dalam Pipeline: imputasi median + standarisasi (numerik), one-hot (kategorik)
preprocess = ColumnTransformer([
    ("num", Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ]), NUM),
    ("cat", OneHotEncoder(handle_unknown="ignore"), CAT),
])
model = Pipeline([
    ("preprocess", preprocess),
    ("clf", GradientBoostingClassifier(n_estimators=200, learning_rate=0.05, random_state=SEED)),
])
model.fit(X_train, y_train)

proba = model.predict_proba(X_test)[:, 1]
pred = (proba >= 0.5).astype(int)
metrics = {
    "roc_auc": round(roc_auc_score(y_test, proba), 4),
    "accuracy": round(accuracy_score(y_test, pred), 4),
    "f1": round(f1_score(y_test, pred), 4),
}

metadata = {
    "model_name": "Customer Churn Classifier",
    "model_version": "1.0.0",
    "algorithm": "GradientBoostingClassifier (scikit-learn Pipeline)",
    "sklearn_version": sklearn.__version__,
    "target": "churn",
    "numeric_features": NUM,
    "categorical_features": CAT,
    "feature_order": FEATURES,
    "categories": {c: sorted(df[c].dropna().unique().tolist()) for c in CAT},
    "numeric_ranges": {
        c: [float(df[c].min()), float(df[c].max())] for c in NUM
    },
    "decision_threshold": 0.5,
    "risk_bins": {"Rendah": [0.0, 0.3], "Sedang": [0.3, 0.6], "Tinggi": [0.6, 1.0]},
    "holdout_metrics": metrics,
}

OUT.mkdir(exist_ok=True)
joblib.dump(model, OUT / "churn_model.joblib")
(OUT / "model_metadata.json").write_text(
    json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8"
)
print("Model tersimpan :", OUT / "churn_model.joblib")
print("Metadata        :", OUT / "model_metadata.json")
print("Holdout metrics :", metrics)
