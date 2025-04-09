# XRP Trading Bot v3.0.2 Installation Guide

This guide details the steps for installing and configuring the XRP Trading Bot v3.0.2.

## Prerequisites

- Python 3.9 or higher
- Docker and Docker Compose (for container deployment)
- Kraken account with API keys
- Pushover account with user key and application token

## Standard Installation

### 1. Download the Source Code

Clone the GitHub repository:

```bash
git clone https://github.com/Karibusan/xrp-grid-trading-bot.git
cd xrp-grid-trading-bot
```

### 2. Create a Virtual Environment

Create and activate a Python virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

Install the required packages:

```bash
pip install -r requirements.txt
```

### 4. Create Required Directories

Create directories for data, logs, and backups:

```bash
mkdir -p data logs backups
```

### 5. Configuration

Copy the example configuration files:

```bash
cp config/config.json.example config/config.json
cp config/notification_config.json.example config/notification_config.json
cp config/error_handler_config.json.example config/error_handler_config.json
cp config/api_client_config.json.example config/api_client_config.json
cp config/signal_collapse_config.json.example config/signal_collapse_config.json
cp config/capital_migration_config.json.example config/capital_migration_config.json
cp config/strategic_bifurcation_config.json.example config/strategic_bifurcation_config.json
cp config/technological_convergence_config.json.example config/technological_convergence_config.json
cp config/survivability_config.json.example config/survivability_config.json
```

Modify the configuration files according to your needs, particularly:
- Add your Kraken API keys in `config/config.json`
- Add your Pushover credentials in `config/notification_config.json`

### 6. Launch the Bot

Start the bot with the command:

```bash
python src/main.py
```

## Docker Installation

### 1. Download the Source Code

Clone the GitHub repository:

```bash
git clone https://github.com/Karibusan/xrp-grid-trading-bot.git
cd xrp-grid-trading-bot
```

### 2. Create Required Directories

Create directories for data, logs, and backups:

```bash
mkdir -p data logs backups
```

### 3. Configuration

Copy the example configuration files:

```bash
cp config/config.json.example config/config.json
cp config/notification_config.json.example config/notification_config.json
cp config/error_handler_config.json.example config/error_handler_config.json
cp config/api_client_config.json.example config/api_client_config.json
cp config/signal_collapse_config.json.example config/signal_collapse_config.json
cp config/capital_migration_config.json.example config/capital_migration_config.json
cp config/strategic_bifurcation_config.json.example config/strategic_bifurcation_config.json
cp config/technological_convergence_config.json.example config/technological_convergence_config.json
cp config/survivability_config.json.example config/survivability_config.json
```

Modify the configuration files according to your needs, particularly:
- Add your Kraken API keys in `config/config.json`
- Add your Pushover credentials in `config/notification_config.json`

### 4. Build and Launch the Docker Container

Build and start the Docker container:

```bash
docker-compose up -d
```

### 5. Verify Operation

Check that the container is running correctly:

```bash
docker-compose logs -f
```

## Synology NAS Installation

### 1. Prerequisites

- Docker must be installed on your Synology NAS
- SSH access to the NAS

### 2. Create Required Directories

Connect to your NAS via SSH and create the necessary directories:

```bash
ssh your-username@your-nas-ip -p your-ssh-port
mkdir -p /volume1/docker/xrp-grid-trading-bot/config
mkdir -p /volume1/docker/xrp-grid-trading-bot/data
mkdir -p /volume1/docker/xrp-grid-trading-bot/logs
mkdir -p /volume1/docker/xrp-grid-trading-bot/backups
```

### 3. Download the Source Code

Clone the repository on your NAS:

```bash
cd /volume1/docker
git clone https://github.com/Karibusan/xrp-grid-trading-bot.git
cd xrp-grid-trading-bot
```

### 4. Configuration

Copy and modify the configuration files:

```bash
cp config/config.json.example config/config.json
cp config/notification_config.json.example config/notification_config.json
cp config/error_handler_config.json.example config/error_handler_config.json
cp config/api_client_config.json.example config/api_client_config.json
cp config/signal_collapse_config.json.example config/signal_collapse_config.json
cp config/capital_migration_config.json.example config/capital_migration_config.json
cp config/strategic_bifurcation_config.json.example config/strategic_bifurcation_config.json
cp config/technological_convergence_config.json.example config/technological_convergence_config.json
cp config/survivability_config.json.example config/survivability_config.json
```

