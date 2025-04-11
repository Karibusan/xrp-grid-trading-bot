# Étape 1 : Base Python légère et moderne
FROM python:3.11-slim

# Étape 2 : Définir le répertoire de travail
WORKDIR /app

# Étape 3 : Copier les fichiers requis
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Étape 4 : Copier les sources et la config
COPY src/ ./src/
COPY config/ ./config/
COPY scripts/ ./scripts/
COPY config.json .  # toujours utile pour fallback/override

# Étape 5 : Variables d’environnement
ENV PYTHONUNBUFFERED=1

# Étape 6 : Point d’entrée
CMD ["python", "src/main.py"]

# Étape 7 : Labels (optionnel)
LABEL version="3.1.0-dev"
LABEL description="XRP Grid Trading Bot — refacto .env + config loader + optimisations Docker"
LABEL maintainer="Karibusan"
