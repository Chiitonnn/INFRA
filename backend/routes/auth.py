from flask import Blueprint, request, jsonify
from models import User, db
from datetime import datetime

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({"error": "Données incomplètes."}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Cet email existe déjà."}), 409
        
    user = User(
        nom=data.get('nom'),
        prenom=data.get('prenom'),
        email=data['email'],
        role=data.get('role', 'client')
    )
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "Compte créé.", "user_id": user.id}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data.get('email')).first()
    if user and user.check_password(data.get('password')):
        user.derniere_connexion = datetime.utcnow()
        db.session.commit()
        # Simulation basique d'une session sans librairies tierces complexes
        return jsonify({"message": "Connexion réussie.", "role": user.role, "user_id": user.id}), 200
    return jsonify({"error": "Identifiants invalides."}), 401
