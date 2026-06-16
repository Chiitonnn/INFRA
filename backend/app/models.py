from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100))
    prenom = Column(String(100))
    email = Column(String(255), unique=True, index=True)
    mot_de_passe = Column(String(255))
    role = Column(String(50), default="client")
    agence_id = Column(Integer, ForeignKey("agences.id"), nullable=True)
    date_inscription = Column(DateTime, default=datetime.utcnow)
    derniere_connexion = Column(DateTime, nullable=True)

class Agence(Base):
    __tablename__ = "agences"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100))
    ville = Column(String(100))
    adresse = Column(String(255))
    telephone = Column(String(20))
    email_contact = Column(String(255))

class Bien(Base):
    __tablename__ = "biens"
    id = Column(Integer, primary_key=True, index=True)
    titre = Column(String(255))
    description = Column(Text)
    type = Column(String(50))
    statut = Column(String(50), default="vente")
    prix = Column(Float)
    surface_m2 = Column(Float)
    nb_pieces = Column(Integer)
    nb_chambres = Column(Integer)
    etage = Column(Integer, default=0)
    annee_construction = Column(Integer, nullable=True)
    etat_general = Column(Integer, nullable=True)
    dpe = Column(String(5), nullable=True)
    adresse = Column(String(255))
    ville = Column(String(100))
    code_postal = Column(String(10))
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    has_garage = Column(Boolean, default=False)
    has_jardin = Column(Boolean, default=False)
    has_piscine = Column(Boolean, default=False)
    agence_id = Column(Integer, ForeignKey("agences.id"))
    agent_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    date_ajout = Column(DateTime, default=datetime.utcnow)
    date_modification = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    nb_vues = Column(Integer, default=0)

class Photo(Base):
    __tablename__ = "photos"
    id = Column(Integer, primary_key=True, index=True)
    bien_id = Column(Integer, ForeignKey("biens.id"))
    url = Column(String(255))
    ordre = Column(Integer, default=0)
    date_ajout = Column(DateTime, default=datetime.utcnow)

class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True, index=True)
    bien_id = Column(Integer, ForeignKey("biens.id"))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    nom = Column(String(100))
    email = Column(String(255))
    telephone = Column(String(20))
    message = Column(Text)
    statut = Column(String(50), default="nouveau")
    date_envoi = Column(DateTime, default=datetime.utcnow)

class Estimation(Base):
    __tablename__ = "estimations"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    surface_m2 = Column(Float)
    nb_pieces = Column(Integer)
    type_bien = Column(String(50))
    ville = Column(String(100))
    code_postal = Column(String(10))
    etat_general = Column(Integer, nullable=True)
    has_garage = Column(Boolean, default=False)
    has_jardin = Column(Boolean, default=False)
    has_piscine = Column(Boolean, default=False)
    prix_estime = Column(Float)
    prix_min = Column(Float)
    prix_max = Column(Float)
    prix_m2_zone = Column(Float)
    score_confiance = Column(Float)
    date_estimation = Column(DateTime, default=datetime.utcnow)