import os
from sqlalchemy.orm import Session
from . import models, auth

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@ymmo.fr")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "AdminYmmo2026!")

AGENCES = [
    {"nom": "Ymmo Siège", "ville": "Aix-en-Provence", "adresse": "12 Cours Mirabeau", "telephone": "04 42 00 00 00", "email_contact": "siege@ymmo.fr"},
    {"nom": "Ymmo Paris", "ville": "Paris", "adresse": "45 Avenue des Champs-Élysées", "telephone": "01 42 00 00 01", "email_contact": "paris@ymmo.fr"},
    {"nom": "Ymmo Lyon", "ville": "Lyon", "adresse": "8 Place Bellecour", "telephone": "04 78 00 00 02", "email_contact": "lyon@ymmo.fr"},
    {"nom": "Ymmo Marseille", "ville": "Marseille", "adresse": "22 La Canebière", "telephone": "04 91 00 00 03", "email_contact": "marseille@ymmo.fr"},
    {"nom": "Ymmo Bordeaux", "ville": "Bordeaux", "adresse": "5 Place de la Bourse", "telephone": "05 56 00 00 04", "email_contact": "bordeaux@ymmo.fr"},
    {"nom": "Ymmo Toulouse", "ville": "Toulouse", "adresse": "10 Place du Capitole", "telephone": "05 61 00 00 05", "email_contact": "toulouse@ymmo.fr"},
    {"nom": "Ymmo Nantes", "ville": "Nantes", "adresse": "3 Place Royale", "telephone": "02 40 00 00 06", "email_contact": "nantes@ymmo.fr"},
    {"nom": "Ymmo Lille", "ville": "Lille", "adresse": "18 Grand Place", "telephone": "03 20 00 00 07", "email_contact": "lille@ymmo.fr"},
    {"nom": "Ymmo Nice", "ville": "Nice", "adresse": "7 Promenade des Anglais", "telephone": "04 93 00 00 08", "email_contact": "nice@ymmo.fr"},
    {"nom": "Ymmo Strasbourg", "ville": "Strasbourg", "adresse": "2 Place Kléber", "telephone": "03 88 00 00 09", "email_contact": "strasbourg@ymmo.fr"},
    {"nom": "Ymmo Montpellier", "ville": "Montpellier", "adresse": "14 Place de la Comédie", "telephone": "04 67 00 00 10", "email_contact": "montpellier@ymmo.fr"},
    {"nom": "Ymmo Rennes", "ville": "Rennes", "adresse": "6 Place des Lices", "telephone": "02 99 00 00 11", "email_contact": "rennes@ymmo.fr"},
    {"nom": "Ymmo Grenoble", "ville": "Grenoble", "adresse": "9 Place Grenette", "telephone": "04 76 00 00 12", "email_contact": "grenoble@ymmo.fr"},
]


def seed_data(db: Session):
    if db.query(models.Agence).count() == 0:
        for agence_data in AGENCES:
            db.add(models.Agence(**agence_data))
        db.commit()

    admin = db.query(models.User).filter(models.User.email == ADMIN_EMAIL).first()
    if not admin:
        siege = db.query(models.Agence).filter(models.Agence.nom == "Ymmo Siège").first()
        admin = models.User(
            nom="Admin",
            prenom="Ymmo",
            email=ADMIN_EMAIL,
            mot_de_passe=auth.get_password_hash(ADMIN_PASSWORD),
            role="admin",
            agence_id=siege.id if siege else None,
        )
        db.add(admin)
        db.commit()

    if db.query(models.Bien).count() == 0:
        siege = db.query(models.Agence).filter(models.Agence.nom == "Ymmo Siège").first()
        admin_user = db.query(models.User).filter(models.User.email == ADMIN_EMAIL).first()
        bien = models.Bien(
            titre="Appartement Test",
            description="Ceci est un appartement test intégré par défaut.",
            type="appartement",
            statut="vente",
            prix=250000.0,
            surface_m2=75.0,
            nb_pieces=3,
            nb_chambres=2,
            ville="Aix-en-Provence",
            code_postal="13100",
            adresse="12 Cours Mirabeau",
            agence_id=siege.id if siege else None,
            agent_id=admin_user.id if admin_user else None
        )
        db.add(bien)
        db.commit()
