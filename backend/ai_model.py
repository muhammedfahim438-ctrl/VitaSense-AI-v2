"""
VitaSense AI - ai_model.py
Loads trained model artifacts and runs predictions.
Handles optional fields (pregnancies, skin_thickness, insulin) via median imputation.
Returns full result with accurate percentage breakdowns for every factor.
"""

import os
import sys
import pickle
import numpy as np
import warnings
warnings.filterwarnings("ignore")

# ─── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")

MODEL_PATH   = os.path.join(MODELS_DIR, "vitasense_model.pkl")
SCALER_PATH  = os.path.join(MODELS_DIR, "vitasense_scaler.pkl")
IMPUTER_PATH = os.path.join(MODELS_DIR, "vitasense_imputer.pkl")
MEDIANS_PATH = os.path.join(MODELS_DIR, "vitasense_medians.pkl")

# ─── Load artifacts once at import time ──────────────────────────────────────
def _load(path):
    with open(path, "rb") as f:
        return pickle.load(f)

try:
    MODEL   = _load(MODEL_PATH)
    SCALER  = _load(SCALER_PATH)
    IMPUTER = _load(IMPUTER_PATH)
    MEDIANS = _load(MEDIANS_PATH)
    print("✓ Model artifacts loaded successfully.")
except FileNotFoundError as e:
    raise RuntimeError(
        f"Model file not found: {e}\n"
        "Please run: python train_model.py  before starting the server."
    )

# ─── Feature column order (must match train_model.py) ─────────────────────────
FEATURE_COLS = [
    "pregnancies", "glucose", "blood_pressure", "skin_thickness",
    "insulin", "bmi", "dpf", "age",
    "glucose_bmi_ratio", "insulin_resistance", "age_bmi_interaction",
    "glucose_age_ratio", "bmi_category", "glucose_category",
    "bp_category", "age_category",
]

# ─── Reference ranges for % contribution scoring ─────────────────────────────
GLUCOSE_NORMAL  = 100.0   # mg/dL
GLUCOSE_HIGH    = 200.0
BP_NORMAL       = 80.0    # mmHg
BP_HIGH         = 130.0
BMI_NORMAL      = 22.0
BMI_HIGH        = 40.0
AGE_LOW         = 18.0
AGE_HIGH        = 70.0
DPF_LOW         = 0.08
DPF_HIGH        = 2.5


# ─── Helper: clamp to 0–100 ───────────────────────────────────────────────────
def _pct(val, lo, hi):
    return round(float(np.clip((val - lo) / (hi - lo) * 100, 0, 100)), 1)


# ─── HbA1c estimate from glucose (mg/dL) ─────────────────────────────────────
def estimate_hba1c(glucose: float) -> float:
    """
    Nathan et al. formula:  HbA1c % ≈ (glucose + 46.7) / 28.7
    """
    return round((glucose + 46.7) / 28.7, 1)


# ─── Classify helpers ─────────────────────────────────────────────────────────
def classify_bmi(bmi: float) -> str:
    if bmi < 18.5: return "Underweight"
    if bmi < 25.0: return "Normal"
    if bmi < 30.0: return "Overweight"
    return "Obese"

def classify_glucose(glucose: float) -> str:
    if glucose < 100: return "Normal"
    if glucose < 126: return "Prediabetes"
    return "High"

def classify_bp(bp: float) -> str:
    if bp < 80:  return "Normal"
    if bp < 90:  return "Elevated"
    return "High"

def classify_risk_level(risk_pct: float) -> str:
    if risk_pct < 35: return "Low"
    if risk_pct < 65: return "Medium"
    return "High"

def classify_risk_category(risk_pct: float) -> str:
    if risk_pct < 35: return "Normal"
    if risk_pct < 65: return "Prediabetes"
    return "Diabetes"

def classify_urgency(risk_pct: float, glucose: float) -> str:
    if risk_pct >= 65 or glucose >= 200:
        return "See Doctor Now"
    if risk_pct >= 35 or glucose >= 126:
        return "See Doctor Soon"
    return "Routine Checkup"


