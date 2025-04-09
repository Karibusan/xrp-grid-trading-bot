#!/bin/bash
# Script de déploiement personnalisé pour le Synology NAS de Karibusan avec gestion du mot de passe
# Paramètres spécifiques :
# - IP NAS : 192.168.1.100
# - Port SSH : 28
# - Utilisateur : Karibusan
# - Emplacement d'installation : /volume1/docker/xrp-grid-trading-bot

SYNOLOGY_IP="192.168.1.100"
SYNOLOGY_PORT="28"
SYNOLOGY_USER="Karibusan"
DEPLOY_PATH="/volume1/docker/xrp-grid-trading-bot"

# Vérifier si sshpass est installé
if ! command -v sshpass &> /dev/null; then
    echo "sshpass n'est pas installé. Voulez-vous l'installer? (y/n)"
    read -r install_sshpass
    if [[ "$install_sshpass" =~ ^[Yy]$ ]]; then
        sudo apt-get update && sudo apt-get install -y sshpass
    else
        echo "Ce script nécessite sshpass pour fonctionner sans demander le mot de passe à chaque commande."
        echo "Alternatives:"
        echo "1. Configurez l'authentification par clé SSH:"
        echo "   ssh-keygen -t rsa  # Si vous n'avez pas déjà une clé"
        echo "   ssh-copy-id -p 28 Karibusan@192.168.1.100"
        echo "2. Utilisez ssh-agent:"
        echo "   ssh-agent bash"
        echo "   ssh-add"
        echo "   ./deploy_to_synology_custom.sh"
        exit 1
    fi
fi

# Demander le mot de passe une seule fois
echo -n "Entrez le mot de passe SSH pour $SYNOLOGY_USER@$SYNOLOGY_IP: "
read -rs SSH_PASSWORD
echo ""

echo "Déploiement du XRP Trading Bot v3.0 sur Synology NAS ($SYNOLOGY_IP)..."

# Fonction pour exécuter des commandes SSH avec sshpass
function ssh_cmd {
    sshpass -p "$SSH_PASSWORD" ssh -p $SYNOLOGY_PORT -o StrictHostKeyChecking=no $SYNOLOGY_USER@$SYNOLOGY_IP "$1"
}

# Fonction pour copier des fichiers avec sshpass
function scp_cmd {
    sshpass -p "$SSH_PASSWORD" scp -P $SYNOLOGY_PORT -o StrictHostKeyChecking=no $1 $SYNOLOGY_USER@$SYNOLOGY_IP:$2
}

# Création des répertoires nécessaires sur le Synology
echo "Création des répertoires nécessaires..."
ssh_cmd "mkdir -p $DEPLOY_PATH/config"
ssh_cmd "mkdir -p $DEPLOY_PATH/data"
ssh_cmd "mkdir -p $DEPLOY_PATH/logs"
ssh_cmd "mkdir -p $DEPLOY_PATH/backups"

# Vérification que les répertoires ont été créés
if [ $? -ne 0 ]; then
    echo "Erreur lors de la création des répertoires. Vérifiez vos permissions et connexion SSH."
    exit 1
fi

# Copie des fichiers
echo "Copie des fichiers vers le Synology..."
scp_cmd -r src $DEPLOY_PATH/
scp_cmd -r scripts $DEPLOY_PATH/
scp_cmd docker-compose.yml $DEPLOY_PATH/
scp_cmd requirements.txt $DEPLOY_PATH/
scp_cmd Dockerfile $DEPLOY_PATH/

# Copie des fichiers de configuration d'exemple
echo "Copie des fichiers de configuration..."
scp_cmd -r config/*.example $DEPLOY_PATH/config/

# Définition des permissions
echo "Configuration des permissions..."
ssh_cmd "chmod -R 755 $DEPLOY_PATH"
ssh_cmd "chmod -R 777 $DEPLOY_PATH/logs"
ssh_cmd "chmod -R 777 $DEPLOY_PATH/data"
ssh_cmd "chmod -R 777 $DEPLOY_PATH/backups"
ssh_cmd "chmod +x $DEPLOY_PATH/scripts/*.sh"

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
echo "1. Connectez-vous à votre Synology via SSH (ssh -p 28 Karibusan@192.168.1.100)"
echo "2. Naviguez vers $DEPLOY_PATH"
echo "3. Exécutez: docker-compose up -d"
echo ""
echo "Pour vérifier les logs:"
echo "docker-compose logs -f"
