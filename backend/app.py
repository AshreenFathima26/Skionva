from flask import Flask, render_template, request, session, redirect, jsonify, send_file
import os
import uuid
import base64
import time
import random
import pdfkit
from flask import send_file
from datetime import datetime
from flask import session
from io import BytesIO
from database.progress_service import save_progress, get_progress
import traceback
from services.weather_service import get_weather
from services.recommendation_service import RecommendationEngine




from utils.preprocess import preprocess_image
from utils.predictors import analyze_skin   # REAL ML LOGIC

config = pdfkit.configuration(
    wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
)
# -------------------------------------------------
# APP INITIALIZATION
# -------------------------------------------------
app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)

app.secret_key = "skinova_secure_key_2026"


# -------------------------------------------------
# CONFIGURATION
# -------------------------------------------------
UPLOAD_FOLDER = os.path.join("static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

# -------------------------------------------------
# HELPER FUNCTIONS
# -------------------------------------------------
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_base64_image(base64_string):
    """
    Saves a base64 image and returns the file path
    """
    image_data = base64.b64decode(base64_string.split(",")[1])
    filename = f"{uuid.uuid4().hex}.png"
    path = os.path.join(UPLOAD_FOLDER, filename)

    with open(path, "wb") as f:
        f.write(image_data)

    return path, filename


# -------------------------------------------------
# PAGE ROUTES
# -------------------------------------------------
@app.route("/")
def splash():
    return render_template("splash.html")

@app.route("/register", methods=["GET","POST"])
def register():

    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    return render_template("login.html")

@app.route("/session-login", methods=["POST"])
def session_login():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "No data received"
        }), 400

    session["uid"] = data.get("uid")
    session["email"] = data.get("email")

    return jsonify({
        "success": True,
        "message": "Session created successfully"
    })


@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/analyzer")
def analyzer():
    return render_template("analyzer.html")

@app.route("/score")
def score():
    return render_template("score.html")



@app.route("/progress")
def progress():
    return render_template("progress.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/skintrack")
def skintrack():
    return render_template("skintrack.html")



# -------------------------------------------------
# API: IMAGE UPLOAD (FORM DATA)
# -------------------------------------------------
@app.route("/analyze-skin", methods=["POST"])
def analyze_skin_api():
    """
    Handles single image upload
    """

    if "image" not in request.files:
        return jsonify({"success": False, "error": "No image uploaded"}), 400

    image = request.files["image"]

    if image.filename == "" or not allowed_file(image.filename):
        return jsonify({"success": False, "error": "Invalid image"}), 400

    filename = f"{uuid.uuid4().hex}.png"
    image_path = os.path.join(UPLOAD_FOLDER, filename)
    image.save(image_path)

    # Force fresh processing
    time.sleep(0.1)

    preprocess_image(image_path)
    result = analyze_skin(image_path)

    session["analysis_result"] = result

    return jsonify({"success": True}), 200


# -------------------------------------------------
# API: REAL-TIME MULTI FRAME ANALYSIS
# -------------------------------------------------
@app.route("/analyze-skin-realtime", methods=["POST"])
def analyze_skin_realtime():
    """
    Accepts multiple frames (base64),
    performs averaging to stabilize predictions
    """

    data = request.get_json()
    images = data.get("images", [])

    if not images or len(images) < 3:
        return jsonify({
            "success": False,
            "error": "Minimum 3 frames required"
        }), 400

    all_results = []

    for img_base64 in images:
        path, _ = save_base64_image(img_base64)

        # Force inference re-run
        time.sleep(0.05)

        result = analyze_skin(path)
        all_results.append(result)

    # -------------------------------------------------
    # AVERAGING LOGIC
    # -------------------------------------------------
    avg_health = round(
        sum(r["overall_health_percentage"] for r in all_results) / len(all_results),
        2
    )

    averaged_conditions = {}

    for condition in all_results[0]["conditions"]:
        avg_percentage = sum(
            r["conditions"][condition]["percentage"] for r in all_results
        ) / len(all_results)

        # ---- FALSE POSITIVE SUPPRESSION ----
        if avg_percentage < 18:
            severity = "normal"
            avg_percentage = 0
        elif avg_percentage < 35:
            severity = "mild"
        elif avg_percentage < 60:
            severity = "moderate"
        else:
            severity = "severe"

        averaged_conditions[condition] = {
            "percentage": round(avg_percentage, 2),
            "severity": severity,
            "ingredients": all_results[0]["conditions"][condition]["ingredients"],
            "notes": all_results[0]["conditions"][condition]["notes"],
        }

    # -------------------------------------------------
    # SMART PERSONAL SUGGESTION
    # -------------------------------------------------
    significant = {
        k: v for k, v in averaged_conditions.items()
        if v["percentage"] >= 25
    }

    if not significant:
        final_suggestion = "Your skin appears healthy with no prominent concerns."
    else:
        focus = max(significant, key=lambda k: significant[k]["percentage"])
        final_suggestion = f"{focus.capitalize()} needs slightly more attention."

    final_result = {
        "overall_health_percentage": avg_health,
        "overall_health_message": "Your skin is in good condition overall.",
        "conditions": averaged_conditions,
        "final_suggestion": final_suggestion
    }

    session["analysis_result"] = final_result

    return jsonify({
        "success": True,
        "data": final_result
    }), 200


