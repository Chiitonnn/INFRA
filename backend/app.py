import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Configuration sécurisée
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret_key_ymmo_v2')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///local_ymmo.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)

    # Simple route root de l'API
    @app.route('/api/')
    def home_api():
        return jsonify({"message": "Bienvenue sur l'API Ymmo V2", "status": "online"})
    
    # Simple route santé
    @app.route('/api/health')
    def health_check():
        return jsonify({"status": "ok"})
    
    with app.app_context():
        import models
        from routes.auth import auth_bp
        from routes.biens import biens_bp
        
        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        app.register_blueprint(biens_bp, url_prefix='/api/biens')

        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=8000, debug=True)
