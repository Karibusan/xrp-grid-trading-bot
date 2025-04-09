# Guide d'installation du Bot de Trading XRP v3.0

Ce guide détaille les étapes d'installation et de configuration du Bot de Trading XRP v3.0.

## Prérequis

- Python 3.9 ou supérieur
- Docker et Docker Compose (pour le déploiement en conteneur)
- Compte Kraken avec clés API
- Compte Pushover avec clé utilisateur et jeton d'application

## Installation standard

### 1. Téléchargement du code source

Clonez le dépôt GitHub :

```bash
git clone https://github.com/Karibusan/xrp-grid-trading-bot.git
cd xrp-grid-trading-bot
```

### 2. Création de l'environnement virtuel

Créez un environnement virtuel Python et activez-le :

```bash
python3 -m venv venv
source venv/bin/activate  # Sur Windows : venv\Scripts\activate
```

### 3. Installation des dépendances

Installez les packages requis :

```bash
pip install -r requirements.txt
```

### 4. Configuration

Copiez les fichiers de configuration d'exemple :

```bash
cp config/config.json.example config/config.json
cp config/notification_config.json.example config/notification_config.json
cp config/error_handler_config.json.example config/error_handler_config.json
cp config/api_client_config.json.example config/api_client_config.json
```

Modifiez les fichiers de configuration selon vos besoins, en particulier :
- Ajoutez vos clés API Kraken dans `config/config.json`
- Ajoutez vos identifiants Pushover dans `config/notification_config.json`

### 5. Création des répertoires nécessaires

Créez les répertoires pour les données et les journaux :

```bash
mkdir -p data logs
```

### 6. Lancement du bot

Lancez le bot avec la commande :

```bash
python src/main.py
```

## Installation avec Docker

### 1. Téléchargement du code source

Clonez le dépôt GitHub :

```bash
git clone https://github.com/Karibusan/xrp-grid-trading-bot.git
cd xrp-grid-trading-bot
```

### 2. Configuration

Copiez les fichiers de configuration d'exemple :

```bash
cp config/config.json.example config/config.json
cp config/notification_config.json.example config/notification_config.json
cp config/error_handler_config.json.example config/error_handler_config.json
cp config/api_client_config.json.example config/api_client_config.json
```

Modifiez les fichiers de configuration selon vos besoins, en particulier :
- Ajoutez vos clés API Kraken dans `config/config.json`
- Ajoutez vos identifiants Pushover dans `config/notification_config.json`

### 3. Création des répertoires nécessaires

Créez les répertoires pour les données et les journaux :

```bash
mkdir -p /volume1/docker/xrp-grid-trading-bot/backups
mkdir -p /volume1/docker/xrp-grid-trading-bot/config
mkdir -p /volume1/docker/xrp-grid-trading-bot/data
mkdir -p /volume1/docker/xrp-grid-trading-bot/logs
```

### 4. Construction et lancement du conteneur Docker

Construisez et lancez le conteneur Docker :

```bash
docker-compose up -d
```

### 5. Vérification du fonctionnement

Vérifiez que le conteneur fonctionne correctement :

```bash
docker-compose logs -f
```

## Installation sur Synology NAS

### 1. Prérequis

- Docker doit être installé sur votre Synology NAS
- Accès SSH au NAS

### 2. Téléchargement du code source

Connectez-vous à votre NAS via SSH et clonez le dépôt :

```bash
ssh admin@votre-nas
cd /volume1/docker
git clone https://github.com/Karibusan/xrp-grid-trading-bot.git
cd xrp-grid-trading-bot
```

### 3. Configuration

Copiez et modifiez les fichiers de configuration :

```bash
cp config/config.json.example config/config.json
cp config/notification_config.json.example config/notification_config.json
cp config/error_handler_config.json.example config/error_handler_config.json
cp config/api_client_config.json.example config/api_client_config.json
```

Modifiez les fichiers avec un éditeur de texte comme nano :

```bash
nano config/config.json
nano config/notification_config.json
```

### 4. Création des répertoires nécessaires

Créez les répertoires pour les données et les journaux :

