# Documentation du Bot de Trading XRP v3.0

## Introduction

Le Bot de Trading XRP v3.0 est une évolution majeure du système de trading automatisé pour la paire XRP/GBP. Cette nouvelle version apporte des améliorations significatives en termes de fiabilité, de gestion des erreurs, de notifications et de performance.

Ce document présente l'architecture, les fonctionnalités et les instructions d'installation et de configuration du bot v3.0.

## Nouvelles fonctionnalités

La version 3.0 introduit plusieurs améliorations majeures par rapport aux versions précédentes :

1. **Système de notification Pushover** : Remplacement de Telegram par Pushover pour des notifications plus fiables et configurables
2. **Gestion avancée des erreurs** : Système centralisé de détection, journalisation et récupération des erreurs
3. **Client API optimisé** : Limitation de débit, mise en cache et gestion robuste des erreurs pour l'API Kraken
4. **Gestion de configuration améliorée** : Validation des configurations via des schémas JSON et gestion centralisée
5. **Tests unitaires** : Couverture de test pour tous les composants principaux
6. **Sécurité renforcée** : Meilleure protection des clés API et des données sensibles
7. **Documentation complète** : Documentation détaillée en français et en anglais

## Architecture du système

Le bot v3.0 est construit autour d'une architecture modulaire avec les composants suivants :

### Composants principaux

1. **EnhancedTradingSystem** : Système principal de trading qui coordonne tous les autres composants
2. **NotificationManager** : Gestion des notifications via Pushover avec différents niveaux de priorité
3. **ErrorHandler** : Détection, journalisation et récupération des erreurs
4. **APIClient** : Interface optimisée pour l'API Kraken avec mise en cache et limitation de débit
5. **ConfigManager** : Gestion centralisée des configurations avec validation

### Modules spécialisés

1. **SignalCollapseModule** : Analyse des signaux de marché pour détecter les effondrements potentiels
2. **CapitalMigrationModule** : Suivi des mouvements de capitaux entre les marchés
3. **StrategicBifurcationModule** : Analyse des bifurcations stratégiques dans le marché
4. **TechnologicalConvergenceModule** : Évaluation de l'impact des convergences technologiques
5. **SurvivabilityModule** : Analyse de la survie du système dans des conditions de marché extrêmes

## Installation

### Prérequis

- Python 3.9 ou supérieur
- Docker et Docker Compose (pour le déploiement en conteneur)
- Compte Kraken avec clés API
- Compte Pushover avec clé utilisateur et jeton d'application

### Installation standard

1. Clonez le dépôt :
   ```bash
   git clone https://github.com/Karibusan/xrp-grid-trading-bot.git
   cd xrp-grid-trading-bot
   ```

2. Créez un environnement virtuel et installez les dépendances :
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Copiez les fichiers de configuration d'exemple et modifiez-les selon vos besoins :
   ```bash
   cp config/config.json.example config/config.json
   cp config/notification_config.json.example config/notification_config.json
   cp config/error_handler_config.json.example config/error_handler_config.json
   cp config/api_client_config.json.example config/api_client_config.json
   ```

4. Modifiez les fichiers de configuration pour ajouter vos clés API Kraken et Pushover.

### Installation avec Docker

1. Clonez le dépôt :
   ```bash
   git clone https://github.com/Karibusan/xrp-grid-trading-bot.git
   cd xrp-grid-trading-bot
   ```

2. Copiez les fichiers de configuration d'exemple et modifiez-les selon vos besoins :
   ```bash
   cp config/config.json.example config/config.json
   cp config/notification_config.json.example config/notification_config.json
   cp config/error_handler_config.json.example config/error_handler_config.json
   cp config/api_client_config.json.example config/api_client_config.json
   ```

3. Modifiez les fichiers de configuration pour ajouter vos clés API Kraken et Pushover.

4. Lancez le conteneur Docker :
   ```bash
   docker-compose up -d
   ```

## Configuration

### Configuration principale

Le fichier `config/config.json` contient la configuration principale du bot :

