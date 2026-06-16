from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    email: EmailStr
    role: str = "client"
    agence_id: Optional[int] = None

class UserCreate(UserBase):
    mot_de_passe: str

class UserLogin(BaseModel):
    email: EmailStr
    mot_de_passe: str

class User(UserBase):
    id: int
    date_inscription: datetime

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

class BienBase(BaseModel):
    titre: str
    description: Optional[str] = None
    type: str
    statut: str = "vente"
    prix: float
    surface_m2: float
    nb_pieces: int
    nb_chambres: Optional[int] = None
    etage: int = 0
    annee_construction: Optional[int] = None
    etat_general: Optional[int] = None
    dpe: Optional[str] = None
    adresse: str
    ville: str
    code_postal: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    has_garage: bool = False
    has_jardin: bool = False
    has_piscine: bool = False
    agence_id: int
    agent_id: Optional[int] = None

class BienCreate(BienBase):
    pass

class Bien(BienBase):
    id: int
    date_ajout: datetime
    nb_vues: int

    class Config:
        orm_mode = True

class EstimationRequest(BaseModel):
    surface_m2: float
    nb_pieces: int
    type_bien: str
    ville: str
    code_postal: str
    etage: Optional[int] = 0
    annee_construction: Optional[int] = 2000
    etat_general: Optional[int] = 3
    has_garage: bool = False
    has_jardin: bool = False
    has_piscine: bool = False

class EstimationResponse(BaseModel):
    prix_estime: float
    prix_min: float
    prix_max: float
    prix_m2_zone: float
    score_confiance: float

class ContactRequest(BaseModel):
    bien_id: int
    nom: str
    email: EmailStr
    telephone: str
    message: str

class Contact(ContactRequest):
    id: int
    user_id: Optional[int] = None
    statut: str
    date_envoi: datetime

    class Config:
        orm_mode = True