Edit the files with a text editor like nano:

```bash
nano config/config.json
nano config/notification_config.json
```

### 5. Launch with Docker Compose

Start the Docker container:

```bash
docker-compose up -d
```

### 6. Configure Automatic Startup

To configure automatic startup when the NAS reboots, create a scheduled task in DSM:
1. Open the DSM Control Panel
2. Go to "Task Scheduler"
3. Create a new "Triggered" task
4. Set the trigger to "Boot-up"
5. Add the command: `cd /volume1/docker/xrp-grid-trading-bot && docker-compose up -d`

## Pushover Configuration

### 1. Create a Pushover Account

1. Go to [pushover.net](https://pushover.net) and create an account
2. Log in to your account
3. Note your User Key displayed on the main page

### 2. Create an Application

1. Scroll down to the "Your Applications" section at the bottom of the page
2. Click on "Create an Application/API Token"
3. Fill out the form:
   - Name: XRP Trading Bot
   - Type: Application
   - Description: Notifications for the XRP trading bot
   - URL: (leave empty or enter your GitHub repository URL)
   - Icon: (optional, you can upload an icon)
4. Accept the terms of service and click "Create Application"
5. Note the application token (API Token/Key) that is displayed

### 3. Configuration in the Bot

Open the `config/notification_config.json` file and add your Pushover credentials:

```json
{
    "pushover": {
        "enabled": true,
        "user_key": "YOUR_USER_KEY",
        "app_token": "YOUR_APPLICATION_TOKEN",
        "device": "",
        "sound": "pushover",
        "priority": 0
    },
    ...
}
```

### 4. Test Notifications

You can test notifications by running the test script:

```bash
python scripts/test_notifications.py
```

## Verifying the Installation

### 1. Check the Logs

Check the logs to ensure the bot is working correctly:

```bash
# Standard installation
tail -f logs/xrp_bot.log

# Docker installation
docker-compose logs -f
```

### 2. Verify Notifications

Make sure you receive Pushover notifications on your device.

### 3. Verify Orders

Log in to your Kraken account and verify that orders are being placed correctly.

## Troubleshooting

### Problem: The Bot Doesn't Start

**Solution:**
1. Check that all configuration files are correctly formatted (valid JSON)
2. Make sure the Kraken API keys are correct and have the necessary permissions
3. Check the logs for specific errors

### Problem: No Notifications

**Solution:**
1. Verify that the Pushover keys are correct
2. Make sure Pushover is enabled in the configuration
3. Check that notification levels are enabled
4. Run the notification test script

### Problem: Kraken API Errors

**Solution:**
1. Check that the API keys have the correct permissions
2. Make sure you haven't exceeded the API limits
3. Check your internet connection

### Problem: Errors in Specialized Modules

**Solution:**
1. Check the module-specific configuration files
2. Consult the error logs in `data/error_log.json`
3. Temporarily disable problematic modules in the main configuration

## Updating

To update the bot to the latest version:

```bash
# Standard installation
git pull
pip install -r requirements.txt

# Docker installation
git pull
docker-compose down
docker-compose up -d --build
```

## Backup

Use the provided backup script to back up your configurations and data:

```bash
./scripts/backup.sh
```

This will create a dated archive in the `backups/` directory containing all your configuration files and important data.

## Directory Structure

The bot requires the following directory structure:

```
xrp-grid-trading-bot/
├── src/                 # Source code
├── config/              # Configuration files
├── data/                # Data files and state
├── logs/                # Log files
├── backups/             # Backup archives
├── scripts/             # Utility scripts
└── tests/               # Test files
```

Make sure all these directories exist before running the bot. If they don't exist, create them using:

```bash
mkdir -p src config data logs backups scripts tests
```

The bot will store various files in these directories:
- `data/`: Trading state, error logs, and analytics
- `logs/`: Daily operation logs
- `backups/`: Automated backups of configuration and data

Ensuring these directories exist and have the correct permissions is essential for the bot to function properly.
