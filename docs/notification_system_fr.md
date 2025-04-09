#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Documentation pour le gestionnaire de notifications du XRP Trading Bot v3.0
"""

# Guide d'utilisation du système de notification Pushover

## Introduction

Le système de notification du XRP Trading Bot v3.0 utilise Pushover pour envoyer des notifications push
à vos appareils mobiles et navigateurs de bureau. Ce document explique comment configurer et utiliser
ce système.

## Qu'est-ce que Pushover ?

Pushover est un service qui permet d'envoyer des notifications push à vos appareils iOS, Android et
navigateurs de bureau. Il offre une API simple et fiable pour l'envoi de notifications.

## Configuration de Pushover

### 1. Créer un compte Pushover

1. Rendez-vous sur [https://pushover.net/](https://pushover.net/) et créez un compte
2. Installez l'application Pushover sur votre appareil mobile (iOS ou Android)
3. Connectez-vous à l'application avec vos identifiants

### 2. Créer une application pour le XRP Trading Bot

1. Connectez-vous à votre compte Pushover sur le site web
2. Accédez à [https://pushover.net/apps/build](https://pushover.net/apps/build)
3. Créez une nouvelle application avec les informations suivantes :
   - Nom : XRP Trading Bot
   - Type : Application
   - Description : Bot de trading automatisé pour XRP
   - URL : (facultatif)
   - Icône : (facultatif)
4. Cliquez sur "Create Application"
5. Notez le "API Token/Key" qui vous est attribué

### 3. Configurer le XRP Trading Bot

1. Ouvrez le fichier `config/notification_config.json`
2. Remplacez `YOUR_USER_KEY_HERE` par votre clé utilisateur Pushover (trouvable sur votre page d'accueil Pushover)
3. Remplacez `YOUR_APP_TOKEN_HERE` par le token d'API de l'application que vous venez de créer
4. Ajustez les autres paramètres selon vos préférences

Exemple de configuration :
```json
{
    "pushover": {
        "enabled": true,
        "user_key": "uQiRzpo4DXghDmr9QzzfQu27cmVRsG",
        "app_token": "azGDORePK8gMaC0QOYAMyEEuzJnyUi",
        "device": "",
        "sound": "pushover",
        "priority": 0
    },
    "high_priority_trades": true,
    "notification_levels": {
        "trade": true,
        "error": true,
        "warning": true,
        "info": true,
        "debug": false
    },
    "throttling": {
        "enabled": true,
        "max_notifications_per_hour": 20,
        "min_time_between_notifications_seconds": 30
    }
}
```

## Types de notifications

Le système envoie plusieurs types de notifications :

1. **Notifications de trade** : Envoyées lorsqu'un ordre d'achat ou de vente est exécuté
2. **Notifications d'erreur** : Envoyées lorsqu'une erreur se produit dans le système
3. **Notifications de statut** : Envoyées pour informer de l'état du système
4. **Notifications générales** : Autres informations importantes

## Personnalisation des notifications

### Priorités

Pushover prend en charge différents niveaux de priorité :

- `-2` : Plus basse priorité, pas de notification sonore ou visuelle
- `-1` : Priorité basse, pas de notification sonore
- `0` : Priorité normale (par défaut)
- `1` : Priorité haute, contourne le mode silencieux
- `2` : Priorité d'urgence, répète jusqu'à confirmation

Vous pouvez configurer la priorité par défaut dans le fichier de configuration.

### Sons

Pushover propose différents sons pour les notifications. Vous pouvez spécifier le son par défaut
dans le fichier de configuration. Les options incluent :

- `pushover` (par défaut)
- `bike`
- `bugle`
- `cashregister`
- `classical`
- `cosmic`
- `falling`
- `gamelan`
- `incoming`
- `intermission`
- `magic`
- `mechanical`
- `pianobar`
- `siren`
- `spacealarm`
- `tugboat`
- `alien`
- `climb`
- `persistent`
- `echo`
- `updown`
- `vibrate`
- `none`

### Limitation des notifications

Pour éviter de recevoir trop de notifications, le système inclut des options de limitation :

- `max_notifications_per_hour` : Nombre maximum de notifications par heure
- `min_time_between_notifications_seconds` : Temps minimum entre deux notifications

## Dépannage

### Je ne reçois pas de notifications

1. Vérifiez que Pushover est correctement configuré avec les bonnes clés
2. Assurez-vous que l'option `enabled` est définie sur `true`
3. Vérifiez les journaux du bot pour les erreurs liées à l'envoi de notifications
4. Testez votre configuration Pushover avec l'outil de test sur le site web de Pushover

### Les notifications sont retardées

1. Vérifiez votre connexion Internet
2. Assurez-vous que l'application Pushover est autorisée à s'exécuter en arrière-plan
3. Vérifiez les paramètres de batterie et d'optimisation de votre appareil

### J'ai besoin de limiter certains types de notifications

Utilisez les options dans `notification_levels` pour activer ou désactiver des types spécifiques de notifications :

```json
"notification_levels": {
    "trade": true,
    "error": true,
    "warning": true,
    "info": false,
    "debug": false
}
```

## Utilisation avancée

### Notifications à des appareils spécifiques

Si vous avez plusieurs appareils enregistrés avec Pushover, vous pouvez spécifier un appareil particulier
pour recevoir les notifications en définissant le paramètre `device` dans la configuration.

### Intégration avec d'autres systèmes

Le gestionnaire de notifications est conçu de manière modulaire et peut être étendu pour prendre en charge
d'autres systèmes de notification à l'avenir.
