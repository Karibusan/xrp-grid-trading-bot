# Pushover Notification System Guide

## Introduction

The notification system of the XRP Trading Bot v3.0 uses Pushover to send push notifications to your mobile devices and desktop browsers. This document explains how to configure and use this system.

## What is Pushover?

Pushover is a service that allows you to send push notifications to your iOS, Android devices, and desktop browsers. It offers a simple and reliable API for sending notifications.

## Pushover Configuration

### 1. Create a Pushover Account

1. Go to [https://pushover.net/](https://pushover.net/) and create an account
2. Install the Pushover application on your mobile device (iOS or Android)
3. Log in to the application with your credentials

### 2. Create an Application for the XRP Trading Bot

1. Log in to your Pushover account on the website
2. Go to [https://pushover.net/apps/build](https://pushover.net/apps/build)
3. Create a new application with the following information:
   - Name: XRP Trading Bot
   - Type: Application
   - Description: Automated trading bot for XRP
   - URL: (optional)
   - Icon: (optional)
4. Click on "Create Application"
5. Note the "API Token/Key" that is assigned to you

### 3. Configure the XRP Trading Bot

1. Open the `config/notification_config.json` file
2. Replace `YOUR_USER_KEY_HERE` with your Pushover user key (found on your Pushover home page)
3. Replace `YOUR_APP_TOKEN_HERE` with the API token of the application you just created
4. Adjust other parameters according to your preferences

Example configuration:
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

## Notification Types

The system sends several types of notifications:

1. **Trade notifications**: Sent when a buy or sell order is executed
2. **Error notifications**: Sent when an error occurs in the system
3. **Status notifications**: Sent to inform about the system status
4. **General notifications**: Other important information

## Customizing Notifications

### Priorities

Pushover supports different priority levels:

- `-2`: Lowest priority, no sound or visual notification
- `-1`: Low priority, no sound notification
- `0`: Normal priority (default)
- `1`: High priority, bypasses quiet hours
- `2`: Emergency priority, repeats until confirmed

You can configure the default priority in the configuration file.

### Sounds

Pushover offers different sounds for notifications. You can specify the default sound in the configuration file. Options include:

- `pushover` (default)
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

### Notification Throttling

To avoid receiving too many notifications, the system includes throttling options:

- `max_notifications_per_hour`: Maximum number of notifications per hour
- `min_time_between_notifications_seconds`: Minimum time between two notifications

## Troubleshooting

### I'm not receiving notifications

1. Check that Pushover is correctly configured with the right keys
2. Make sure the `enabled` option is set to `true`
3. Check the bot logs for errors related to sending notifications
4. Test your Pushover configuration with the test tool on the Pushover website

### Notifications are delayed

1. Check your Internet connection
2. Make sure the Pushover application is allowed to run in the background
3. Check your device's battery and optimization settings

### I need to limit certain types of notifications

Use the options in `notification_levels` to enable or disable specific types of notifications:

```json
"notification_levels": {
    "trade": true,
    "error": true,
    "warning": true,
    "info": false,
    "debug": false
}
```

## Advanced Usage

### Notifications to specific devices

If you have multiple devices registered with Pushover, you can specify a particular device to receive notifications by setting the `device` parameter in the configuration.

### Integration with other systems

The notification manager is designed in a modular way and can be extended to support other notification systems in the future.
