#!/bin/bash
echo "Attente de 5s pour laisser le temps à la base éventuelle de démarrer (optionnel)..."
sleep 5

echo "--- Démarrage de l'entraînement IA (Scikit-Learn) ---"
python train.py

echo "--- Démarrage du serveur API ML (Gunicorn) ---"
gunicorn --bind 0.0.0.0:5000 app:app