# -------------------------------------------------
# API: BASE64 SINGLE IMAGE (CAMERA / UPLOAD)
# -------------------------------------------------
@app.route("/analyze-image-base64", methods=["POST"])
def analyze_image_base64():
    try:
        data = request.get_json(force=True)

        if not data or "image" not in data:
            return jsonify({"success": False, "error": "No image data"}), 400

        image_data = data["image"]

        # 🔧 Remove base64 header safely
        if "," in image_data:
            image_data = image_data.split(",")[1]

        # Decode base64
        image_bytes = base64.b64decode(image_data)

        # 🔥 SAFE IMAGE LOAD (THIS IS THE KEY FIX)
        from io import BytesIO
        from PIL import Image

        img = Image.open(BytesIO(image_bytes)).convert("RGB")

        filename = f"{uuid.uuid4().hex}.jpg"
        image_path = os.path.join(UPLOAD_FOLDER, filename)

        img.save(image_path, format="JPEG", quality=95)

        # ---- ML ANALYSIS ----
        result = analyze_skin(image_path)

        

        session["uploaded_image"] = filename
        session["overall_score"] = result["overall_health_percentage"]
        session["skin_message"] = result["overall_health_message"]
        session["focus_area"] = result["main_focus_area"]
        session["final_suggestion"] = result["final_suggestion"]
        session["conditions"] = result["conditions"]

        conditions = result["conditions"]

        session["acne"] = conditions.get("acne", 0)
        session["dark"] = conditions.get("dark_circles", 0)
        session["dry"] = conditions.get("dryness", 0)
        session["oil"] = conditions.get("oiliness", 0)
        session["pig"] = conditions.get("pigmentation", 0)
        session["pores"] = conditions.get("pores", 0)

        

        return jsonify({
            "success": True,
            "data": {
                "image_path": filename,
                "overall_health_percentage": result["overall_health_percentage"],
                "overall_health_message": result["overall_health_message"],
                "main_focus_area": result["main_focus_area"],
                "final_suggestion": result["final_suggestion"],
                "conditions": result["conditions"]
            }
        })

    except Exception as e:
     traceback.print_exc()

    return jsonify({
        "success": False,
        "message": str(e)
    }), 500


# -------------------------------------------------
# RUN SERVER
# -------------------------------------------------
@app.route("/report")
def report():

    data = {
        "date": datetime.today().strftime("%d %B %Y"),

        "name": session.get("name"),
        "age": session.get("age"),
        "email": session.get("email"),
        "phone": session.get("phone"),

        "skin_type": session.get("skin_type"),

        "score": session.get("overall_score"),

        "conditions": session.get("conditions"),

        "image": "static/uploads/" + str(session.get("uploaded_image")),
        
        "template_bg":os.path.abspath("static/images/skinovatemp.png")
    }

    return render_template("report.html", **data)

