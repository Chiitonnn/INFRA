from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import httpx
import os
from ..database import get_db
from .. import models, schemas

router = APIRouter()

ML_URL = os.getenv("ML_URL", "http://ymmo_ml:5000")

@router.post("/predict", response_model=schemas.EstimationResponse)
async def predict_estimation(data: schemas.EstimationRequest, db: Session = Depends(get_db)):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{ML_URL}/predict", json=data.dict(), timeout=10.0)
            response.raise_for_status()
            result = response.json()
            
            # Sauvegarder l'estimation en DB
            estimation = models.Estimation(
                surface_m2=data.surface_m2,
                nb_pieces=data.nb_pieces,
                type_bien=data.type_bien,
                ville=data.ville,
                code_postal=data.code_postal,
                etat_general=data.etat_general,
                has_garage=data.has_garage,
                has_jardin=data.has_jardin,
                has_piscine=data.has_piscine,
                prix_estime=result["prix_estime"],
                prix_min=result["prix_min"],
                prix_max=result["prix_max"],
                prix_m2_zone=result["prix_m2_zone"],
                score_confiance=result["score_confiance"]
            )
            db.add(estimation)
            db.commit()
            
            return result
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="Service d'estimation indisponible")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"Erreur du service d'estimation: {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'estimation: {str(e)}")
