import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import os
import warnings
warnings.filterwarnings('ignore')

class PriceEstimator:
    """Modèle d'estimation des prix immobiliers"""
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.le_type = None
        self.le_ville = None
        self.features = [
            "surface_m2", "nb_pieces", "type_bien_encoded", "ville_encoded",
            "etage", "annee_construction", "etat_general", "has_garage",
            "has_jardin", "has_piscine"
        ]
        self.is_trained = False
    
    def generate_data(self, n_samples=5000):
        """Génère un dataset synthétique réaliste pour l'entraînement"""
        np.random.seed(42)
        
        villes = ["Aix-en-Provence", "Marseille", "Lyon", "Paris", "Bordeaux", 
                  "Toulouse", "Nice", "Nantes", "Strasbourg", "Montpellier",
                  "Lille", "Rennes", "Reims", "Saint-Étienne", "Toulon"]
        
        type_bien = ["maison", "appartement", "commerce"]
        
        # Prix de base par ville (€/m²)
        prix_base = {
            "Paris": 8500, "Aix-en-Provence": 4800, "Marseille": 3600,
            "Lyon": 5000, "Bordeaux": 4500, "Toulouse": 4000,
            "Nice": 5500, "Nantes": 3700, "Strasbourg": 3800, 
            "Montpellier": 4200, "Lille": 3800, "Rennes": 3500,
            "Reims": 3200, "Saint-Étienne": 2500, "Toulon": 3900
        }
        
        type_factors = {"maison": 1.1, "appartement": 1.0, "commerce": 1.3}
        
        data = {
            "surface_m2": np.random.uniform(25, 300, n_samples),
            "nb_pieces": np.random.randint(1, 12, n_samples),
            "type_bien": np.random.choice(type_bien, n_samples),
            "ville": np.random.choice(villes, n_samples),
            "code_postal": np.random.randint(10000, 95000, n_samples),
            "etage": np.random.randint(0, 20, n_samples),
            "annee_construction": np.random.randint(1850, 2025, n_samples),
            "etat_general": np.random.randint(1, 6, n_samples),
            "has_garage": np.random.choice([True, False], n_samples, p=[0.35, 0.65]),
            "has_jardin": np.random.choice([True, False], n_samples, p=[0.45, 0.55]),
            "has_piscine": np.random.choice([True, False], n_samples, p=[0.12, 0.88])
        }
        
        df = pd.DataFrame(data)
        
        # Calcul du prix au m²
        df["prix_m2_base"] = df["ville"].map(prix_base) * df["type_bien"].map(type_factors)
        df["prix_m2_base"] = df["prix_m2_base"].fillna(3500)  # fallback
        
        # Ajustements
        df["prix_m2"] = df["prix_m2_base"] * \
                       (1 + (df["etat_general"] - 3) * 0.06) * \
                       (1 + df["surface_m2"] / 1500) * \
                       (1 + df["has_garage"] * 0.06) * \
                       (1 + df["has_jardin"] * 0.04) * \
                       (1 + df["has_piscine"] * 0.10) * \
                       np.random.normal(1, 0.12, len(df))
        
        # Prix total
        df["prix"] = df["surface_m2"] * df["prix_m2"] + np.random.normal(0, 15000, len(df))
        df["prix"] = df["prix"].clip(lower=30000, upper=3000000)
        df["prix_m2"] = df["prix"] / df["surface_m2"]
        
        return df.drop(["prix_m2", "prix_m2_base"], axis=1)
    
    def train(self, df=None):
        """Entraîne le modèle sur les données"""
        print("📊 Génération des données d'entraînement...")
        if df is None:
            df = self.generate_data(5000)
        
        print("🔍 Nettoyage des données...")
        df = df.dropna()
        df = df[df["prix"] > 10000]
        df = df[df["prix"] < 5000000]
        
        print("🏷️ Encodage des variables catégorielles...")
        self.le_type = LabelEncoder()
        self.le_ville = LabelEncoder()
        df["type_bien_encoded"] = self.le_type.fit_transform(df["type_bien"])
        df["ville_encoded"] = self.le_ville.fit_transform(df["ville"])
        
        X = df[self.features]
        y = df["prix"]
        
        print("📈 Split train/test...")
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        print("🔧 Normalisation...")
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        print("🤖 Entraînement des modèles...")
        models = {
            "RandomForest": RandomForestRegressor(n_estimators=150, max_depth=20, random_state=42),
            "GradientBoosting": GradientBoostingRegressor(n_estimators=150, learning_rate=0.08, random_state=42),
            "LinearRegression": LinearRegression()
        }
        
        best_model = None
        best_r2 = -float('inf')
        best_mae = float('inf')
        
        for name, model in models.items():
            scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring='r2')
            model.fit(X_train_scaled, y_train)
            y_pred = model.predict(X_test_scaled)
            
            r2 = r2_score(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            
            print(f"  {name}:")
            print(f"    R² = {r2:.4f} (CV: {scores.mean():.4f} ± {scores.std():.4f})")
            print(f"    MAE = {mae:,.0f} €")
            print(f"    RMSE = {rmse:,.0f} €")
            
            if r2 > best_r2:
                best_r2 = r2
                best_mae = mae
                best_model = model
        
        self.model = best_model
        self.is_trained = True
        
        print(f"✅ Meilleur modèle: {best_model.__class__.__name__}")
        print(f"   R² = {best_r2:.4f}, MAE = {best_mae:,.0f} €")
        
        return self
    
    def predict(self, features_dict):
        """Prédit le prix pour une nouvelle entrée"""
        if not self.is_trained or self.model is None:
            raise ValueError("Le modèle doit être entraîné avant de faire des prédictions")
        
        # Préparer les données
        type_encoded = self.le_type.transform([features_dict["type_bien"]])[0]
        ville_encoded = self.le_ville.transform([features_dict["ville"]])[0]
        
        input_data = np.array([[
            features_dict["surface_m2"],
            features_dict["nb_pieces"],
            type_encoded,
            ville_encoded,
            features_dict.get("etage", 0),
            features_dict.get("annee_construction", 2000),
            features_dict.get("etat_general", 3),
            int(features_dict.get("has_garage", False)),
            int(features_dict.get("has_jardin", False)),
            int(features_dict.get("has_piscine", False))
        ]])
        
        # Normaliser et prédire
        input_scaled = self.scaler.transform(input_data)
        prix_estime = self.model.predict(input_scaled)[0]
        
        # Fourchette d'estimation (basée sur l'erreur du modèle)
        marge = 0.15  # 15% de marge
        prix_min = prix_estime * (1 - marge)
        prix_max = prix_estime * (1 + marge)
        prix_m2_zone = prix_estime / features_dict["surface_m2"]
        
        return {
            "prix_estime": round(float(prix_estime), 2),
            "prix_min": round(float(prix_min), 2),
            "prix_max": round(float(prix_max), 2),
            "prix_m2_zone": round(float(prix_m2_zone), 2),
            "score_confiance": 0.85
        }
    
    def save(self, path="models/"):
        """Sauvegarde le modèle et ses encodeurs"""
        os.makedirs(path, exist_ok=True)
        joblib.dump(self.model, f"{path}/model.pkl")
        joblib.dump(self.scaler, f"{path}/scaler.pkl")
        joblib.dump(self.le_type, f"{path}/le_type.pkl")
        joblib.dump(self.le_ville, f"{path}/le_ville.pkl")
        joblib.dump(self.features, f"{path}/features.pkl")
        print(f"✅ Modèle sauvegardé dans {path}")
    
    def load(self, path="models/"):
        """Charge un modèle sauvegardé"""
        self.model = joblib.load(f"{path}/model.pkl")
        self.scaler = joblib.load(f"{path}/scaler.pkl")
        self.le_type = joblib.load(f"{path}/le_type.pkl")
        self.le_ville = joblib.load(f"{path}/le_ville.pkl")
        self.features = joblib.load(f"{path}/features.pkl")
        self.is_trained = True
        print("✅ Modèle chargé avec succès")
        return self