```json
{
    "trading_pair": "XRPGBP",
    "grid_range_percentage": 4.0,
    "grid_levels": 16,
    "total_allocation": 100.0,
    "price_check_interval_minutes": 5,
    "dynamic_sizing": true,
    "stop_loss_percentage": 10.0,
    "profit_reinvestment": 50.0,
    "api_key": "VOTRE_CLE_API_KRAKEN",
    "api_secret": "VOTRE_SECRET_API_KRAKEN",
    "modules": {
        "signal_collapse": {
            "enabled": true,
            "config_file": "signal_collapse_config.json"
        },
        "capital_migration": {
            "enabled": true,
            "config_file": "capital_migration_config.json"
        },
        "strategic_bifurcation": {
            "enabled": true,
            "config_file": "strategic_bifurcation_config.json"
        },
        "technological_convergence": {
            "enabled": true,
            "config_file": "technological_convergence_config.json"
        },
        "survivability": {
            "enabled": true,
            "config_file": "survivability_config.json"
        }
    },
    "notification": {
        "config_file": "notification_config.json"
    },
    "error_handler": {
        "config_file": "error_handler_config.json"
    },
    "api_client": {
        "config_file": "api_client_config.json"
    },
    "emergency_mode": false,
    "debug_mode": false
}
```

### Configuration des notifications

Le fichier `config/notification_config.json` contient la configuration du système de notification :

```json
{
    "pushover": {
        "enabled": true,
        "user_key": "VOTRE_CLE_UTILISATEUR_PUSHOVER",
        "app_token": "VOTRE_JETON_APP_PUSHOVER",
        "device": "",
        "sound": "pushover",
        "priority": 0
    },
    "notification_levels": {
        "trade": true,
        "daily_report": true,
        "efficiency": true,
        "error": true,
        "debug": false
    },
    "level_settings": {
        "trade": {
            "priority": 0,
            "sound": "cashregister"
        },
        "daily_report": {
            "priority": -1,
            "sound": "classical"
        },
        "efficiency": {
            "priority": -1,
            "sound": "mechanical"
        },
        "error": {
            "priority": 1,
            "sound": "siren"
        },
        "debug": {
            "priority": -2,
            "sound": "none"
        }
    },
    "throttling": {
        "enabled": true,
        "max_notifications_per_hour": {
            "trade": 20,
            "daily_report": 2,
            "efficiency": 4,
            "error": 10,
            "debug": 5
        },
        "min_time_between_notifications_seconds": {
            "trade": 30,
            "daily_report": 3600,
            "efficiency": 900,
            "error": 60,
            "debug": 300
        }
    }
}
```

### Configuration du gestionnaire d'erreurs

Le fichier `config/error_handler_config.json` contient la configuration du gestionnaire d'erreurs :

```json
{
    "error_log_path": "data/error_log.json",
    "max_log_size": 1000,
    "reraise_exceptions": false,
    "recovery_cooldown_minutes": {
        "api_timeout": 5,
        "network_error": 10,
        "data_processing_error": 15,
        "kraken_api_error": 5,
        "order_placement_error": 10,
        "configuration_error": 30
    },
    "notification_settings": {
        "severity": {
            "critical": true,
            "high": true,
            "medium": true,
            "low": false,
            "info": false
        },
        "error_types": {
            "api_timeout": true,
            "network_error": true,
            "data_processing_error": true,
            "kraken_api_error": true,
            "order_placement_error": true,
            "configuration_error": true,
            "module_initialization_error": true
        },
        "max_notifications_per_hour": {
            "api_timeout": 3,
            "network_error": 3,
            "data_processing_error": 5,
            "kraken_api_error": 5,
            "order_placement_error": 5,
            "configuration_error": 2,
            "module_initialization_error": 2
        }
    }
}
```

### Configuration du client API

Le fichier `config/api_client_config.json` contient la configuration du client API :

```json
{
    "rate_limits": {
        "max_requests_per_second": 1.0,
        "max_requests_per_minute": 15
    },
    "cache": {
        "max_size": 100,
        "default_ttl_seconds": 60,
        "ttl_overrides": {
            "Time": 60,
            "Assets": 3600,
            "AssetPairs": 3600,
            "Ticker": 15,
            "Depth": 5,
            "Trades": 30,
            "Spread": 5,
            "OHLC": 60
        }
    },
    "timeout_seconds": 30,
    "retry": {
        "max_retries": 3,
        "retry_delay_seconds": 2,
        "retry_backoff_factor": 2,
        "retry_status_codes": [429, 500, 502, 503, 504]
    }
}
```

## Utilisation

### Démarrage du bot

Pour démarrer le bot en mode standard :

```bash
python src/main.py
```

Pour démarrer le bot avec un fichier de configuration spécifique :

```bash
python src/main.py --config path/to/config.json
```

### Commandes disponibles

Le bot prend en charge les commandes suivantes :

- `--config` : Spécifie le chemin vers le fichier de configuration principal
- `--debug` : Active le mode debug (journalisation détaillée)
- `--test` : Exécute le bot en mode test (sans passer d'ordres réels)
- `--reset` : Réinitialise l'état du bot avant de démarrer

### Surveillance et maintenance

#### Journaux

Les journaux sont stockés dans le répertoire `logs/` et sont organisés par date.

#### Sauvegarde

Un script de sauvegarde est fourni pour sauvegarder les configurations et les données :

```bash
./scripts/backup.sh
```

#### Mise à jour

Pour mettre à jour le bot vers la dernière version :

```bash
git pull
pip install -r requirements.txt
```

## Configuration de Pushover

### Création d'un compte Pushover

1. Rendez-vous sur [pushover.net](https://pushover.net) et créez un compte
2. Après la connexion, notez votre clé utilisateur (User Key)
3. Créez une nouvelle application pour obtenir un jeton d'application (App Token)

### Configuration des notifications

1. Ajoutez votre clé utilisateur et votre jeton d'application dans `config/notification_config.json`
2. Configurez les niveaux de notification selon vos préférences
3. Personnalisez les sons et les priorités pour chaque type de notification

## Dépannage

### Problèmes courants

#### Le bot ne démarre pas

- Vérifiez que tous les fichiers de configuration sont correctement formatés (JSON valide)
- Assurez-vous que les clés API Kraken sont correctes et ont les permissions nécessaires
- Vérifiez les journaux pour des erreurs spécifiques

#### Pas de notifications

- Vérifiez que les clés Pushover sont correctes
- Assurez-vous que Pushover est activé dans la configuration
- Vérifiez que les niveaux de notification sont activés

#### Erreurs d'API Kraken

- Vérifiez que les clés API ont les bonnes permissions
- Assurez-vous que vous n'avez pas dépassé les limites de l'API
- Vérifiez votre connexion internet

### Journaux d'erreurs

Le gestionnaire d'erreurs enregistre toutes les erreurs dans `data/error_log.json`. Consultez ce fichier pour des informations détaillées sur les erreurs rencontrées.

## Modules spécialisés

### Signal Collapse Module

Ce module analyse les signaux de marché pour détecter les effondrements potentiels. Il utilise des techniques d'analyse avancées pour identifier les moments où le marché pourrait connaître une chute significative.

### Capital Migration Module

Ce module suit les mouvements de capitaux entre les marchés. Il aide à identifier les tendances de migration de capitaux qui pourraient affecter le prix du XRP.

### Strategic Bifurcation Module

Ce module analyse les bifurcations stratégiques dans le marché. Il identifie les moments où le marché pourrait prendre une direction différente et ajuste la stratégie de trading en conséquence.

### Technological Convergence Module

Ce module évalue l'impact des convergences technologiques sur le prix du XRP. Il analyse comment les développements technologiques pourraient influencer la valeur de la cryptomonnaie.

### Survivability Module

Ce module analyse la capacité du système à survivre dans des conditions de marché extrêmes. Il peut activer le mode d'urgence si nécessaire pour protéger les actifs.

## Sécurité

### Protection des clés API

Les clés API sont stockées localement et ne sont jamais partagées. Le bot utilise des techniques sécurisées pour signer les requêtes API.

### Sauvegarde des données

Toutes les données importantes sont sauvegardées régulièrement. Utilisez le script de sauvegarde fourni pour créer des sauvegardes manuelles supplémentaires.

## Mises à jour futures

Les fonctionnalités suivantes sont prévues pour les versions futures :

1. Interface web pour la surveillance et la configuration
2. Support pour d'autres paires de trading
3. Stratégies de trading supplémentaires
4. Intégration avec d'autres échanges
5. Analyse de sentiment basée sur les médias sociaux

## Contribution

Les contributions au projet sont les bienvenues. Veuillez suivre ces étapes pour contribuer :

1. Forkez le dépôt
2. Créez une branche pour votre fonctionnalité
3. Ajoutez vos modifications
4. Soumettez une pull request

## Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

## Contact

Pour toute question ou assistance, veuillez contacter l'équipe de développement via GitHub.
