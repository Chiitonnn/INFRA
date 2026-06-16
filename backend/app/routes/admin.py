from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from ..database import get_db
from .. import models, schemas, auth

router = APIRouter(dependencies=[Depends(auth.require_admin)])


@router.get("/stats", response_model=schemas.AdminStats)
def get_stats(db: Session = Depends(get_db)):
    total_vues = db.query(func.coalesce(func.sum(models.Bien.nb_vues), 0)).scalar() or 0
    return schemas.AdminStats(
        total_users=db.query(models.User).count(),
        total_agents=db.query(models.User).filter(models.User.role == "agent").count(),
        total_clients=db.query(models.User).filter(models.User.role == "client").count(),
        total_agences=db.query(models.Agence).count(),
        total_biens=db.query(models.Bien).count(),
        biens_vente=db.query(models.Bien).filter(models.Bien.statut == "vente").count(),
        biens_vendus=db.query(models.Bien).filter(models.Bien.statut == "vendu").count(),
        total_contacts=db.query(models.Contact).count(),
        contacts_nouveaux=db.query(models.Contact).filter(models.Contact.statut == "nouveau").count(),
        total_estimations=db.query(models.Estimation).count(),
        total_vues=int(total_vues),
    )


@router.get("/users", response_model=List[schemas.User])
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.User).offset(skip).limit(limit).all()


@router.post("/users", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if len(user.mot_de_passe) < 8:
        raise HTTPException(status_code=400, detail="Le mot de passe doit contenir au moins 8 caractères")
    if user.role not in ["client", "agent", "admin"]:
        raise HTTPException(status_code=400, detail="Rôle invalide")
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email déjà utilisé")
    if user.agence_id:
        agence = db.query(models.Agence).filter(models.Agence.id == user.agence_id).first()
        if not agence:
            raise HTTPException(status_code=404, detail="Agence non trouvée")
    db_user = models.User(
        nom=user.nom,
        prenom=user.prenom,
        email=user.email,
        mot_de_passe=auth.get_password_hash(user.mot_de_passe),
        role=user.role,
        agence_id=user.agence_id,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.put("/users/{user_id}", response_model=schemas.User)
def update_user(user_id: int, data: schemas.UserUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.require_admin)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    if data.email and data.email != user.email:
        if db.query(models.User).filter(models.User.email == data.email).first():
            raise HTTPException(status_code=400, detail="Email déjà utilisé")
    if data.role and data.role not in ["client", "agent", "admin"]:
        raise HTTPException(status_code=400, detail="Rôle invalide")
    if user.id == current_user.id and data.role and data.role != "admin":
        raise HTTPException(status_code=400, detail="Impossible de retirer vos propres droits admin")
    update_data = data.dict(exclude_unset=True)
    if "mot_de_passe" in update_data:
        if len(update_data["mot_de_passe"]) < 8:
            raise HTTPException(status_code=400, detail="Le mot de passe doit contenir au moins 8 caractères")
        update_data["mot_de_passe"] = auth.get_password_hash(update_data["mot_de_passe"])
    for field, value in update_data.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.require_admin)):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Impossible de supprimer votre propre compte")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    db.delete(user)
    db.commit()
    return {"message": "Utilisateur supprimé"}


@router.get("/agences", response_model=List[schemas.Agence])
def list_agences(db: Session = Depends(get_db)):
    return db.query(models.Agence).all()


@router.post("/agences", response_model=schemas.Agence)
def create_agence(agence: schemas.AgenceCreate, db: Session = Depends(get_db)):
    db_agence = models.Agence(**agence.dict())
    db.add(db_agence)
    db.commit()
    db.refresh(db_agence)
    return db_agence


@router.put("/agences/{agence_id}", response_model=schemas.Agence)
def update_agence(agence_id: int, data: schemas.AgenceUpdate, db: Session = Depends(get_db)):
    agence = db.query(models.Agence).filter(models.Agence.id == agence_id).first()
    if not agence:
        raise HTTPException(status_code=404, detail="Agence non trouvée")
    for field, value in data.dict(exclude_unset=True).items():
        setattr(agence, field, value)
    db.commit()
    db.refresh(agence)
    return agence


@router.delete("/agences/{agence_id}")
def delete_agence(agence_id: int, db: Session = Depends(get_db)):
    agence = db.query(models.Agence).filter(models.Agence.id == agence_id).first()
    if not agence:
        raise HTTPException(status_code=404, detail="Agence non trouvée")
    linked_users = db.query(models.User).filter(models.User.agence_id == agence_id).count()
    linked_biens = db.query(models.Bien).filter(models.Bien.agence_id == agence_id).count()
    if linked_users or linked_biens:
        raise HTTPException(status_code=400, detail="Agence liée à des utilisateurs ou biens")
    db.delete(agence)
    db.commit()
    return {"message": "Agence supprimée"}


@router.get("/biens", response_model=List[schemas.Bien])
def list_all_biens(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Bien).offset(skip).limit(limit).all()


@router.put("/biens/{bien_id}", response_model=schemas.Bien)
def update_bien(bien_id: int, data: schemas.BienUpdate, db: Session = Depends(get_db)):
    bien = db.query(models.Bien).filter(models.Bien.id == bien_id).first()
    if not bien:
        raise HTTPException(status_code=404, detail="Bien non trouvé")
    for field, value in data.dict(exclude_unset=True).items():
        setattr(bien, field, value)
    db.commit()
    db.refresh(bien)
    return bien


@router.delete("/biens/{bien_id}")
def delete_bien(bien_id: int, db: Session = Depends(get_db)):
    bien = db.query(models.Bien).filter(models.Bien.id == bien_id).first()
    if not bien:
        raise HTTPException(status_code=404, detail="Bien non trouvé")
    db.query(models.Contact).filter(models.Contact.bien_id == bien_id).delete()
    db.query(models.Photo).filter(models.Photo.bien_id == bien_id).delete()
    db.delete(bien)
    db.commit()
    return {"message": "Bien supprimé"}


@router.get("/contacts", response_model=List[schemas.Contact])
def list_all_contacts(skip: int = 0, limit: int = 100, statut: str = None, db: Session = Depends(get_db)):
    query = db.query(models.Contact)
    if statut:
        query = query.filter(models.Contact.statut == statut)
    return query.offset(skip).limit(limit).all()


@router.get("/estimations", response_model=List[schemas.EstimationRecord])
def list_estimations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Estimation).order_by(models.Estimation.date_estimation.desc()).offset(skip).limit(limit).all()
