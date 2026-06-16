from model import PriceEstimator
import pandas as pd
import os

def main():
    print("🚀 Entraînement du modèle d'estimation Ymmo")
    print("=" * 50)
    
    estimator = PriceEstimator()
    
    # Générer et entraîner
    estimator.train()
    
    # Sauvegarder le modèle
    estimator.save()
    
    print("\n✅ Entraînement terminé avec succès !")
    
    # Tester une prédiction
    test_input = {
        "surface_m2": 75,
        "nb_pieces": 3,
        "type_bien": "appartement",
        "ville": "Lyon",
        "etage": 2,
        "annee_construction": 2010,
        "etat_general": 4,
        "has_garage": True,
        "has_jardin": False,
        "has_piscine": False
    }
    
    result = estimator.predict(test_input)
    print("\n📊 Test de prédiction:")
    print(f"  Surface: {test_input['surface_m2']} m²")
    print(f"  Type: {test_input['type_bien']}")
    print(f"  Ville: {test_input['ville']}")
    print(f"  Prix estimé: {result['prix_estime']:,.0f} €")
    print(f"  Fourchette: {result['prix_min']:,.0f} - {result['prix_max']:,.0f} €")
    print(f"  Prix/m²: {result['prix_m2_zone']:,.0f} €/m²")

if __name__ == "__main__":
    main()