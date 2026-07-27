# utils/ingredient_guidance.py

def get_guidance(condition, percentage):
    """
    Returns ingredient guidance based on condition and severity percentage
    """

    guidance_map = {
        "acne": [
            {
                "min": 0,
                "max": 35,
                "ingredients": ["Niacinamide 2–5%", "Green Tea Extract"],
                "note": "Early acne control and barrier support"
            },
            {
                "min": 36,
                "max": 65,
                "ingredients": ["Salicylic Acid 0.5–2%", "Niacinamide 5%"],
                "note": "Active acne management"
            },
            {
                "min": 66,
                "max": 100,
                "ingredients": ["Benzoyl Peroxide 2.5%", "Salicylic Acid 2%"],
                "note": "Severe acne – dermatologist grade care recommended"
            }
        ],

        "darkcircles": [
            {
                "min": 0,
                "max": 35,
                "ingredients": ["Caffeine", "Vitamin C"],
                "note": "Mild pigmentation and fatigue marks"
            },
            {
                "min": 36,
                "max": 65,
                "ingredients": ["Niacinamide", "Peptides"],
                "note": "Moderate dark circle correction"
            },
            {
                "min": 66,
                "max": 100,
                "ingredients": ["Retinol (Eye-safe)", "Kojic Acid"],
                "note": "Advanced dark circle treatment"
            }
        ],

        "dryness": [
            {
                "min": 0,
                "max": 35,
                "ingredients": ["Glycerin", "Aloe Vera"],
                "note": "Light hydration support"
            },
            {
                "min": 36,
                "max": 65,
                "ingredients": ["Hyaluronic Acid", "Ceramides"],
                "note": "Skin barrier repair"
            },
            {
                "min": 66,
                "max": 100,
                "ingredients": ["Shea Butter", "Squalane"],
                "note": "Intense moisture therapy"
            }
        ],

        "oiliness": [
            {
                "min": 0,
                "max": 35,
                "ingredients": ["Green Tea", "Zinc PCA"],
                "note": "Oil balance maintenance"
            },
            {
                "min": 36,
                "max": 65,
                "ingredients": ["Niacinamide", "Clay"],
                "note": "Sebum control"
            },
            {
                "min": 66,
                "max": 100,
                "ingredients": ["Salicylic Acid", "Charcoal"],
                "note": "Excess oil detox"
            }
        ],

        "pigmentation": [
            {
                "min": 0,
                "max": 35,
                "ingredients": ["Vitamin C", "Licorice Extract"],
                "note": "Tone brightening"
            },
            {
                "min": 36,
                "max": 65,
                "ingredients": ["Alpha Arbutin", "Niacinamide"],
                "note": "Pigment correction"
            },
            {
                "min": 66,
                "max": 100,
                "ingredients": ["Kojic Acid", "Tranexamic Acid"],
                "note": "Advanced pigmentation treatment"
            }
        ],

        "pores": [
            {
                "min": 0,
                "max": 35,
                "ingredients": ["Niacinamide", "Witch Hazel"],
                "note": "Pore tightening"
            },
            {
                "min": 36,
                "max": 65,
                "ingredients": ["Salicylic Acid", "Retinol"],
                "note": "Pore refinement"
            },
            {
                "min": 66,
                "max": 100,
                "ingredients": ["Chemical Exfoliants (AHA/BHA)"],
                "note": "Deep pore cleansing"
            }
        ]
    }

    for rule in guidance_map.get(condition, []):
        if rule["min"] <= percentage <= rule["max"]:
            return rule

    return {
        "ingredients": [],
        "note": "No guidance available"
    }