# ─── Health score (0–100, higher = healthier) ─────────────────────────────────
def compute_health_score(glucose, bmi, bp, age, dpf, risk_pct) -> float:
    """
    Weighted penalty system:
      glucose  30 % weight
      bmi      25 % weight
      bp       15 % weight
      dpf      15 % weight
      age      15 % weight
    Final score = 100 - weighted_risk
    """
    g_score  = _pct(glucose, GLUCOSE_NORMAL, GLUCOSE_HIGH)
    b_score  = _pct(bmi,     BMI_NORMAL,     BMI_HIGH)
    bp_score = _pct(bp,      BP_NORMAL,      BP_HIGH)
    dpf_score = _pct(dpf,    DPF_LOW,        DPF_HIGH)
    a_score  = _pct(age,     AGE_LOW,        AGE_HIGH)

    weighted = (
        g_score  * 0.30 +
        b_score  * 0.25 +
        bp_score * 0.15 +
        dpf_score* 0.15 +
        a_score  * 0.15
    )
    health = round(100 - weighted, 1)
    return max(0.0, min(100.0, health))


# ─── Recommendation message based on risk ────────────────────────────────────
def get_recommendation_message(risk_pct: float, risk_level: str) -> str:
    if risk_level == "High":
        return (
            "Your results show a HIGH diabetes risk. "
            "It is strongly advised to consult a doctor immediately. "
            "Follow the personalised diet and exercise plan below to start "
            "reducing your risk right away. Early action makes a big difference."
        )
    if risk_level == "Medium":
        return (
            "You are in the PREDIABETES range. The good news is that with the "
            "right lifestyle changes now, you can normalise your blood sugar. "
            "Follow the diet and exercise plan below consistently and recheck "
            "your levels in 3 months."
        )
    return (
        "You are doing well! Your diabetes risk is LOW. "
        "Keep up your healthy habits. The tips below will help you "
        "maintain your current health and stay diabetes-free long term."
    )


