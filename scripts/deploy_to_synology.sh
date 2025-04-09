#!/bin/bash
# Script de déploiement amélioré pour Synology NAS
# Usage: ./deploy_to_synology.sh <synology_ip> <synology_user> <deploy_path>

# Vérification des arguments
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <synology_ip> <synology_user> <deploy_path>"
    echo "Example: $0 192.168.1.100 admin /volume1/docker/xrp_bot"
    exit 1
fi

SYNOLOGY_IP=$1
SYNOLOGY_USER=$2
DEPLOY_PATH=$3

echo "Déploiement du XRP Trading Bot v3.0 sur Synology NAS ($SYNOLOGY_IP)..."

# Création des répertoires nécessaires sur le Synology
echo "Création des répertoires nécessaires..."
ssh $SYNOLOGY_USER@$SYNOLOGY_IP "mkdir -p $DEPLOY_PATH/config"
ssh $SYNOLOGY_USER@$SYNOLOGY_IP "mkdir -p $DEPLOY_PATH/data"
ssh $SYNOLOGY_USER@$SYNOLOGY_IP "mkdir -p $DEPLOY_PATH/logs"
ssh $SYNOLOGY_USER@$SYNOLOGY_IP "mkdir -p $DEPLOY_PATH/backups"

# Vérification que les répertoires ont été créés
if [ $? -ne 0 ]; then
    echo "Erreur lors de la création des répertoires. Vérifiez vos permissions et connexion SSH."
    exit 1
fi

# Copie des fichiers
echo "Copie des fichiers vers le Synology..."
scp -r src $SYNOLOGY_USER@$SYNOLOGY_IP:$DEPLOY_PATH/
scp -r scripts $SYNOLOGY_USER@$SYNOLOGY_IP:$DEPLOY_PATH/
scp docker-compose.yml $SYNOLOGY_USER@$SYNOLOGY_IP:$DEPLOY_PATH/
scp requirements.txt $SYNOLOGY_USER@$SYNOLOGY_IP:$DEPLOY_PATH/
scp Dockerfile $SYNOLOGY_USER@$SYNOLOGY_IP:$DEPLOY_PATH/

# Copie des fichiers de configuration d'exemple
echo "Copie des fichiers de configuration..."
scp -r config/*.example $SYNOLOGY_USER@$SYNOLOGY_IP:$DEPLOY_PATH/config/

# Définition des permissions
echo "Configuration des permissions..."
ssh $SYNOLOGY_USER@$SYNOLOGY_IP "chmod -R 755 $DEPLOY_PATH"
ssh $SYNOLOGY_USER@$SYNOLOGY_IP "chmod -R 777 $DEPLOY_PATH/logs"
ssh $SYNOLOGY_USER@$SYNOLOGY_IP "chmod -R 777 $DEPLOY_PATH/data"
ssh $SYNOLOGY_USER@$SYNOLOGY_IP "chmod -R 777 $DEPLOY_PATH/backups"
ssh $SYNOLOGY_USER@$SYNOLOGY_IP "chmod +x $DEPLOY_PATH/scripts/*.sh"

echo "Déploiement terminé avec succès!"
echo ""
echo "Pour configurer le bot:"
echo "1. Connectez-vous à votre Synology"
echo "2. Naviguez vers $DEPLOY_PATH/config"
echo "3. Copiez les fichiers .example en retirant l'extension .example"
echo "   cp config.json.example config.json"
echo "   cp notification_config.json.example notification_config.json"
echo "   cp error_handler_config.json.example error_handler_config.json"
echo "   cp api_client_config.json.example api_client_config.json"
echo "4. Modifiez les fichiers de configuration avec vos clés API"
echo ""
echo "Pour démarrer le bot:"
echo "1. Connectez-vous à votre Synology via SSH"
echo "2. Naviguez vers $DEPLOY_PATH"
echo "3. Exécutez: docker-compose up -d"
echo ""
echo "Pour vérifier les logs:"
echo "docker-compose logs -f"
