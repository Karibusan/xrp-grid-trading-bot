# Guide de déploiement manuel pour macOS

Ce guide explique comment déployer manuellement le XRP Trading Bot v3.0 sur un Synology NAS depuis macOS, sans modifier votre configuration SSH existante.

## Prérequis

- Un Synology NAS avec Docker installé
- Accès à l'interface web DSM de votre Synology
- Accès SSH à votre Synology (port 28)
- Client SFTP (comme FileZilla, Cyberduck ou Transmit)

## Étapes de déploiement

### 1. Création des répertoires

Utilisez l'interface web File Station de votre Synology pour créer les répertoires suivants :

```
/volume1/docker/xrp-grid-trading-bot/config
/volume1/docker/xrp-grid-trading-bot/data
/volume1/docker/xrp-grid-trading-bot/logs
/volume1/docker/xrp-grid-trading-bot/backups
```

### 2. Transfert des fichiers

Utilisez un client SFTP pour transférer les fichiers suivants vers votre Synology :

1. Connectez-vous à votre Synology avec les paramètres suivants :
   - Hôte : 192.168.1.100
   - Port : 28
   - Utilisateur : Karibusan
   - Mot de passe : votre_mot_de_passe

2. Transférez les fichiers et dossiers suivants vers `/volume1/docker/xrp-grid-trading-bot/` :
   - Le dossier `src/`
   - Le dossier `scripts/`
   - Le fichier `docker-compose.yml`
   - Le fichier `Dockerfile`
   - Le fichier `requirements.txt`

3. Transférez les fichiers de configuration d'exemple vers `/volume1/docker/xrp-grid-trading-bot/config/` :
   - Tous les fichiers `.example` du dossier `config/`

### 3. Configuration

1. Dans File Station, naviguez vers `/volume1/docker/xrp-grid-trading-bot/config/`
2. Copiez chaque fichier `.example` en retirant l'extension `.example` :
   - `config.json.example` → `config.json`
   - `notification_config.json.example` → `notification_config.json`
   - `error_handler_config.json.example` → `error_handler_config.json`
   - `api_client_config.json.example` → `api_client_config.json`
3. Modifiez ces fichiers pour ajouter vos clés API et autres paramètres personnalisés

### 4. Configuration des permissions

Connectez-vous en SSH à votre Synology :

```bash
ssh -p 28 Karibusan@192.168.1.100
```

Exécutez les commandes suivantes :

```bash
chmod -R 755 /volume1/docker/xrp-grid-trading-bot
chmod -R 777 /volume1/docker/xrp-grid-trading-bot/logs
chmod -R 777 /volume1/docker/xrp-grid-trading-bot/data
chmod -R 777 /volume1/docker/xrp-grid-trading-bot/backups
chmod +x /volume1/docker/xrp-grid-trading-bot/scripts/*.sh
```

### 5. Démarrage du bot

Toujours en SSH, exécutez :

```bash
cd /volume1/docker/xrp-grid-trading-bot
docker-compose up -d
```

### 6. Vérification des logs

Pour vérifier que tout fonctionne correctement :

```bash
docker-compose logs -f
```

## Dépannage

### Le conteneur ne démarre pas

Vérifiez les logs Docker pour plus de détails :

```bash
docker-compose logs
```

### Problèmes de permissions

Assurez-vous que les répertoires ont les bonnes permissions :

```bash
chmod -R 777 /volume1/docker/xrp-grid-trading-bot/logs
chmod -R 777 /volume1/docker/xrp-grid-trading-bot/data
chmod -R 777 /volume1/docker/xrp-grid-trading-bot/backups
```

### Problèmes de configuration

Vérifiez que vos fichiers de configuration sont correctement formatés (JSON valide) et contiennent toutes les informations nécessaires.

## Maintenance

### Sauvegarde

Les sauvegardes sont automatiquement stockées dans `/volume1/docker/xrp-grid-trading-bot/backups/`.

### Mise à jour

Pour mettre à jour le bot, répétez le processus de transfert de fichiers pour les nouveaux fichiers, puis redémarrez le conteneur :

```bash
cd /volume1/docker/xrp-grid-trading-bot
docker-compose down
docker-compose up -d --build
```
