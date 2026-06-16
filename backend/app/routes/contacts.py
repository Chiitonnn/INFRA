from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas, auth
from typing import List

router = APIRouter()

@router.post("/", response_model=schemas.Contact)
def create_contact(
    contact: schemas.ContactRequest,
    db: Session = Depends(get_db)
):
    """Créer un nouveau message de contact pour un bien"""
    # Vérifier que le bien existe
    bien = db.query(models.Bien).filter(models.Bien.id == contact.bien_id).first()
    if not bien:
        raise HTTPException(status_code=404, detail="Bien non trouvé")
    
    db_contact = models.Contact(
        bien_id=contact.bien_id,
        nom=contact.nom,
        email=contact.email,
        telephone=contact.telephone,
        message=contact.message,
        statut="nouveau"
    )
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

@router.get("/", response_model=List[schemas.Contact])
def list_contacts(
    skip: int = 0,
    limit: int = 50,
    statut: str = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Liste des contacts (agent uniquement)"""
    if current_user.role not in ["agent", "admin"]:
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    query = db.query(models.Contact)
    if statut:
        query = query.filter(models.Contact.statut == statut)
    return query.offset(skip).limit(limit).all()

@router.get("/{contact_id}", response_model=schemas.Contact)
def get_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Obtenir un contact spécifique"""
    if current_user.role not in ["agent", "admin"]:
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    contact = db.query(models.Contact).filter(models.Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact non trouvé")
    return contact

@router.put("/{contact_id}/statut", response_model=schemas.Contact)
def update_contact_statut(
    contact_id: int,
    statut: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Mettre à jour le statut d'un contact (lu/traité)"""
    if current_user.role not in ["agent", "admin"]:
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    contact = db.query(models.Contact).filter(models.Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact non trouvé")
    
    if statut not in ["nouveau", "lu", "traite"]:
        raise HTTPException(status_code=400, detail="Statut invalide")
    
    contact.statut = statut
    db.commit()
    db.refresh(contact)
    return contact