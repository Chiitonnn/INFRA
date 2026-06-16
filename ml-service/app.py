from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import pandas as pd
import numpy as np
import joblib
import os
from model import PriceEstimator

app = FastAPI(title="Ymmo ML Service", version="1.0")

# Charger le modèle
model_path = "models/"
estimator = PriceEstimator()

try:
    estimator.load(model_path)
    print("✅ Modèle chargé avec succès")
except:
    print("⚠️ Aucun modèle trouvé, entraînement en cours...")
    from train import main as train_model
    train_model()
    estimator.load(model_path)

class EstimationRequest(BaseModel):
    surface_m2: float
    nb_pieces: int
    type_bien: str
    ville: str
    code_postal: str
    etage: Optional[int] = 0
    annee_construction: Optional[int] = 2000
    etat_general: Optional[int] = 3
    has_garage: Optional[bool] = False
    has_jardin: Optional[bool] = False
    has_piscine: Optional[bool] = False

class EstimationResponse(BaseModel):
    prix_estime: float
    prix_min: float
    prix_max: float
    prix_m2_zone: float
    score_confiance: float

@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": estimator.is_trained}

@app.get("/stats")
def stats():
    """Statistiques globales du modèle"""
    return {
        "model_type": estimator.model.__class__.__name__ if estimator.model else None,
        "is_trained": estimator.is_trained,
        "features": estimator.features if estimator.features else None
    }

@app.post("/predict", response_model=EstimationResponse)
def predict(data: EstimationRequest):
    try:
        features_dict = data.dict()
        result = estimator.predict(features_dict)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de prédiction: {str(e)}")

@app.post("/predict/batch")
def predict_batch(requests: list[EstimationRequest]):
    """Prédiction en batch pour plusieurs biens"""
    results = []
    for req in requests:
        try:
            result = estimator.predict(req.dict())
            results.append(result)
        except Exception as e:
            results.append({"error": str(e)})
    return {"results": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)