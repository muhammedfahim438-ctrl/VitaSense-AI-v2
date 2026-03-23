"""
VitaSense AI - train_model.py
Trains a Voting Ensemble (Random Forest + Gradient Boosting) on the
PIMA Indians Diabetes Dataset (5000 records) with 16 features
(8 original + 8 engineered). Saves model + scaler + imputer as .pkl files.
Run once: python train_model.py
"""

import os
import sys
import numpy as np
import pandas as pd
import pickle
import warnings
warnings.filterwarnings("ignore")

from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.metrics import (
    accuracy_score, roc_auc_score, classification_report,
    confusion_matrix
)

# ─── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODELS_DIR, exist_ok=True)

MODEL_PATH   = os.path.join(MODELS_DIR, "vitasense_model.pkl")
SCALER_PATH  = os.path.join(MODELS_DIR, "vitasense_scaler.pkl")
IMPUTER_PATH = os.path.join(MODELS_DIR, "vitasense_imputer.pkl")
MEDIANS_PATH = os.path.join(MODELS_DIR, "vitasense_medians.pkl")

# ─── 1. Generate synthetic dataset (PIMA-based, 5000 records) ─────────────────
def generate_dataset(n=5000, random_state=42):
    """
    Generates a realistic synthetic dataset based on PIMA Indians statistics.
    Optional fields (pregnancies, skin_thickness, insulin) include ~15% missing
    values so the model learns to handle them via imputation.
    """
    rng = np.random.RandomState(random_state)

    # Core features — drawn from distributions matching PIMA statistics
    glucose         = rng.normal(120.9, 31.97, n).clip(0, 300)
    blood_pressure  = rng.normal(69.1, 19.36, n).clip(0, 130)
    bmi             = rng.normal(31.99, 7.88, n).clip(10, 70)
    dpf             = rng.gamma(2.0, 0.25, n).clip(0.08, 2.5)
    age             = rng.normal(33.24, 11.76, n).clip(18, 85)

    # Optional features — with realistic missing-value rate
    pregnancies     = rng.randint(0, 17, n).astype(float)
    skin_thickness  = rng.normal(20.5, 15.95, n).clip(0, 100).astype(float)
    insulin         = rng.lognormal(4.0, 0.9, n).clip(0, 850).astype(float)

    # Inject ~15 % missingness into optional fields
    for arr in [pregnancies, skin_thickness, insulin]:
        mask = rng.rand(n) < 0.15
        arr[mask] = np.nan

    # ── Engineered features (8) ──────────────────────────────────────────────
    # Use fillna median for engineering (training-time imputation)
    preg_fill  = np.where(np.isnan(pregnancies),    np.nanmedian(pregnancies),    pregnancies)
    skin_fill  = np.where(np.isnan(skin_thickness), np.nanmedian(skin_thickness), skin_thickness)
    ins_fill   = np.where(np.isnan(insulin),        np.nanmedian(insulin),        insulin)

    glucose_bmi_ratio    = glucose / (bmi + 1e-6)
    insulin_resistance   = (ins_fill * glucose) / 405.0          # HOMA-IR proxy
    age_bmi_interaction  = age * bmi / 100.0
    glucose_age_ratio    = glucose / (age + 1e-6)
    bmi_category         = pd.cut(bmi,
                                  bins=[-np.inf, 18.5, 25, 30, np.inf],
                                  labels=[0, 1, 2, 3]).astype(float)
    glucose_category     = pd.cut(glucose,
                                  bins=[-np.inf, 100, 125, np.inf],
                                  labels=[0, 1, 2]).astype(float)
    bp_category          = pd.cut(blood_pressure,
                                  bins=[-np.inf, 80, 90, np.inf],
                                  labels=[0, 1, 2]).astype(float)
    age_category         = pd.cut(age,
                                  bins=[-np.inf, 30, 45, 60, np.inf],
                                  labels=[0, 1, 2, 3]).astype(float)

    # ── Realistic outcome (Outcome) ──────────────────────────────────────────
    # Score-based probability → threshold at ~35 % prevalence
    score = (
        (glucose - 100) * 0.03 +
        (bmi     -  25) * 0.04 +
        (age     -  30) * 0.015 +
        dpf             * 0.5  +
        insulin_resistance * 0.02
    )
    prob    = 1 / (1 + np.exp(-score))           # logistic
    outcome = (rng.rand(n) < prob).astype(int)

    df = pd.DataFrame({
        # ── Original 8 ──
        "pregnancies":    pregnancies,
        "glucose":        glucose,
        "blood_pressure": blood_pressure,
        "skin_thickness": skin_thickness,
        "insulin":        insulin,
        "bmi":            bmi,
        "dpf":            dpf,
        "age":            age,
        # ── Engineered 8 ──
        "glucose_bmi_ratio":   glucose_bmi_ratio,
        "insulin_resistance":  insulin_resistance,
        "age_bmi_interaction": age_bmi_interaction,
        "glucose_age_ratio":   glucose_age_ratio,
        "bmi_category":        bmi_category,
        "glucose_category":    glucose_category,
        "bp_category":         bp_category,
        "age_category":        age_category,
        # ── Target ──
        "outcome":        outcome,
    })
    return df

