import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import os
import matplotlib.pyplot as plt
import seaborn as sns

def generate_data(n=2000):
    villes = ['Aix-en-Provence', 'Marseille', 'Paris', 'Lyon']
    prix_villes = {'Aix-en-Provence': 4500, 'Marseille': 3200, 'Paris': 10500, 'Lyon': 5100}
    
    data = []
    for _ in range(n):
        v = np.random.choice(villes)
        s = np.random.normal(80, 40)
        s = max(15, s)
        t = np.random.choice(['maison', 'appartement', 'commerce'])
        
        # Création d'un prix logique avec du bruit
        p = s * prix_villes[v]
        p *= 1.2 if t == 'maison' else 1.0
        p *= np.random.normal(1.0, 0.15)
        
        data.append({
            'surface_m2': s,
            'nb_pieces': max(1, int(s / 25)),
            'type_bien': t,
            'ville': v,
            'code_postal': 13100 if v == 'Aix-en-Provence' else 75000,
            'etage': np.random.randint(0, 5),
            'annee_construction': np.random.randint(1950, 2023),
            'etat_general': np.random.randint(1, 6),
            'has_garage': np.random.choice([True, False]),
            'has_jardin': np.random.choice([True, False]) if t == 'maison' else False,
            'has_piscine': np.random.choice([True, False], p=[0.1, 0.9]),
            'prix_vente': p
        })
    df = pd.DataFrame(data)
    
    # Nettoyage selon le brief (outliers < 10000 ou > 5000000)
    df.loc[np.random.choice(df.index, 5), 'prix_vente'] = 5000
    df.loc[np.random.choice(df.index, 5), 'prix_vente'] = 8000000
    return df

def train_and_export():
    df = generate_data()
    print(f"Lignes avant nettoyage = {len(df)}")
    df = df[(df['prix_vente'] >= 10000) & (df['prix_vente'] <= 5000000)]
    print(f"Lignes après nettoyage : {len(df)}")
    
    X = df.drop('prix_vente', axis=1)
    y = df['prix_vente']
    
    num_f = ['surface_m2', 'nb_pieces', 'code_postal', 'etage', 'annee_construction', 'etat_general']
    cat_f = ['type_bien', 'ville']
    bool_f = ['has_garage', 'has_jardin', 'has_piscine']
    
    preprocessor = ColumnTransformer([
        ('num', Pipeline([('imputer', SimpleImputer(strategy='median')), ('scaler', StandardScaler())]), num_f),
        ('cat', Pipeline([('imputer', SimpleImputer(strategy='most_frequent')), ('ohe', OneHotEncoder(handle_unknown='ignore'))]), cat_f),
        ('bool', SimpleImputer(strategy='constant', fill_value=False), bool_f)
    ])
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    
    models = {
        'LinearReg': LinearRegression(),
        'RandomForest': RandomForestRegressor(n_estimators=50),
        'GradientBoosting': GradientBoostingRegressor(n_estimators=50)
    }
    
    best_pipe, best_r2, best_name = None, -float('inf'), ""
    
    for name, m in models.items():
        pipe = Pipeline([('prep', preprocessor), ('model', m)])
        pipe.fit(X_train, y_train)
        preds = pipe.predict(X_test)
        r2 = r2_score(y_test, preds)
        mae = mean_absolute_error(y_test, preds)
        print(f"Modèle {name} : R2 {r2:.3f} | MAE {mae:.0f} €")
        if r2 > best_r2:
            best_r2, best_pipe, best_name = r2, pipe, name
            
    print(f"Meilleur modèle : {best_name}")
    joblib.dump(best_pipe, "best_model.pkl")
    
    # Reports PNG simples
    os.makedirs('static', exist_ok=True)
    
    plt.figure(figsize=(8,5))
    sns.boxplot(x='type_bien', y='prix_vente', data=df)
    plt.savefig('static/prix_type.png')
    plt.close()

if __name__ == '__main__':
    train_and_export()
