#!/bin/bash
# Script de déploiement sur Synology NAS pour le Bot de Trading XRP v3.0

# Définition des variables
NAS_IP="${1:-192.168.1.100}"  # Adresse IP du NAS (par défaut: 192.168.1.100)
NAS_USER="${2:-admin}"        # Utilisateur du NAS (par défaut: admin)
NAS_DIR="${3:-/volume1/docker/xrp_bot}"  # Répertoire de destination sur le NAS
LOCAL_DIR="$(pwd)"            # Répertoire local du bot

# Vérification des arguments
if [ "$#" -lt 1 ]; then
  echo "Usage: $0 [NAS_IP] [NAS_USER] [NAS_DIR]"
  echo "  NAS_IP    : Adresse IP du NAS Synology (défaut: 192.168.1.100)"
  echo "  NAS_USER  : Nom d'utilisateur du NAS (défaut: admin)"
  echo "  NAS_DIR   : Répertoire de destination sur le NAS (défaut: /volume1/docker/xrp_bot)"
  echo ""
  echo "Exemple: $0 192.168.1.100 admin /volume1/docker/xrp_bot"
  
  # Demander confirmation pour utiliser les valeurs par défaut
  read -p "Voulez-vous continuer avec les valeurs par défaut? (o/n): " confirm
  if [[ "$confirm" != "o" && "$confirm" != "O" ]]; then
    exit 1
  fi
fi

echo "=== Déploiement du Bot de Trading XRP v3.0 sur Synology NAS ==="
echo "NAS IP       : $NAS_IP"
echo "NAS User     : $NAS_USER"
echo "NAS Directory: $NAS_DIR"
echo "Local Source : $LOCAL_DIR"
echo ""

# Vérification de la connexion SSH
echo "Vérification de la connexion SSH au NAS..."
ssh -q "$NAS_USER@$NAS_IP" exit
if [ $? -ne 0 ]; then
  echo "Erreur: Impossible de se connecter au NAS via SSH."
  echo "Veuillez vérifier l'adresse IP, le nom d'utilisateur et que SSH est activé sur le NAS."
  exit 1
fi
echo "Connexion SSH établie avec succès."

# Création du répertoire de destination sur le NAS
echo "Création du répertoire de destination sur le NAS..."
ssh "$NAS_USER@$NAS_IP" "mkdir -p $NAS_DIR"

# Synchronisation des fichiers
echo "Synchronisation des fichiers vers le NAS..."
rsync -avz --progress \
  --exclude '.git/' \
  --exclude 'venv/' \
  --exclude '__pycache__/' \
  --exclude '*.pyc' \
  --exclude 'logs/*' \
  --exclude 'data/*' \
  --exclude 'backups/*' \
  "$LOCAL_DIR/" "$NAS_USER@$NAS_IP:$NAS_DIR/"

if [ $? -ne 0 ]; then
  echo "Erreur lors de la synchronisation des fichiers."
  exit 1
fi
echo "Synchronisation des fichiers terminée avec succès."

# Création des répertoires nécessaires sur le NAS
echo "Création des répertoires de données sur le NAS..."
ssh "$NAS_USER@$NAS_IP" "mkdir -p $NAS_DIR/data $NAS_DIR/logs $NAS_DIR/backups"

# Vérification des fichiers de configuration
echo "Vérification des fichiers de configuration..."
ssh "$NAS_USER@$NAS_IP" "
  if [ ! -f $NAS_DIR/config/config.json ]; then
    echo 'Configuration principale non trouvée, copie du fichier exemple...'
    cp $NAS_DIR/config/config.json.example $NAS_DIR/config/config.json
  fi
  
  if [ ! -f $NAS_DIR/config/notification_config.json ]; then
    echo 'Configuration des notifications non trouvée, copie du fichier exemple...'
    cp $NAS_DIR/config/notification_config.json.example $NAS_DIR/config/notification_config.json
  fi
  
  if [ ! -f $NAS_DIR/config/error_handler_config.json ]; then
    echo 'Configuration du gestionnaire d'erreurs non trouvée, copie du fichier exemple...'
    cp $NAS_DIR/config/error_handler_config.json.example $NAS_DIR/config/error_handler_config.json
  fi
  
  if [ ! -f $NAS_DIR/config/api_client_config.json ]; then
    echo 'Configuration du client API non trouvée, copie du fichier exemple...'
    cp $NAS_DIR/config/api_client_config.json.example $NAS_DIR/config/api_client_config.json
  fi
"

# Rendre les scripts exécutables
echo "Configuration des permissions des scripts..."
ssh "$NAS_USER@$NAS_IP" "chmod +x $NAS_DIR/scripts/*.sh"

# Démarrage du conteneur Docker
echo "Démarrage du conteneur Docker..."
ssh "$NAS_USER@$NAS_IP" "cd $NAS_DIR && docker-compose up -d"

if [ $? -ne 0 ]; then
  echo "Erreur lors du démarrage du conteneur Docker."
  echo "Veuillez vérifier que Docker est installé et fonctionnel sur le NAS."
  exit 1
fi

echo "=== Déploiement terminé avec succès ==="
echo "Le Bot de Trading XRP v3.0 est maintenant déployé et en cours d'exécution sur votre NAS Synology."
echo ""
echo "Pour vérifier l'état du conteneur:"
echo "  ssh $NAS_USER@$NAS_IP \"cd $NAS_DIR && docker-compose ps\""
echo ""
echo "Pour voir les logs:"
echo "  ssh $NAS_USER@$NAS_IP \"cd $NAS_DIR && docker-compose logs -f\""
echo ""
echo "Pour arrêter le bot:"
echo "  ssh $NAS_USER@$NAS_IP \"cd $NAS_DIR && docker-compose down\""
echo ""
echo "N'oubliez pas de configurer vos clés API et Pushover dans les fichiers de configuration!"