# ─── 2. Feature list ──────────────────────────────────────────────────────────
FEATURE_COLS = [
    # Original
    "pregnancies", "glucose", "blood_pressure", "skin_thickness",
    "insulin", "bmi", "dpf", "age",
    # Engineered
    "glucose_bmi_ratio", "insulin_resistance", "age_bmi_interaction",
    "glucose_age_ratio", "bmi_category", "glucose_category",
    "bp_category", "age_category",
]

# ─── 3. Train ─────────────────────────────────────────────────────────────────
def train():
    print("=" * 60)
    print("  VitaSense AI — Model Training")
    print("=" * 60)

    # 3a. Dataset
    print("\n[1/5] Generating dataset (5000 records, 16 features)...")
    df = generate_dataset(5000)
    print(f"      Diabetic  : {df['outcome'].sum()} ({df['outcome'].mean()*100:.1f}%)")
    print(f"      Non-diabetic: {(1-df['outcome']).sum()} ({(1-df['outcome'].mean())*100:.1f}%)")

    X = df[FEATURE_COLS]
    y = df["outcome"]

    # 3b. Save column medians for optional-field imputation at inference time
    medians = {
        "pregnancies":    float(np.nanmedian(df["pregnancies"])),
        "skin_thickness": float(np.nanmedian(df["skin_thickness"])),
        "insulin":        float(np.nanmedian(df["insulin"])),
    }
    print(f"\n[2/5] Optional-field medians for inference imputation:")
    for k, v in medians.items():
        print(f"      {k}: {v:.2f}")

    # 3c. Impute → Scale
    print("\n[3/5] Imputing missing values + scaling features...")
    imputer = SimpleImputer(strategy="median")
    X_imp   = imputer.fit_transform(X)

    scaler  = StandardScaler()
    X_scaled = scaler.fit_transform(X_imp)

    # 3d. Split
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42, stratify=y
    )

    # 3e. Build Voting Ensemble
    print("\n[4/5] Training Voting Ensemble (RF + GB)...")
    rf = RandomForestClassifier(
        n_estimators=300,
        max_depth=10,
        min_samples_split=4,
        min_samples_leaf=2,
        max_features="sqrt",
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    gb = GradientBoostingClassifier(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=5,
        min_samples_split=4,
        min_samples_leaf=2,
        subsample=0.8,
        random_state=42,
    )
    ensemble = VotingClassifier(
        estimators=[("rf", rf), ("gb", gb)],
        voting="soft",          # use predicted probabilities
        weights=[1, 1],
    )
    ensemble.fit(X_train, y_train)

    # 3f. Evaluate
    print("\n[5/5] Evaluating model...")
    y_pred      = ensemble.predict(X_test)
    y_prob      = ensemble.predict_proba(X_test)[:, 1]
    accuracy    = accuracy_score(y_test, y_pred)
    roc_auc     = roc_auc_score(y_test, y_prob)

    # 5-fold cross-validation accuracy
    cv          = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores   = cross_val_score(ensemble, X_scaled, y, cv=cv, scoring="accuracy", n_jobs=-1)

    print(f"\n  {'─'*40}")
    print(f"  Accuracy      : {accuracy*100:.2f}%")
    print(f"  ROC-AUC       : {roc_auc:.4f}")
    print(f"  CV Accuracy   : {cv_scores.mean()*100:.2f}% ± {cv_scores.std()*100:.2f}%")
    print(f"  {'─'*40}")
    print("\n  Classification Report:")
    print(classification_report(y_test, y_pred,
                                 target_names=["Non-Diabetic", "Diabetic"]))
    cm = confusion_matrix(y_test, y_pred)
    print("  Confusion Matrix:")
    print(f"    TN={cm[0,0]}  FP={cm[0,1]}")
    print(f"    FN={cm[1,0]}  TP={cm[1,1]}")

    # 3g. Save artifacts
    print("\n  Saving model artifacts...")
    with open(MODEL_PATH,   "wb") as f: pickle.dump(ensemble, f)
    with open(SCALER_PATH,  "wb") as f: pickle.dump(scaler,   f)
    with open(IMPUTER_PATH, "wb") as f: pickle.dump(imputer,  f)
    with open(MEDIANS_PATH, "wb") as f: pickle.dump(medians,  f)

    print(f"  ✓ Model   → {MODEL_PATH}")
    print(f"  ✓ Scaler  → {SCALER_PATH}")
    print(f"  ✓ Imputer → {IMPUTER_PATH}")
    print(f"  ✓ Medians → {MEDIANS_PATH}")
    print("\n  Training complete! Run python app.py to start the server.")
    print("=" * 60)

    return {
        "accuracy": round(accuracy * 100, 2),
        "roc_auc":  round(roc_auc, 4),
        "cv_mean":  round(cv_scores.mean() * 100, 2),
    }


if __name__ == "__main__":
    train()