@app.route("/download_report")
def download_report():

   data = {
    "template_bg": os.path.abspath("static/images/skinovatemp.png"),
    "css_file": os.path.abspath("static/css/report.css"),
    "report_id": "SKN-" + datetime.now().strftime("%Y%m%d%H%M"),
    "date": datetime.today().strftime("%d %b %Y"),
    "time": datetime.now().strftime("%I:%M %p"),

    "name": request.args.get("name"),
    "age": request.args.get("age"),
    "gender": request.args.get("gender"),
    "email": session.get("email"),
    "phone": session.get("phone"),

    "skin_type": session.get("skin_type"),
    "overall_score": session.get("overall_score"),
    "conditions": session.get("conditions"),

    "image": os.path.abspath(
        "static/uploads/" + str(session.get("uploaded_image"))
        
    ),

    "logo": os.path.abspath(
        "static/images/logo.png"
    )
}
   html = render_template("report.html", **data)

   config = pdfkit.configuration(
        wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
    )

   options = {
    "enable-local-file-access": None,
    "page-size": "A4",
    "margin-top": "0mm",
    "margin-right": "0mm",
    "margin-bottom": "0mm",
    "margin-left": "0mm"
}

   pdf = pdfkit.from_string(
        html,
        False,
        options=options,
        configuration=config
)

   return send_file(
        BytesIO(pdf),
        as_attachment=True,
        download_name="Skinova_Report.pdf",
        mimetype="application/pdf"
    )

@app.route("/save-progress", methods=["POST"])
def save_progress_api():

    try:
        data = request.get_json()

        uid = session.get("uid")

        if not uid:
         return jsonify({
        "success": False,
        "message": "User not logged in."
        }), 401

        analysis_data = {
            "overall_score": data.get("overall_score"),
            "conditions": data.get("conditions"),
            "final_suggestion": data.get("final_suggestion"),
            "image": data.get("image")
        }

        save_progress(uid, analysis_data)

        return jsonify({
            "success": True,
            "message": "✅ Progress saved successfully!"
        })

    except Exception as e:
        print(e)

        return jsonify({
            "success": False,
            "message": "Failed to save progress."
        }), 500
@app.route("/get-progress")
def get_progress_api():

    try:

        uid = session.get("uid")

        if not uid:

            return jsonify({

                "success": False,
                "message": "Please login first."

            }),401

        progress = get_progress(uid)

        return jsonify({

            "success": True,
            "progress": progress

        })

    except Exception as e:

        import traceback

        traceback.print_exc()

        return jsonify({

            "success": False,
            "message": str(e)

        }),500
        
@app.route("/weather")
def weather():
    lat = request.args.get("lat")
    lon = request.args.get("lon")

    if not lat or not lon:
        return jsonify({"error": "Location not provided"}), 400

    data = get_weather(lat, lon)
    return jsonify(data)        

@app.route("/recommendation")
def recommendation():

    weather = get_weather(
        request.args.get("lat"),
        request.args.get("lon")
    )

    progress = get_progress(session["uid"])

    latest = progress[-1]

    score = latest["overall_score"]

    conditions = []

    for name, value in latest["conditions"].items():

        if value["percentage"] >= 20:
            conditions.append(name)

    engine = RecommendationEngine(
        weather,
        conditions,
        score
    )

    return jsonify(engine.generate())

@app.route("/profile")
def profile():
    if "uid" not in session:
        return redirect("/login")

    return render_template("profile.html")

@app.route("/profile-data")
def profile_data():

    uid = session.get("uid")

    if not uid:
        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    progress = get_progress(uid)

    total_analyses = len(progress)

    if total_analyses > 0:

        scores = [item["overall_score"] for item in progress]

        average_score = round(sum(scores) / total_analyses)

        best_score = max(scores)

        joined_date = progress[0]["date"]

    else:

        average_score = 0
        best_score = 0
        joined_date = "N/A"

    return jsonify({

        "name": session.get("name", "Skinova User"),

        "username": uid[:8],

        "email": session.get("email"),

        "joined_date": joined_date,

        "total_analyses": total_analyses,

        "average_score": average_score,

        "best_score": best_score,

        "report_count": total_analyses

    })

if __name__ == "__main__":
    print("🔥 SKINOVA REAL-TIME ML SERVER STARTED 🔥")
    app.run(debug=True)