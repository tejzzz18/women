import os
import pathlib
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
from pymongo import MongoClient
from dotenv import load_dotenv

# ------------------------------
# Load environment variables
# ------------------------------
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")  # <-- Put your MongoDB API Key here in .env
DB_NAME = os.getenv("MONGO_DBNAME", "mahila_reports")
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "static/uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "pdf"}

# ensure uploads directory exists
pathlib.Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)

# ------------------------------
# Flask App Setup
# ------------------------------
app = Flask(__name__)
app.secret_key = "replace_this_in_production"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50MB max

# ------------------------------
# MongoDB Setup
# ------------------------------
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
reports_col = db["reports"]


# ------------------------------
# Helpers
# ------------------------------
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ------------------------------
# Inject year globally
# ------------------------------
@app.context_processor
def inject_year():
    return {"current_year": datetime.utcnow().year}


# --------------------------------
#            ENGLISH ROUTES
# --------------------------------

@app.route("/")
def home():
    return render_template("ehome.html")


@app.route("/articles")
def articles():
    return render_template("earticle.html")


@app.route("/articles/physical")
def physical_article():
    return render_template("physical.html")


@app.route("/articles/emotional")
def emotional_article():
    return render_template("emotional.html")


@app.route("/articles/digital")
def digital_article():
    return render_template("d.html")


@app.route("/about")
def about():
    return render_template("eaboutus.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")

        if not name or not email or not message:
            flash("Please fill in all required fields.", "error")
            return redirect(url_for("contact"))

        flash("Your message has been received!", "success")
        return redirect(url_for("contact"))

    return render_template("econtact.html")


@app.route("/help")
def help_page():
    return render_template("ehelp.html")


# ============================
#     SAVE REPORT TO MONGODB
# ============================

@app.route("/submit_report", methods=["POST"])
def submit_report():
    """Handles AJAX submission from ereport.html"""

    name = request.form.get("name", "").strip()
    contact = request.form.get("contact", "").strip()
    category = request.form.get("category", "").strip()
    location = request.form.get("location", "").strip()
    incident = request.form.get("incident", "").strip()

    if not name or not contact or not category or not location or not incident:
        return jsonify({"success": False, "error": "All fields except evidence are required."}), 400

    uploaded_files = request.files.getlist("evidence")
    saved_files = []

    for file in uploaded_files:
        if file and file.filename:
            if not allowed_file(file.filename):
                return jsonify({"success": False, "error": "File type not allowed"}), 400

            filename = secure_filename(file.filename)
            save_path = os.path.join(UPLOAD_FOLDER, filename)

            # avoid overwriting
            base, ext = os.path.splitext(filename)
            counter = 1
            while os.path.exists(save_path):
                filename = f"{base}_{counter}{ext}"
                save_path = os.path.join(UPLOAD_FOLDER, filename)
                counter += 1

            file.save(save_path)
            saved_files.append(save_path)

    # Save document into MongoDB
    report_doc = {
        "name": name,
        "contact": contact,
        "category": category,
        "location": location,
        "incident": incident,
        "evidence_files": saved_files,
        "created_at": datetime.utcnow(),
        "language": "english",
    }

    inserted_id = reports_col.insert_one(report_doc).inserted_id

    return jsonify({"success": True, "id": str(inserted_id)}), 201


@app.route("/report", methods=["GET"])
def report():
    return render_template("ereport.html")


@app.route("/stories")
def stories():
    return render_template("ytvideos.html")


@app.route("/selfdefence")
def selfdefence():
    return render_template("evideos.html")


@app.route("/chatbot")
def chatbot():
    return render_template("chatbot.html")


@app.route("/feedback", methods=["GET", "POST"])
def feedback():
    if request.method == "POST":
        flash("Thank you for your feedback!", "success")
        return redirect(url_for("feedback"))

    return render_template("efeedback.html")


# --------------------------------
#          KANNADA ROUTES
# --------------------------------

@app.route("/kannada")
def kannada_home():
    return render_template("khome.html")


@app.route("/karticle")
def karticle():
    return render_template("karticle.html")


@app.route("/kabout")
def kabout():
    return render_template("kaboutus.html")


@app.route("/kcontact", methods=["GET", "POST"])
def kcontact():
    if request.method == "POST":
        flash("ನಿಮ್ಮ ಸಂದೇಶವನ್ನು ಸ್ವೀಕರಿಸಲಾಗಿದೆ!", "success")
        return redirect(url_for("kcontact"))
    return render_template("kcontact.html")


@app.route("/khelp")
def khelp():
    return render_template("khelp.html")


# ============================
#  KANNADA REPORT SAVE
# ============================

@app.route("/submit_kreport", methods=["POST"])
def submit_kreport():
    """Separate endpoint for kreport.html"""

    name = request.form.get("name", "").strip()
    contact = request.form.get("contact", "").strip()
    category = request.form.get("category", "").strip()
    location = request.form.get("location", "").strip()
    incident = request.form.get("incident", "").strip()

    uploaded_files = request.files.getlist("evidence")
    saved_files = []

    for file in uploaded_files:
        if file and file.filename:
            filename = secure_filename(file.filename)
            save_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(save_path)
            saved_files.append(save_path)

    report_doc = {
        "name": name,
        "contact": contact,
        "category": category,
        "location": location,
        "incident": incident,
        "evidence_files": saved_files,
        "created_at": datetime.utcnow(),
        "language": "kannada",
    }

    inserted_id = reports_col.insert_one(report_doc).inserted_id
    flash("ಘಟನೆ ಯಶಸ್ವಿಯಾಗಿ ಸಲ್ಲಿಸಲಾಗಿದೆ.", "success")
    return redirect(url_for("kreport"))


@app.route("/kreport")
def kreport():
    return render_template("kreport.html")


@app.route("/kselfdefence")
def kselfdefence():
    return render_template("kvideos.html")


@app.route("/kfeedback", methods=["GET", "POST"])
def kfeedback():
    if request.method == "POST":
        flash("ಪ್ರತಿಕ್ರಿಯೆಗೆ ಧನ್ಯವಾದಗಳು!", "success")
        return redirect(url_for("kfeedback"))
    return render_template("kfeedback.html")


# ------------------------------
#     Run Server
# ------------------------------
if __name__ == "__main__":
    app.run(debug=True)
