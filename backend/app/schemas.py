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

class UserUpdate(BaseModel):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    agence_id: Optional[int] = None
    mot_de_passe: Optional[str] = None

class AgenceBase(BaseModel):
    nom: str
    ville: str
    adresse: str
    telephone: Optional[str] = ""
    email_contact: Optional[str] = ""

class AgenceCreate(AgenceBase):
    pass

class AgenceUpdate(BaseModel):
    nom: Optional[str] = None
    ville: Optional[str] = None
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    email_contact: Optional[str] = None

class Agence(AgenceBase):
    id: int

    class Config:
        orm_mode = True

class BienUpdate(BaseModel):
    titre: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    statut: Optional[str] = None
    prix: Optional[float] = None
    surface_m2: Optional[float] = None
    nb_pieces: Optional[int] = None
    nb_chambres: Optional[int] = None
    etage: Optional[int] = None
    annee_construction: Optional[int] = None
    etat_general: Optional[int] = None
    dpe: Optional[str] = None
    adresse: Optional[str] = None
    ville: Optional[str] = None
    code_postal: Optional[str] = None
    has_garage: Optional[bool] = None
    has_jardin: Optional[bool] = None
    has_piscine: Optional[bool] = None
    agence_id: Optional[int] = None
    agent_id: Optional[int] = None

class EstimationRecord(BaseModel):
    id: int
    user_id: Optional[int] = None
    surface_m2: float
    nb_pieces: int
    type_bien: str
    ville: str
    code_postal: str
    prix_estime: float
    prix_min: float
    prix_max: float
    prix_m2_zone: float
    score_confiance: float
    date_estimation: datetime

    class Config:
        orm_mode = True

class AdminStats(BaseModel):
    total_users: int
    total_agents: int
    total_clients: int
    total_agences: int
    total_biens: int
    biens_vente: int
    biens_vendus: int
    total_contacts: int
    contacts_nouveaux: int
    total_estimations: int
    total_vues: int
