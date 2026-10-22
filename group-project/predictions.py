"""Load the group's deployment artifacts once; inference only."""
import json
from pathlib import Path

import joblib
import pandas as pd
from pharmacy_logic import dynamic_recommender_advanced

ROOT = Path(__file__).resolve().parent
MODEL_DIR = ROOT / "model"
REGRESSION = joblib.load(MODEL_DIR / "exam_score_regressor.joblib")
CLASSIFIER = joblib.load(MODEL_DIR / "fraud_logreg_pipeline.pkl")
BANK = joblib.load(MODEL_DIR / "bank_segmentation.joblib")
PHARMACY = json.loads((MODEL_DIR / "pharmacy_recommender.json").read_text(encoding="utf-8"))

SPECS = {
    "student-exam-score-regressor": {
        "title": "Exam score", "description": "Estimate a final exam score from a student profile.",
        "pipeline": REGRESSION,
        "defaults": {"study_hours_per_week": 15.0, "attendance_rate_pct": 85.0,
                     "previous_gpa": 3.0, "sleep_hours_per_night": 7.0,
                     "extracurricular_activities_count": 2, "stress_level_score": 4,
                     "tutoring_hours_per_week": 2.0, "internet_access_quality": "Good",
                     "study_group_participation": "Yes", "parental_education_level": "Secondary"},
    },
    "insurance-fraud-classifier": {
        "title": "Insurance claim", "description": "Classify a synthetic insurance claim using your saved logistic-regression pipeline.",
        "pipeline": CLASSIFIER,
        "defaults": {"claimant_age": 45, "policy_tenure_years": 3.5, "prior_claims_count": 2,
                     "days_to_report_claim": 12, "claim_amount_kes": 850000.0,
                     "claim_amount_to_policy_limit_ratio": 0.65, "customer_credit_score": 620.0,
                     "police_report_missing": 0, "credit_score_missing": 0,
                     "policy_type": "Comprehensive", "claim_type": "Accident",
                     "witnesses_present": "Yes", "agent_flagged_history": "Yes"},
    },
    "bank-account-segmenter": {
        "title": "Bank accounts", "description": "Assign a new account to one of the three trained segments.",
        "pipeline": BANK["pipeline"],
        "defaults": {"account_balance_kes": 3200000.0, "transactions_per_month": 7.0,
                     "years_as_customer": 10.0, "digital_banking_usage_score": 55.0},
    },
    "pharmacy-recommender": {
        "title": "Pharmacy basket", "description": "Explore products bought together in the synthetic receipt data.",
        "defaults": {"cart": ["Baby Lotion", "Aloe Vera Gel"], "top_n": 3},
    },
}


def input_schema(key):
    spec = SPECS[key]
    if key == "pharmacy-recommender":
        return []
    pipe = spec["pipeline"]
    names = list(pipe.feature_names_in_)
    categories = {}
    pre = pipe.named_steps.get("preprocessor")
    if pre is not None:
        for _, transformer, columns in pre.transformers_:
            if hasattr(transformer, "named_steps") and "encoder" in transformer.named_steps:
                encoder = transformer.named_steps["encoder"]
                categories.update({field: [str(v) for v in values]
                                   for field, values in zip(columns, encoder.categories_)})
    fields = []
    for name in names:
        options = categories.get(name)
        default = spec["defaults"].get(name, options[0] if options else 0.0)
        if options and str(default) not in options:
            default = options[0]
        label = name.replace("_", " ").title().replace(" Kes", " (KES)").replace(" Gpa", " GPA").replace(" Pct", " (%)")
        if name in ["police_report_missing", "credit_score_missing"]:
            label += " (0 = no, 1 = yes)"
        fields.append({"name": name, "label": label,
                       "options": options, "default": default})
    return fields


def example_payload(key):
    if key == "pharmacy-recommender":
        return dict(SPECS[key]["defaults"])
    return {field["name"]: field["default"] for field in input_schema(key)}


def predict(key, payload):
    if not isinstance(payload, dict):
        raise ValueError("Send inputs as a JSON object.")
    if key == "pharmacy-recommender":
        cart, top_n = payload.get("cart"), payload.get("top_n", 3)
        if not isinstance(cart, list) or not cart or not all(isinstance(v, str) for v in cart):
            raise ValueError("Select at least one product, or send cart as a list of product names/IDs.")
        if type(top_n) is not int or not 1 <= top_n <= 20:
            raise ValueError("top_n must be a whole number from 1 to 20.")
        known = {name.casefold() for name in PHARMACY["item_id_to_name"].values()}
        known.update(item.casefold() for item in PHARMACY["item_id_to_name"])
        unknown = [v for v in cart if v.strip().casefold() not in known]
        if unknown:
            raise ValueError("Unknown products: " + ", ".join(unknown))
        results = dynamic_recommender_advanced(cart, PHARMACY["cleaned_rules"],
                    PHARMACY["item_id_to_name"], PHARMACY["recommendation_lookup"], top_n)
        return {"cart": cart, "recommendations": results,
                "meaning": "Co-purchase patterns; not medical advice or proof of product suitability."}
    pipe = SPECS[key]["pipeline"]
    missing = [name for name in pipe.feature_names_in_ if name not in payload]
    if missing:
        raise ValueError("Missing inputs: " + ", ".join(missing))
    # Keep the exact training column order for all pipelines.
    row = pd.DataFrame([payload], columns=list(pipe.feature_names_in_))
    value = pipe.predict(row)[0]
    if key == "student-exam-score-regressor":
        return {"predicted_final_exam_score": round(float(value), 3)}
    if key == "bank-account-segmenter":
        cluster = int(value)
        return {"assigned_cluster": cluster, "segment": BANK["segment_names"][cluster]}
    probabilities = pipe.predict_proba(row)[0]
    return {"predicted_class": int(value), "category": "Fraudulent" if int(value) == 1 else "Legitimate",
            "class_probabilities": {str(label): round(float(prob), 6)
                                    for label, prob in zip(pipe.classes_, probabilities)}}
