print("🔥 REAL-TIME PREDICTORS LOADED (FINAL HUMAN-CALIBRATED VERSION) 🔥")

import numpy as np
from tensorflow.keras.models import load_model
from utils.preprocess import preprocess_image
from utils.ingredient_guidance import get_guidance

# =====================================================
# LOAD MODELS (ONCE ONLY)
# =====================================================
MODELS = {
    "acne": load_model("models/acne_model.h5"),
    "darkcircles": load_model("models/darkcircles_model.h5"),
    "dryness": load_model("models/dryness_model.h5"),
    "oiliness": load_model("models/oiliness_model.h5"),
    "pigmentation": load_model("models/pigmentation_model.h5"),
    "pores": load_model("models/pores_model.h5"),
}

LABELS = ["normal", "mild", "moderate", "severe"]

# =====================================================
# SINGLE CONDITION PREDICTION (FINAL FIX)
# =====================================================
def predict_condition(condition, image_path):
    model = MODELS[condition]

    # preprocess image
    img = preprocess_image(image_path)
    img = img.copy()   # avoid tensor reuse issues

    # model prediction
    probs = model.predict(img, verbose=0)[0]
    probs = np.clip(probs, 1e-6, 1.0)
    probs = probs / np.sum(probs)

    # extract probabilities
    normal_p = probs[LABELS.index("normal")]
    mild_p = probs[LABELS.index("mild")]
    moderate_p = probs[LABELS.index("moderate")]
    severe_p = probs[LABELS.index("severe")]

    # =================================================
    # 🔥 CLINICAL RULE (THIS FIXES CLEAR SKIN ISSUE)
    # =================================================
    if (normal_p + mild_p) >= (moderate_p + severe_p):
        severity = "normal"
    else:
        severity = LABELS[int(np.argmax(probs))]

    confidence = round(float(np.max(probs)) * 100, 2)

    # =================================================
    # REALISTIC PERCENTAGE CALCULATION
    # =================================================
    percentage = round(
        (mild_p * 15) +
        (moderate_p * 40) +
        (severe_p * 70),
        2
    )

    # 🔒 HARD SAFETY: clear skin must not exceed this
    if severity == "normal":
        percentage = min(percentage, 12.0)

    # =================================================
    # INGREDIENT + NOTE LOGIC
    # =================================================
    if severity == "normal":
        ingredients = [
            "Gentle cleanser",
            "Light moisturizer",
            "Broad-spectrum sunscreen"
        ]
        notes = "No visible acne detected. Your skin appears clear and healthy."
    else:
        guide = get_guidance(condition, percentage)
        ingredients = guide.get("ingredients", [])
        notes = guide.get("note", "Targeted care recommended.")

    return {
        "severity": severity,
        "percentage": percentage,
        "confidence": confidence,
        "ingredients": ingredients,
        "notes": notes
    }

# =====================================================
# OVERALL SKIN HEALTH (HUMAN ALIGNED)
# =====================================================
def calculate_overall_health(results):
    avg_problem = sum(results.values()) / len(results)

    health_score = round(100 - avg_problem, 2)

    # cap unrealistic values
    health_score = min(health_score, 92)

    if health_score >= 85:
        message = "Your skin looks healthy and well maintained."
    elif health_score >= 70:
        message = "Your skin is in good condition overall."
    elif health_score >= 55:
        message = "Your skin shows moderate concerns."
    else:
        message = "Your skin has multiple visible concerns."

    return health_score, message

# =====================================================
# MAIN ANALYSIS ENTRY POINT
# =====================================================
def analyze_skin(image_path):
    results = {}
    detailed = {}

    for condition in MODELS:
        output = predict_condition(condition, image_path)
        results[condition] = output["percentage"]
        detailed[condition] = output

    health_score, health_message = calculate_overall_health(results)

    main_issue = max(results, key=results.get)

    # soft human-safe suggestion
    if results[main_issue] < 18:
        suggestion = "No major skin concerns detected. Continue your current skincare routine."
    else:
        suggestion = (
            f"{main_issue.capitalize()} appears slightly more prominent. "
            f"Focused care can improve overall skin balance."
        )

    return {
        "conditions": detailed,
        "overall_health_percentage": health_score,
        "overall_health_message": health_message,
        "main_focus_area": main_issue,
        "final_suggestion": suggestion
    }