# ─── Main prediction function ─────────────────────────────────────────────────
def predict(input_data: dict) -> dict:
    """
    Parameters
    ----------
    input_data : dict with keys:
        Required : glucose, blood_pressure, bmi, dpf, age
        Optional : pregnancies, skin_thickness, insulin  (None / missing = use median)

    Returns
    -------
    dict with full prediction result including all % breakdowns
    """

    # 1. Fill optional fields with training medians if not provided
    pregnancies    = input_data.get("pregnancies")
    skin_thickness = input_data.get("skin_thickness")
    insulin        = input_data.get("insulin")

    if pregnancies    is None or pregnancies    == "":
        pregnancies    = MEDIANS["pregnancies"]
    if skin_thickness is None or skin_thickness == "":
        skin_thickness = MEDIANS["skin_thickness"]
    if insulin        is None or insulin        == "":
        insulin        = MEDIANS["insulin"]

    # Convert all to float
    pregnancies    = float(pregnancies)
    skin_thickness = float(skin_thickness)
    insulin        = float(insulin)
    glucose        = float(input_data["glucose"])
    blood_pressure = float(input_data["blood_pressure"])
    bmi            = float(input_data["bmi"])
    dpf            = float(input_data["dpf"])
    age            = float(input_data["age"])

    # 2. Engineered features
    glucose_bmi_ratio    = glucose / (bmi + 1e-6)
    insulin_resistance   = (insulin * glucose) / 405.0
    age_bmi_interaction  = age * bmi / 100.0
    glucose_age_ratio    = glucose / (age + 1e-6)

    def _bin(val, bins, labels):
        for i, (lo, hi) in enumerate(zip(bins[:-1], bins[1:])):
            if lo <= val < hi:
                return float(labels[i])
        return float(labels[-1])

    bmi_cat      = _bin(bmi,            [-1e9,18.5,25,30,1e9],  [0,1,2,3])
    glucose_cat  = _bin(glucose,        [-1e9,100,126,1e9],     [0,1,2])
    bp_cat       = _bin(blood_pressure, [-1e9,80,90,1e9],       [0,1,2])
    age_cat      = _bin(age,            [-1e9,30,45,60,1e9],    [0,1,2,3])

    # 3. Assemble feature vector (same order as FEATURE_COLS)
    features = np.array([[
        pregnancies, glucose, blood_pressure, skin_thickness,
        insulin, bmi, dpf, age,
        glucose_bmi_ratio, insulin_resistance, age_bmi_interaction,
        glucose_age_ratio, bmi_cat, glucose_cat, bp_cat, age_cat,
    ]])

    # 4. Impute → Scale → Predict
    features_imp    = IMPUTER.transform(features)
    features_scaled = SCALER.transform(features_imp)

    prediction_label = MODEL.predict(features_scaled)[0]
    probabilities    = MODEL.predict_proba(features_scaled)[0]
    risk_probability = float(probabilities[1])          # probability of Diabetic class
    risk_percentage  = round(risk_probability * 100, 1) # e.g. 73.4

    # 5. Derived classifications
    prediction_text  = "Diabetic" if prediction_label == 1 else "Not Diabetic"
    risk_level       = classify_risk_level(risk_percentage)
    risk_category    = classify_risk_category(risk_percentage)
    hba1c            = estimate_hba1c(glucose)
    bmi_status       = classify_bmi(bmi)
    glucose_category = classify_glucose(glucose)
    bp_status        = classify_bp(blood_pressure)
    urgency          = classify_urgency(risk_percentage, glucose)
    health_score     = compute_health_score(glucose, bmi, blood_pressure, age, dpf, risk_percentage)
    rec_message      = get_recommendation_message(risk_percentage, risk_level)

    # 6. Individual % contributions
    glucose_contribution = _pct(glucose,        GLUCOSE_NORMAL, GLUCOSE_HIGH)
    bmi_contribution     = _pct(bmi,            BMI_NORMAL,     BMI_HIGH)
    age_contribution     = _pct(age,            AGE_LOW,        AGE_HIGH)
    dpf_contribution     = _pct(dpf,            DPF_LOW,        DPF_HIGH)
    bp_contribution      = _pct(blood_pressure, BP_NORMAL,      BP_HIGH)
    age_risk_factor      = age_contribution

    # 7. Build full result dict
    result = {
        # ── Inputs (after imputation) ──
        "inputs": {
            "pregnancies":    round(pregnancies, 1),
            "glucose":        round(glucose, 1),
            "blood_pressure": round(blood_pressure, 1),
            "skin_thickness": round(skin_thickness, 1),
            "insulin":        round(insulin, 1),
            "bmi":            round(bmi, 1),
            "dpf":            round(dpf, 3),
            "age":            round(age, 0),
        },

        # ── Core result ──
        "prediction":       prediction_text,
        "risk_percentage":  risk_percentage,
        "risk_level":       risk_level,
        "risk_category":    risk_category,
        "urgency_level":    urgency,
        "recommendation_message": rec_message,

        # ── Health metrics ──
        "hba1c_estimate":      hba1c,
        "bmi_status":          bmi_status,
        "glucose_category":    glucose_category,
        "bp_status":           bp_status,
        "age_risk_factor":     age_risk_factor,
        "insulin_resistance":  round(insulin_resistance, 2),
        "health_score":        health_score,

        # ── Accurate % breakdown ──
        "percentage_breakdown": {
            "glucose_contribution": glucose_contribution,
            "bmi_contribution":     bmi_contribution,
            "age_contribution":     age_contribution,
            "dpf_contribution":     dpf_contribution,
            "bp_contribution":      bp_contribution,
        },

        # ── Flat copies for DB save ──
        "glucose_contribution": glucose_contribution,
        "bmi_contribution":     bmi_contribution,
        "age_contribution":     age_contribution,
        "dpf_contribution":     dpf_contribution,
        "bp_contribution":      bp_contribution,
    }

    return result


# ─── Quick self-test ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Test 1 — High risk (all required + optional filled)
    test_high = {
        "glucose": 180, "blood_pressure": 95, "bmi": 38.5,
        "dpf": 1.2, "age": 52,
        "pregnancies": 4, "skin_thickness": 35, "insulin": 200,
    }
    # Test 2 — Low risk (optional fields left blank)
    test_low = {
        "glucose": 88, "blood_pressure": 72, "bmi": 22.0,
        "dpf": 0.2, "age": 25,
    }
    for label, data in [("HIGH RISK", test_high), ("LOW RISK", test_low)]:
        r = predict(data)
        print(f"\n{'─'*50}")
        print(f"  Test: {label}")
        print(f"  Result       : {r['prediction']}")
        print(f"  Risk %       : {r['risk_percentage']}%")
        print(f"  Risk Level   : {r['risk_level']}")
        print(f"  Health Score : {r['health_score']}/100")
        print(f"  HbA1c Est.   : {r['hba1c_estimate']}%")
        print(f"  Urgency      : {r['urgency_level']}")
        print(f"  Breakdown    : {r['percentage_breakdown']}")
        print(f"  Message      : {r['recommendation_message'][:80]}...")