```bash
mkdir -p /volume1/docker/xrp-grid-trading-bot/backups
mkdir -p /volume1/docker/xrp-grid-trading-bot/config
mkdir -p /volume1/docker/xrp-grid-trading-bot/data
mkdir -p /volume1/docker/xrp-grid-trading-bot/logs
```

### 5. Lancement avec Docker Compose

Lancez le conteneur Docker :

```bash
docker-compose up -d
```

### 6. Configuration du démarrage automatique

Pour configurer le démarrage automatique au redémarrage du NAS, créez une tâche planifiée dans DSM :
1. Ouvrez le Centre de contrôle DSM
2. Allez dans "Tâche planifiée"
3. Créez une nouvelle tâche "Déclenchée"
4. Définissez le déclencheur sur "Démarrage"
5. Ajoutez la commande : `cd /volume1/docker/xrp-grid-trading-bot && docker-compose up -d`

## Configuration de Pushover

### 1. Création d'un compte Pushover

1. Rendez-vous sur [pushover.net](https://pushover.net) et créez un compte
2. Connectez-vous à votre compte
3. Notez votre clé utilisateur (User Key) affichée sur la page principale

### 2. Création d'une application

1. Faites défiler jusqu'à la section "Your Applications" en bas de la page
2. Cliquez sur "Create an Application/API Token"
3. Remplissez le formulaire :
   - Name: XRP Trading Bot
   - Type: Application
   - Description: Notifications pour le bot de trading XRP
   - URL: (laissez vide ou mettez l'URL de votre dépôt GitHub)
   - Icon: (optionnel, vous pouvez télécharger une icône)
4. Acceptez les conditions d'utilisation et cliquez sur "Create Application"
5. Notez le jeton d'application (API Token/Key) qui s'affiche

### 3. Configuration dans le bot

Ouvrez le fichier `config/notification_config.json` et ajoutez vos identifiants Pushover :

```json
{
    "pushover": {
        "enabled": true,
        "user_key": "VOTRE_CLE_UTILISATEUR",
        "app_token": "VOTRE_JETON_APPLICATION",
        "device": "",
        "sound": "pushover",
        "priority": 0
    },
    ...
}
```

### 4. Test des notifications

Vous pouvez tester les notifications en exécutant le script de test :

```bash
python scripts/test_notifications.py
```

## Vérification de l'installation

### 1. Vérification des journaux

Vérifiez les journaux pour vous assurer que le bot fonctionne correctement :

```bash
# Installation standard
tail -f logs/xrp_bot.log

# Installation Docker
docker-compose logs -f
```

### 2. Vérification des notifications

Assurez-vous de recevoir les notifications Pushover sur votre appareil.

### 3. Vérification des ordres

Connectez-vous à votre compte Kraken et vérifiez que les ordres sont correctement placés.

## Dépannage

### Problème : Le bot ne démarre pas

**Solution :**
1. Vérifiez que tous les fichiers de configuration sont correctement formatés (JSON valide)
2. Assurez-vous que les clés API Kraken sont correctes et ont les permissions nécessaires
3. Vérifiez les journaux pour des erreurs spécifiques

### Problème : Pas de notifications

**Solution :**
1. Vérifiez que les clés Pushover sont correctes
2. Assurez-vous que Pushover est activé dans la configuration
3. Vérifiez que les niveaux de notification sont activés
4. Exécutez le script de test des notifications

### Problème : Erreurs d'API Kraken

**Solution :**
1. Vérifiez que les clés API ont les bonnes permissions
2. Assurez-vous que vous n'avez pas dépassé les limites de l'API
3. Vérifiez votre connexion internet

### Problème : Erreurs dans les modules spécialisés

**Solution :**
1. Vérifiez les fichiers de configuration spécifiques aux modules
2. Consultez les journaux d'erreurs dans `data/error_log.json`
3. Désactivez temporairement les modules problématiques dans la configuration principale

## Mise à jour

Pour mettre à jour le bot vers la dernière version :

```bash
# Installation standard
git pull
pip install -r requirements.txt

# Installation Docker
git pull
docker-compose down
docker-compose up -d --build
```

## Sauvegarde

Utilisez le script de sauvegarde fourni pour sauvegarder vos configurations et données :

```bash
./scripts/backup.sh
```

Cela créera une archive datée dans le répertoire `backups/` contenant tous vos fichiers de configuration et données importantes.
