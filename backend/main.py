from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
from pathlib import Path
import pandas as pd
import numpy as np
import joblib
import sqlite3
import traceback

# ============================================================
# APP SETUP
# ============================================================

app = Flask(__name__)

app.secret_key = "fertilizer_optimizer_secret_key"

CORS(app, supports_credentials=True)

# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

FRONTEND_DIR = BASE_DIR / "frontend"
DATA_DIR = BASE_DIR / "data"
DATABASE_DIR = BASE_DIR / "database"

MODEL_PATH = BASE_DIR / "fertilizer_model.pkl"

DATABASE_DIR.mkdir(exist_ok=True)

DB_PATH = DATABASE_DIR / "fertilizer.db"

# ============================================================
# LOAD DATASET
# ============================================================

dataset = None

possible_datasets = [
    DATA_DIR / "fertilizer_recommendation.csv",
    DATA_DIR / "fertilizer_recommendation_master.csv",
    DATA_DIR / "fertilizer.csv",
]

for file_path in possible_datasets:
    if file_path.exists():
        try:
            dataset = pd.read_csv(file_path)
            print("Dataset loaded successfully.")
            print("Rows:", len(dataset))
            print("Columns:", len(dataset.columns))
            break
        except Exception as e:
            print("Dataset loading error:", e)

if dataset is None:
    print("WARNING: Dataset was not found.")

# ============================================================
# LOAD MACHINE LEARNING MODEL
# ============================================================

model = None

if MODEL_PATH.exists():

    try:
        model = joblib.load(MODEL_PATH)
        print("ML model loaded successfully.")

    except Exception as e:
        print("Model loading error:", e)

else:
    print("WARNING: fertilizer_model.pkl was not found.")

# ============================================================
# DATABASE
# ============================================================

def initialize_database():

    connection = sqlite3.connect(DB_PATH)

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            crop TEXT,
            nitrogen REAL,
            phosphorus REAL,
            potassium REAL,
            ph REAL,
            moisture REAL,
            organic_carbon REAL,
            temperature REAL,
            humidity REAL,
            fertilizer TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()

    print("Database initialized successfully.")


initialize_database()

# ============================================================
# HELPER FUNCTION
# ============================================================

def get_value(data, *names, default=None):

    for name in names:

        if name in data:
            return data[name]

    return default


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def home():

    return send_from_directory(
        FRONTEND_DIR,
        "index.html"
    )


# ============================================================
# DASHBOARD PAGE
# ============================================================

@app.route("/dashboard")
def dashboard():
    return send_from_directory(FRONTEND_DIR, "dashboard.html")

@app.route("/history")
@app.route("/statistics")
@app.route("/dataset")
def dashboard_section():
    return send_from_directory(FRONTEND_DIR, "dashboard.html")


# ============================================================
# AI ASSISTANT PAGE
# ============================================================

@app.route("/ai-assistant")
@app.route("/ai_assistant")
def ai_assistant_page():

    return send_from_directory(
        FRONTEND_DIR,
        "ai_assistant.html"
    )


# ============================================================
# STATIC FILES
# ============================================================

@app.route("/<path:filename>")
def frontend_files(filename):

    file_path = FRONTEND_DIR / filename

    if file_path.exists() and file_path.is_file():

        return send_from_directory(
            FRONTEND_DIR,
            filename
        )

    return jsonify({
        "success": False,
        "message": "File not found"
    }), 404


# ============================================================
# USER API
# ============================================================

@app.route("/api/me")
def api_me():

    return jsonify({
        "success": True,
        "user": {
            "name": "User",
            "email": "user@gmail.com"
        }
    })


# ============================================================
# DATASET INFORMATION API
# ============================================================

@app.route("/api/dataset-info")
def dataset_info():

    if dataset is None:

        return jsonify({
            "success": False,
            "message": "Dataset is not loaded."
        })

    return jsonify({
        "success": True,
        "rows": int(dataset.shape[0]),
        "columns": int(dataset.shape[1]),
        "column_names": dataset.columns.tolist()
    })


# ============================================================
# DATASET API
# ============================================================

@app.route("/api/dataset")
def dataset_api():

    if dataset is None:

        return jsonify({
            "success": False,
            "message": "Dataset is not loaded."
        }), 500

    data = dataset.head(100).replace(
        {np.nan: None}
    ).to_dict(orient="records")

    return jsonify({
        "success": True,
        "data": data
    })


