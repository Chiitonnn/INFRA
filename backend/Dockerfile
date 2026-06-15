FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Variables d'environnement standard pour Flask
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Commande de lancement Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:create_app()"]
