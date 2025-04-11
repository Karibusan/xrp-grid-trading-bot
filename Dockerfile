# Étape 1 : Base Python moderne & légère
FROM python:3.11-slim

# Étape 2 : Répertoire de travail
WORKDIR /app

# Étape 3 : Dépendances Python
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Étape 4 : Copier le code source
COPY src/ ./src/
COPY config/ ./config/
COPY scripts/ ./scripts/
COPY config.json .  # Si encore utilisé pour fallback manuel

# Étape 5 : Configuration runtime
ENV PYTHONUNBUFFERED=1

# Étape 6 : Point d’entrée
CMD ["python", "src/main.py"]

# Étape 7 : Labeling (meta-infos)
LABEL version="3.1.0-dev"
LABEL description="XRP Grid Trading Bot refactoré pour .env + Docker + Synology"
LABEL maintainer="Karibusan"
