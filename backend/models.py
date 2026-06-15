from datetime import datetime
from app import db
import bcrypt

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100))
    prenom = db.Column(db.String(100))
    email = db.Column(db.String(150), unique=True, nullable=False)
    mot_de_passe = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='client') # 'client', 'agent', 'admin'
    agence_id = db.Column(db.Integer, db.ForeignKey('agences.id'), nullable=True)
    date_inscription = db.Column(db.DateTime, default=datetime.utcnow)
    derniere_connexion = db.Column(db.DateTime, nullable=True)

    def set_password(self, password):
        self.mot_de_passe = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.mot_de_passe.encode('utf-8'))


class Agence(db.Model):
    __tablename__ = 'agences'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(150), nullable=False)
    ville = db.Column(db.String(100))
    adresse = db.Column(db.Text)
    telephone = db.Column(db.String(20))
    email_contact = db.Column(db.String(150))
    responsable = db.Column(db.String(100))
    users = db.relationship('User', backref='agence')


class Bien(db.Model):
    __tablename__ = 'biens'
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    type = db.Column(db.String(50)) # maison, appartement, commerce
    statut = db.Column(db.String(50), default='vente') # vente, location, vendu
    prix = db.Column(db.Float)
    surface_m2 = db.Column(db.Float)
    nb_pieces = db.Column(db.Integer)
    nb_chambres = db.Column(db.Integer)
    etage = db.Column(db.Integer, default=0)
    annee_construction = db.Column(db.Integer)
    etat_general = db.Column(db.Integer) # 1 à 5
    dpe = db.Column(db.String(2)) # A à G
    adresse = db.Column(db.Text)
    ville = db.Column(db.String(100))
    code_postal = db.Column(db.String(20))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    has_garage = db.Column(db.Boolean, default=False)
    has_jardin = db.Column(db.Boolean, default=False)
    has_piscine = db.Column(db.Boolean, default=False)
    agence_id = db.Column(db.Integer, db.ForeignKey('agences.id'))
    agent_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    date_ajout = db.Column(db.DateTime, default=datetime.utcnow)
    date_modification = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    nb_vues = db.Column(db.Integer, default=0)
    
    photos = db.relationship('Photo', backref='bien', cascade="all, delete")


class Photo(db.Model):
    __tablename__ = 'photos'
    id = db.Column(db.Integer, primary_key=True)
    bien_id = db.Column(db.Integer, db.ForeignKey('biens.id'))
    url = db.Column(db.String(255), nullable=False)
    ordre = db.Column(db.Integer, default=0)
    date_ajout = db.Column(db.DateTime, default=datetime.utcnow)


class Contact(db.Model):
    __tablename__ = 'contacts'
    id = db.Column(db.Integer, primary_key=True)
    bien_id = db.Column(db.Integer, db.ForeignKey('biens.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    nom = db.Column(db.String(150))
    email = db.Column(db.String(150))
    telephone = db.Column(db.String(20))
    message = db.Column(db.Text)
    statut = db.Column(db.String(50), default='nouveau') # nouveau, lu, traite
    date_envoi = db.Column(db.DateTime, default=datetime.utcnow)


class Estimation(db.Model):
    __tablename__ = 'estimations'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    surface_m2 = db.Column(db.Float)
    nb_pieces = db.Column(db.Integer)
    type_bien = db.Column(db.String(50))
    ville = db.Column(db.String(100))
    code_postal = db.Column(db.String(20))
    etat_general = db.Column(db.Integer)
    has_garage = db.Column(db.Boolean, default=False)
    has_jardin = db.Column(db.Boolean, default=False)
    has_piscine = db.Column(db.Boolean, default=False)
    prix_estime = db.Column(db.Float)
    prix_min = db.Column(db.Float)
    prix_max = db.Column(db.Float)
    prix_m2_zone = db.Column(db.Float)
    score_confiance = db.Column(db.Float)
    date_estimation = db.Column(db.DateTime, default=datetime.utcnow)