# ============================================================
# HISTORY API
# ============================================================

@app.route("/api/history")
def history():

    try:

        connection = sqlite3.connect(DB_PATH)

        connection.row_factory = sqlite3.Row

        cursor = connection.cursor()

        cursor.execute("""
            SELECT *
            FROM history
            ORDER BY id DESC
        """)

        rows = cursor.fetchall()

        connection.close()

        result = [
            dict(row)
            for row in rows
        ]

        return jsonify({
            "success": True,
            "history": result
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


# ============================================================
# STATISTICS API
# ============================================================

@app.route("/api/statistics")
@app.route("/api/stats")
def statistics():

    try:

        connection = sqlite3.connect(DB_PATH)

        cursor = connection.cursor()

        cursor.execute(
            "SELECT COUNT(*) FROM history"
        )

        total = cursor.fetchone()[0]

        cursor.execute("""
            SELECT fertilizer, COUNT(*)
            FROM history
            GROUP BY fertilizer
            ORDER BY COUNT(*) DESC
        """)

        fertilizer_data = cursor.fetchall()

        connection.close()

        return jsonify({
            "success": True,
            "total_recommendations": total,
            "fertilizers": [
                {
                    "fertilizer": row[0],
                    "count": row[1]
                }
                for row in fertilizer_data
            ]
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


# ============================================================
# FERTILIZER RECOMMENDATION
# ============================================================

@app.route("/api/recommend", methods=["POST"])
@app.route("/api/recommendation", methods=["POST"])
def recommend():

    try:

        data = request.get_json()

        if not data:

            return jsonify({
                "success": False,
                "message": "No input data received."
            }), 400

        # ----------------------------------------------------
        # GET INPUT VALUES
        # ----------------------------------------------------

        crop = get_value(
            data,
            "crop",
            "Crop",
            default="Unknown"
        )

        nitrogen = float(
            get_value(
                data,
                "nitrogen",
                "Nitrogen",
                "N",
                default=0
            )
        )

        phosphorus = float(
            get_value(
                data,
                "phosphorus",
                "Phosphorus",
                "P",
                default=0
            )
        )

        potassium = float(
            get_value(
                data,
                "potassium",
                "Potassium",
                "K",
                default=0
            )
        )

        ph = float(
            get_value(
                data,
                "ph",
                "pH",
                "soil_ph",
                default=7
            )
        )

        moisture = float(
            get_value(
                data,
                "moisture",
                "soil_moisture",
                default=0
            )
        )

        organic_carbon = float(
            get_value(
                data,
                "organic_carbon",
                "organicCarbon",
                default=0
            )
        )

        temperature = float(
            get_value(
                data,
                "temperature",
                "Temperature",
                default=25
            )
        )

        humidity = float(
            get_value(
                data,
                "humidity",
                "Humidity",
                default=60
            )
        )

        # ----------------------------------------------------
        # MACHINE LEARNING PREDICTION
        # ----------------------------------------------------

        fertilizer = "Urea"

        if model is not None:

            try:

                # Standard feature order used by this project
                features = np.array([[
                    nitrogen,
                    phosphorus,
                    potassium,
                    ph,
                    moisture,
                    organic_carbon,
                    temperature,
                    humidity
                ]])

                prediction = model.predict(features)

                fertilizer = str(
                    prediction[0]
                )

            except Exception as model_error:

                print(
                    "ML prediction error:",
                    model_error
                )

                # Try DataFrame prediction
                try:

                    features_df = pd.DataFrame([{
                        "Nitrogen": nitrogen,
                        "Phosphorus": phosphorus,
                        "Potassium": potassium,
                        "pH": ph,
                        "Soil Moisture": moisture,
                        "Organic Carbon": organic_carbon,
                        "Temperature": temperature,
                        "Humidity": humidity
                    }])

                    prediction = model.predict(
                        features_df
                    )

                    fertilizer = str(
                        prediction[0]
                    )

                except Exception:

                    fertilizer = "Urea"

        # ----------------------------------------------------
        # SAVE RECOMMENDATION
        # ----------------------------------------------------

        try:

            connection = sqlite3.connect(DB_PATH)

            cursor = connection.cursor()

            cursor.execute("""
                INSERT INTO history (
                    email,
                    crop,
                    nitrogen,
                    phosphorus,
                    potassium,
                    ph,
                    moisture,
                    organic_carbon,
                    temperature,
                    humidity,
                    fertilizer
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                "user@gmail.com",
                crop,
                nitrogen,
                phosphorus,
                potassium,
                ph,
                moisture,
                organic_carbon,
                temperature,
                humidity,
                fertilizer
            ))

            connection.commit()
            connection.close()

        except Exception as db_error:

            print(
                "Database save error:",
                db_error
            )

        # ----------------------------------------------------
        # RESPONSE
        # ----------------------------------------------------

        return jsonify({
            "success": True,
            "fertilizer": fertilizer,
            "recommendation": fertilizer,
            "crop": crop,
            "message": "Fertilizer recommendation generated successfully."
        })

    except Exception as e:

        print(
            "Recommendation error:",
            traceback.format_exc()
        )

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


# ============================================================
# AI FARMING ASSISTANT
# ============================================================

@app.route("/api/ai-assistant", methods=["POST"])
@app.route("/api/ai_assistant", methods=["POST"])
def ai_assistant():

    try:

        data = request.get_json()

        question = str(
            get_value(
                data,
                "question",
                "message",
                "query",
                default=""
            )
        ).lower().strip()

        if not question:

            return jsonify({
                "success": False,
                "message": "Please enter a question."
            }), 400

        # ----------------------------------------------------
        # SIMPLE AGRICULTURE KNOWLEDGE BASE
        # ----------------------------------------------------

        if "wheat" in question and "fertilizer" in question:

            answer = (
                "Wheat requires balanced nutrition, especially "
                "nitrogen, phosphorus and potassium. The exact "
                "fertilizer should depend on soil test results "
                "and crop requirements."
            )

        elif "nitrogen" in question:

            answer = (
                "Nitrogen helps plants grow healthy leaves and "
                "supports overall plant growth."
            )

        elif "ph" in question:

            answer = (
                "Soil pH shows whether the soil is acidic or "
                "alkaline. Most crops grow well in a slightly "
                "acidic to neutral pH range."
            )

        elif "irrigation" in question:

            answer = (
                "Irrigation provides water to crops when rainfall "
                "is not enough. Water should be supplied according "
                "to crop and soil moisture requirements."
            )

        elif "improve soil" in question:

            answer = (
                "Soil health can be improved by adding organic "
                "matter, using compost, maintaining proper "
                "moisture and applying fertilizers according "
                "to soil test results."
            )

        elif "fertilizer" in question:

            answer = (
                "Fertilizer provides nutrients such as nitrogen, "
                "phosphorus and potassium. The suitable fertilizer "
                "depends on crop type and soil conditions."
            )

        elif "npk" in question:

            answer = (
                "NPK stands for Nitrogen, Phosphorus and Potassium. "
                "These are three major nutrients required by plants."
            )

        elif "soil" in question:

            answer = (
                "Healthy soil should have suitable pH, moisture, "
                "nutrients and organic matter for good crop growth."
            )

        else:

            answer = (
                "I can help you with fertilizers, soil, crops, "
                "NPK, pH, irrigation and farming practices."
            )

        return jsonify({
            "success": True,
            "answer": answer,
            "message": answer
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


# ============================================================
# LOGIN
# ============================================================

@app.route("/api/login", methods=["POST"])
def login():

    try:

        data = request.get_json()

        email = data.get(
            "email",
            "user@gmail.com"
        )

        session["email"] = email

        return jsonify({
            "success": True,
            "message": "Login successful",
            "user": {
                "email": email
            }
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 400


# ============================================================
# LOGOUT
# ============================================================

@app.route("/api/logout")
def logout():

    session.clear()

    return jsonify({
        "success": True,
        "message": "Logged out successfully."
    })


# ============================================================
# START FLASK SERVER
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("       FERTILIZER OPTIMIZATION RECOMMENDER")
    print("                 FLASK BACKEND")
    print("=" * 60)

    print()
    print("Backend running at:")
    print("http://127.0.0.1:5000")

    print()
    print("Dashboard:")
    print("http://127.0.0.1:5000/dashboard")

    print()
    print("AI Assistant:")
    print("http://127.0.0.1:5000/ai-assistant")

    print()
    print("=" * 60)

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )