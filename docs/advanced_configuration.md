# Configuration avancée du Bot de Trading XRP v3.0

Ce document détaille les options de configuration avancées du Bot de Trading XRP v3.0, permettant une personnalisation fine du comportement du bot.

## Structure des fichiers de configuration

Le bot utilise plusieurs fichiers de configuration JSON pour organiser les paramètres par fonctionnalité :

- `config/config.json` : Configuration principale
- `config/notification_config.json` : Configuration des notifications
- `config/error_handler_config.json` : Configuration de la gestion des erreurs
- `config/api_client_config.json` : Configuration du client API
- `config/schemas/` : Schémas JSON pour la validation des configurations

## Configuration principale

### Paramètres de trading

| Paramètre | Type | Description | Valeur par défaut |
|-----------|------|-------------|-------------------|
| `trading_pair` | string | Paire de trading (ex: XRPGBP) | XRPGBP |
| `grid_range_percentage` | number | Pourcentage de la plage de la grille | 4.0 |
| `grid_levels` | integer | Nombre de niveaux dans la grille | 16 |
| `total_allocation` | number | Allocation totale pour le trading | 100.0 |
| `price_check_interval_minutes` | integer | Intervalle entre les vérifications de prix (minutes) | 5 |
| `dynamic_sizing` | boolean | Utiliser le dimensionnement dynamique des ordres | true |
| `stop_loss_percentage` | number | Pourcentage de stop-loss (0 pour désactiver) | 10.0 |
| `profit_reinvestment` | number | Pourcentage de réinvestissement des profits (0-100) | 50.0 |

### Paramètres API

| Paramètre | Type | Description |
|-----------|------|-------------|
| `api_key` | string | Clé API Kraken |
| `api_secret` | string | Secret API Kraken |

### Configuration des modules

Chaque module peut être activé/désactivé et possède son propre fichier de configuration :

```json
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
}
```

### Paramètres système

| Paramètre | Type | Description | Valeur par défaut |
|-----------|------|-------------|-------------------|
| `emergency_mode` | boolean | Mode d'urgence (arrête le trading) | false |
| `debug_mode` | boolean | Mode debug (journalisation détaillée) | false |

## Configuration des notifications

### Paramètres Pushover

| Paramètre | Type | Description |
|-----------|------|-------------|
| `enabled` | boolean | Activer/désactiver Pushover |
| `user_key` | string | Clé utilisateur Pushover |
| `app_token` | string | Jeton d'application Pushover |
| `device` | string | Appareil spécifique (vide pour tous) |
| `sound` | string | Son par défaut |
| `priority` | integer | Priorité par défaut (-2 à 2) |

### Niveaux de notification

Vous pouvez activer/désactiver chaque niveau de notification :

```json
"notification_levels": {
    "trade": true,
    "daily_report": true,
    "efficiency": true,
    "error": true,
    "debug": false
}
```

### Paramètres par niveau

Chaque niveau peut avoir ses propres paramètres de priorité et de son :

```json
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
}
```

### Limitation des notifications

Pour éviter trop de notifications, vous pouvez configurer des limites :

```json
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
```

## Configuration du gestionnaire d'erreurs

### Paramètres généraux

| Paramètre | Type | Description | Valeur par défaut |
|-----------|------|-------------|-------------------|
| `error_log_path` | string | Chemin du fichier de log d'erreurs | data/error_log.json |
| `max_log_size` | integer | Taille maximale du log (nombre d'entrées) | 1000 |
| `reraise_exceptions` | boolean | Relancer les exceptions après traitement | false |

### Temps de récupération

Configurez le temps d'attente (en minutes) avant de réessayer après une erreur :

```json
"recovery_cooldown_minutes": {
    "api_timeout": 5,
    "network_error": 10,
    "data_processing_error": 15,
    "kraken_api_error": 5,
    "order_placement_error": 10,
    "configuration_error": 30
}
```

### Paramètres de notification d'erreurs

Configurez quelles erreurs déclenchent des notifications :

```json
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
```

## Configuration du client API

### Limites de débit

Configurez les limites de débit pour éviter de dépasser les limites de l'API Kraken :

```json
"rate_limits": {
    "max_requests_per_second": 1.0,
    "max_requests_per_minute": 15
}
```

### Configuration du cache

Configurez le cache pour réduire le nombre d'appels API :

```json
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
}
```

### Paramètres de timeout et retry

```json
"timeout_seconds": 30,
"retry": {
    "max_retries": 3,
    "retry_delay_seconds": 2,
    "retry_backoff_factor": 2,
    "retry_status_codes": [429, 500, 502, 503, 504]
}
```

## Configuration des modules spécialisés

### Signal Collapse Module

Le module Signal Collapse analyse les signaux de marché pour détecter les effondrements potentiels.

```json
{
    "enabled": true,
    "threshold": 0.75,
    "window_size": 24,
    "indicators": ["rsi", "macd", "bollinger"],
    "emergency_threshold": 0.9,
    "risk_adjustment_factor": 0.5
}
```

### Capital Migration Module

Le module Capital Migration suit les mouvements de capitaux entre les marchés.

```json
{
    "enabled": true,
    "tracking_pairs": ["BTCUSD", "ETHUSD", "XRPUSD"],
    "correlation_threshold": 0.7,
    "volume_significance_factor": 1.5,
    "adjustment_strength": 0.5
}
```

### Strategic Bifurcation Module

Le module Strategic Bifurcation analyse les bifurcations stratégiques dans le marché.

```json
{
    "enabled": true,
    "timeframes": [15, 60, 240, 1440],
    "divergence_threshold": 0.2,
    "confirmation_period": 3,
    "max_recommendations": 5
}
```

### Technological Convergence Module

Le module Technological Convergence évalue l'impact des convergences technologiques.

```json
{
    "enabled": true,
    "news_sources": ["cryptopanic", "reddit", "twitter"],
    "sentiment_threshold": 0.6,
    "tech_keywords": ["partnership", "adoption", "integration", "update"],
    "impact_factor": 0.3
}
```

### Survivability Module

Le module Survivability analyse la capacité du système à survivre dans des conditions de marché extrêmes.

```json
{
    "enabled": true,
    "max_drawdown_percentage": 15,
    "recovery_threshold": 0.5,
    "emergency_reserve_percentage": 20,
    "market_stress_indicators": ["volatility", "volume", "spread"],
    "stress_threshold": 0.8
}
```

## Validation des configurations

Le bot utilise des schémas JSON pour valider les configurations. Ces schémas se trouvent dans le répertoire `config/schemas/`.

Pour ajouter un nouveau paramètre de configuration :

1. Ajoutez le paramètre au fichier de configuration approprié
2. Mettez à jour le schéma correspondant dans `config/schemas/`
3. Redémarrez le bot pour appliquer les changements

## Variables d'environnement

Vous pouvez également utiliser des variables d'environnement pour configurer certains paramètres sensibles :

| Variable d'environnement | Paramètre correspondant |
|--------------------------|-------------------------|
| `XRP_BOT_API_KEY` | api_key |
| `XRP_BOT_API_SECRET` | api_secret |
| `XRP_BOT_PUSHOVER_USER_KEY` | pushover.user_key |
| `XRP_BOT_PUSHOVER_APP_TOKEN` | pushover.app_token |

Exemple d'utilisation :

```bash
export XRP_BOT_API_KEY="votre_clé_api"
export XRP_BOT_API_SECRET="votre_secret_api"
python src/main.py
```

## Exemples de configuration

### Configuration pour trading conservateur

```json
{
    "trading_pair": "XRPGBP",
    "grid_range_percentage": 2.0,
    "grid_levels": 10,
    "total_allocation": 50.0,
    "price_check_interval_minutes": 10,
    "dynamic_sizing": true,
    "stop_loss_percentage": 5.0,
    "profit_reinvestment": 25.0
}
```

### Configuration pour trading agressif

```json
{
    "trading_pair": "XRPGBP",
    "grid_range_percentage": 8.0,
    "grid_levels": 24,
    "total_allocation": 200.0,
    "price_check_interval_minutes": 3,
    "dynamic_sizing": true,
    "stop_loss_percentage": 15.0,
    "profit_reinvestment": 75.0
}
```

### Configuration pour notifications minimales

```json
{
    "pushover": {
        "enabled": true,
        "user_key": "VOTRE_CLE_UTILISATEUR",
        "app_token": "VOTRE_JETON_APP",
        "device": "",
        "sound": "pushover",
        "priority": 0
    },
    "notification_levels": {
        "trade": false,
        "daily_report": true,
        "efficiency": false,
        "error": true,
        "debug": false
    },
    "throttling": {
        "enabled": true,
        "max_notifications_per_hour": {
            "daily_report": 1,
            "error": 5
        }
    }
}
```

## Bonnes pratiques

1. **Commencez prudemment** : Utilisez d'abord une allocation totale faible et augmentez progressivement
2. **Testez vos configurations** : Utilisez le mode test avant de passer en production
3. **Surveillez régulièrement** : Vérifiez les journaux et les notifications pour vous assurer que tout fonctionne correctement
4. **Sauvegardez vos configurations** : Utilisez le script de sauvegarde régulièrement
5. **Ajustez progressivement** : Modifiez un paramètre à la fois et observez les résultats avant de faire d'autres changements
