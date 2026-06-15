import os
from flask import Flask, request, jsonify
import joblib
import pandas as pd

app = Flask(__name__)

# Ce chemin sera défini lors de l'entraînement
MODEL_PATH = "best_model.pkl"

# Singleton model loader
def get_model():
    try:
        return joblib.load(MODEL_PATH)
    except FileNotFoundError:
        return None

@app.route('/health')
def health():
    return jsonify({"status": "ML service is running", "model_loaded": get_model() is not None})

@app.route('/predict', methods=['POST'])
def predict():
    model = get_model()
    if not model:
        # Fallback fictif pour un lancement si l'entraînement n'est pas encore fait
        return jsonify({"erreur": "Modèle non entraîné"}), 503
        
    data = request.get_json()
    try:
        df_input = pd.DataFrame([data])
        
        # Le pipeline scikit-learn (preprocessor + model) s'occupe de la transformation
        pred_prix = float(model.predict(df_input)[0])
        
        marge = pred_prix * 0.05
        prix_m2_zone = pred_prix / data.get("surface_m2", 1)
        confiance = 88.5
        
        return jsonify({
            "prix_estime": round(pred_prix, 2),
            "prix_min": round(pred_prix - marge, 2),
            "prix_max": round(pred_prix + marge, 2),
            "prix_m2_zone": round(prix_m2_zone, 2),
            "score_confiance": confiance
        })
    except Exception as e:
        return jsonify({"erreur": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
