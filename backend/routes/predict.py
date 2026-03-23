"""
VitaSense AI - routes/predict.py
Flask route for POST /predict
Receives form data, runs AI prediction, gets recommendations, saves to DB.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Blueprint, request, jsonify
from ai_model import predict
from recommendation import get_recommendations
from models import save_prediction

predict_bp = Blueprint("predict", __name__)


# ─── Validation helpers ───────────────────────────────────────────────────────

def _parse_float(value, field_name, required=True):
    """
    Parses a form value to float.
    Returns None for optional blank fields.
    Raises ValueError for invalid required fields.
    """
    if value is None or str(value).strip() == "":
        if required:
            raise ValueError(f"'{field_name}' is required.")
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        raise ValueError(f"'{field_name}' must be a valid number.")


def validate_inputs(data: dict) -> dict:
    """
    Validates and parses all input fields.
    Required  : glucose, blood_pressure, bmi, dpf, age
    Optional  : pregnancies, skin_thickness, insulin
    Returns   : cleaned dict ready for ai_model.predict()
    """
    errors = []
    parsed = {}

    # ── Required fields ──────────────────────────────────────────────────────
    required_fields = {
        "glucose":        (50,  400,  "Glucose must be between 50 and 400 mg/dL."),
        "blood_pressure": (40,  160,  "Blood pressure must be between 40 and 160 mmHg."),
        "bmi":            (10,  70,   "BMI must be between 10 and 70."),
        "dpf":            (0.05, 3.0, "Diabetes Pedigree Function must be between 0.05 and 3.0."),
        "age":            (1,   120,  "Age must be between 1 and 120."),
    }

    for field, (lo, hi, msg) in required_fields.items():
        try:
            val = _parse_float(data.get(field), field, required=True)
            if val < lo or val > hi:
                errors.append(msg)
            else:
                parsed[field] = val
        except ValueError as e:
            errors.append(str(e))

    # ── Optional fields ───────────────────────────────────────────────────────
    optional_fields = {
        "pregnancies":    (0,  20,   "Pregnancies must be between 0 and 20."),
        "skin_thickness": (0,  100,  "Skin thickness must be between 0 and 100 mm."),
        "insulin":        (0,  900,  "Insulin must be between 0 and 900 µU/mL."),
    }

    for field, (lo, hi, msg) in optional_fields.items():
        try:
            val = _parse_float(data.get(field), field, required=False)
            if val is not None:
                if val < lo or val > hi:
                    errors.append(msg)
                else:
                    parsed[field] = val
            else:
                parsed[field] = None   # will be imputed inside ai_model
        except ValueError as e:
            errors.append(str(e))

    if errors:
        raise ValueError(errors)

    return parsed


# ─── POST /predict ────────────────────────────────────────────────────────────

@predict_bp.route("/predict", methods=["POST"])
def run_prediction():
    """
    Accepts JSON or form-data with diabetes input fields.
    Returns a full prediction result with recommendations.
    """
    try:
        # Support both JSON and form-data
        if request.is_json:
            raw = request.get_json(force=True) or {}
        else:
            raw = request.form.to_dict()

        # ── Validate ─────────────────────────────────────────────────────────
        try:
            inputs = validate_inputs(raw)
        except ValueError as ve:
            errors = ve.args[0]
            return jsonify({
                "success": False,
                "errors":  errors if isinstance(errors, list) else [str(ve)],
            }), 400

        # ── Predict ───────────────────────────────────────────────────────────
        result = predict(inputs)

        # ── Recommendations ───────────────────────────────────────────────────
        recommendations = get_recommendations(
            risk_level = result["risk_level"],
            glucose    = result["inputs"]["glucose"],
            bmi        = result["inputs"]["bmi"],
            bmi_status = result["bmi_status"],
            age        = result["inputs"]["age"],
        )

        # ── Save to DB ────────────────────────────────────────────────────────
        db_record = {
            # inputs
            "glucose":          result["inputs"]["glucose"],
            "blood_pressure":   result["inputs"]["blood_pressure"],
            "bmi":              result["inputs"]["bmi"],
            "dpf":              result["inputs"]["dpf"],
            "age":              result["inputs"]["age"],
            "pregnancies":      result["inputs"]["pregnancies"],
            "skin_thickness":   result["inputs"]["skin_thickness"],
            "insulin":          result["inputs"]["insulin"],
            # core result
            "prediction":           result["prediction"],
            "risk_percentage":      result["risk_percentage"],
            "risk_level":           result["risk_level"],
            "risk_category":        result["risk_category"],
            # health metrics
            "hba1c_estimate":       result["hba1c_estimate"],
            "bmi_status":           result["bmi_status"],
            "glucose_category":     result["glucose_category"],
            "bp_status":            result["bp_status"],
            "age_risk_factor":      result["age_risk_factor"],
            "insulin_resistance":   result["insulin_resistance"],
            "health_score":         result["health_score"],
            # % breakdown
            "glucose_contribution": result["glucose_contribution"],
            "bmi_contribution":     result["bmi_contribution"],
            "age_contribution":     result["age_contribution"],
            "dpf_contribution":     result["dpf_contribution"],
            "bp_contribution":      result["bp_contribution"],
            # urgency and message
            "urgency_level":        result["urgency_level"],
            "recommendation_msg":   result["recommendation_message"],
        }
        record_id = save_prediction(db_record)

        # ── Build response ────────────────────────────────────────────────────
        response = {
            "success":    True,
            "record_id":  record_id,

            # ── Core prediction ──
            "prediction":      result["prediction"],
            "risk_percentage": result["risk_percentage"],
            "risk_level":      result["risk_level"],
            "risk_category":   result["risk_category"],
            "urgency_level":   result["urgency_level"],
            "recommendation_message": result["recommendation_message"],

            # ── Health metrics ──
            "health_metrics": {
                "hba1c_estimate":     result["hba1c_estimate"],
                "bmi_status":         result["bmi_status"],
                "glucose_category":   result["glucose_category"],
                "bp_status":          result["bp_status"],
                "age_risk_factor":    result["age_risk_factor"],
                "insulin_resistance": result["insulin_resistance"],
                "health_score":       result["health_score"],
            },

            # ── Accurate % breakdown ──
            "percentage_breakdown": result["percentage_breakdown"],

            # ── Inputs (with imputed values shown) ──
            "inputs_used": result["inputs"],

            # ── Recommendations ──
            "recommendations": {
                "diet":       recommendations["diet"],
                "exercise":   recommendations["exercise"],
                "lifestyle":  recommendations["lifestyle"],
                "monitoring": recommendations["monitoring"],
                "health_tips": recommendations["health_tips"],
            },
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "errors":  [f"Server error: {str(e)}"],
        }), 500


# ─── GET /predictions/history ─────────────────────────────────────────────────

@predict_bp.route("/predictions/history", methods=["GET"])
def prediction_history():
    """Returns the last 20 predictions for the dashboard."""
    try:
        from models import get_recent_predictions
        limit = int(request.args.get("limit", 20))
        records = get_recent_predictions(limit)
        return jsonify({"success": True, "records": records}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ─── GET /dashboard/stats ─────────────────────────────────────────────────────

@predict_bp.route("/dashboard/stats", methods=["GET"])
def dashboard_stats():
    """Returns aggregated stats for the Dashboard tab charts."""
    try:
        from models import get_dashboard_stats
        stats = get_dashboard_stats()
        return jsonify({"success": True, "stats": stats}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500