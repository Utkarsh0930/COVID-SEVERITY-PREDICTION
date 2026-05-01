from flask import Flask, render_template, request, jsonify
import joblib
import pandas as pd
from pathlib import Path
import os

app = Flask(__name__)

# ✅  This is safe path (Render compatible)
BASE_DIR = Path(__file__).parent

model = joblib.load(BASE_DIR / "adaboost_covid_model.joblib")
label_encoder = joblib.load(BASE_DIR / "label_encoder.joblib")
feature_columns = joblib.load(BASE_DIR / "feature_columns.joblib")

# ✅ Severity metadata
SEVERITY_INFO = {
    "mild": {
        "label": "Mild",
        "color": "green",
        "advice": "Home isolation recommended. Monitor symptoms closely."
    },
    "moderate": {
        "label": "Moderate",
        "color": "amber",
        "advice": "Medical evaluation advised."
    },
    "severe": {
        "label": "Severe",
        "color": "red",
        "advice": "Immediate hospitalisation required."
    }
}

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    try:
        input_data = {}

        # ✅ Robust input handling (CRITICAL FIX)
        for col in feature_columns:
            val = request.form.get(col)

            if val is None or val.strip() == "":
                input_data[col] = 0  # default
            else:
                try:
                    input_data[col] = float(val)
                except:
                    input_data[col] = 0

        df = pd.DataFrame([input_data])[feature_columns]

        # ✅ Prediction
        pred = model.predict(df)[0]
        output = label_encoder.inverse_transform([pred])[0].lower()

        # ✅ Safe probability handling
        confidence = {}
        try:
            proba = model.predict_proba(df)[0]
            classes = [c.lower() for c in label_encoder.classes_]
            confidence = {
                cls: round(float(p) * 100, 1)
                for cls, p in zip(classes, proba)
            }
        except:
            pass

        info = SEVERITY_INFO.get(output, {
            "label": output.title(),
            "color": "gray",
            "advice": ""
        })

        return jsonify({
            "severity": output,
            "label": info["label"],
            "color": info["color"],
            "advice": info["advice"],
            "confidence": confidence
        })

    except Exception as e:
        # ✅ Debug-friendly error
        return jsonify({"error": str(e)}), 500


# ✅ Render-compatible run
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)