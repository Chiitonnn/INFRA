from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from .. import models, schemas, auth

router = APIRouter()

@router.get("/", response_model=List[schemas.Bien])
def list_biens(
    skip: int = 0,
    limit: int = 20,
    ville: Optional[str] = None,
    type_bien: Optional[str] = None,
    prix_min: Optional[float] = None,
    prix_max: Optional[float] = None,
    surface_min: Optional[float] = None,
    surface_max: Optional[float] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Bien)
    if ville:
        query = query.filter(models.Bien.ville == ville)
    if type_bien:
        query = query.filter(models.Bien.type == type_bien)
    if prix_min:
        query = query.filter(models.Bien.prix >= prix_min)
    if prix_max:
        query = query.filter(models.Bien.prix <= prix_max)
    if surface_min:
        query = query.filter(models.Bien.surface_m2 >= surface_min)
    if surface_max:
        query = query.filter(models.Bien.surface_m2 <= surface_max)
    return query.offset(skip).limit(limit).all()

@router.get("/{bien_id}", response_model=schemas.Bien)
def get_bien(bien_id: int, db: Session = Depends(get_db)):
    bien = db.query(models.Bien).filter(models.Bien.id == bien_id).first()
    if not bien:
        raise HTTPException(status_code=404, detail="Bien non trouvé")
    bien.nb_vues += 1
    db.commit()
    return bien

@router.post("/", response_model=schemas.Bien)
def create_bien(bien: schemas.BienCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if current_user.role not in ["agent", "admin"]:
        raise HTTPException(status_code=403, detail="Seul un agent peut créer un bien")
    db_bien = models.Bien(**bien.dict())
    db.add(db_bien)
    db.commit()
    db.refresh(db_bien)
    return db_bien