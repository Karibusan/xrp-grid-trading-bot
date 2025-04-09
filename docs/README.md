# XRP Trading Bot Documentation v3.0.2

## Introduction

The XRP Trading Bot v3.0.2 is a major evolution of the automated trading system for the XRP/GBP pair. This new version brings significant improvements in reliability, error handling, notifications, and performance.

This document presents the architecture, features, and installation and configuration instructions for the bot v3.0.2.

## New Features

Version 3.0.2 introduces several major improvements over previous versions:

1. **Pushover notification system**: Replacement of Telegram with Pushover for more reliable and configurable notifications
2. **Advanced error handling**: Centralized system for error detection, logging, and recovery
3. **Optimized API client**: Rate limiting, caching, and robust error handling for the Kraken API
4. **Improved configuration management**: Configuration validation via JSON schemas and centralized management
5. **Unit tests**: Test coverage for all main components
6. **Enhanced security**: Better protection of API keys and sensitive data
7. **Complete documentation**: Comprehensive documentation in English

## System Architecture

The bot v3.0.2 is built around a modular architecture with the following components:

### Main Components

1. **EnhancedTradingSystem**: Main trading system that coordinates all other components
2. **NotificationManager**: Notification management via Pushover with different priority levels
3. **ErrorHandler**: Error detection, logging, and recovery
4. **APIClient**: Optimized interface for the Kraken API with caching and rate limiting
5. **ConfigManager**: Centralized configuration management with validation

### Specialized Modules

1. **SignalCollapseModule**: Analysis of market signals to detect potential collapses
2. **CapitalMigrationModule**: Tracking of capital movements between markets
3. **StrategicBifurcationModule**: Analysis of strategic bifurcations in the market
4. **TechnologicalConvergenceModule**: Evaluation of the impact of technological convergences
5. **SurvivabilityModule**: Analysis of system survival in extreme market conditions

## Installation

### Prerequisites

- Python 3.9 or higher
- Docker and Docker Compose (for container deployment)
- Kraken account with API keys
- Pushover account with user key and application token

### Standard Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Karibusan/xrp-grid-trading-bot.git
   cd xrp-grid-trading-bot
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Copy the example configuration files and modify them according to your needs:
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

4. Modify the configuration files to add your Kraken and Pushover API keys.

### Docker Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Karibusan/xrp-grid-trading-bot.git
   cd xrp-grid-trading-bot
   ```

2. Copy the example configuration files and modify them according to your needs:
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

3. Modify the configuration files to add your Kraken and Pushover API keys.

4. Launch the Docker container:
   ```bash
   docker-compose up -d
   ```

## Configuration

### Main Configuration

The `config/config.json` file contains the main configuration of the bot:

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
    "api_key": "YOUR_KRAKEN_API_KEY",
    "api_secret": "YOUR_KRAKEN_API_SECRET",
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

### Notification Configuration

The `config/notification_config.json` file contains the configuration of the notification system:

```json
{
    "pushover": {
        "enabled": true,
        "user_key": "YOUR_PUSHOVER_USER_KEY",
        "app_token": "YOUR_PUSHOVER_APP_TOKEN",
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

### Error Handler Configuration

The `config/error_handler_config.json` file contains the configuration of the error handler:

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

### API Client Configuration

The `config/api_client_config.json` file contains the configuration of the API client:

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

## Usage

### Starting the Bot

To start the bot in standard mode:

```bash
python src/main.py
```

To start the bot with a specific configuration file:

```bash
python src/main.py --config path/to/config.json
```

### Available Commands

The bot supports the following commands:

- `--config`: Specifies the path to the main configuration file
- `--debug`: Activates debug mode (detailed logging)
- `--test`: Runs the bot in test mode (without placing real orders)
- `--reset`: Resets the bot's state before starting

### Monitoring and Maintenance

#### Logs

Logs are stored in the `logs/` directory and are organized by date.

#### Backup

A backup script is provided to back up configurations and data:

```bash
./scripts/backup.sh
```

#### Updating

To update the bot, pull the latest changes from the repository and restart:

```bash
git pull
docker-compose down
docker-compose up -d
```

## Troubleshooting

### Common Issues

#### The bot doesn't execute trades

- Check that your API keys are valid and have the necessary permissions
- Verify that the trading pair is available on Kraken
- Check the logs for any errors
- Ensure all module configurations are correct

#### Pushover notifications not working

- Verify your Pushover user key and application token
- Check that the notification levels are enabled in the configuration
- Ensure your device is registered with Pushover

#### Docker container fails to start

- Check that all required directories exist
- Verify that the configuration files are valid JSON
- Check Docker logs for detailed error messages

## Advanced Features

### Specialized Modules

#### Signal Collapse Module

This module analyzes market signals to detect potential market collapses. It uses a combination of technical indicators and market sentiment analysis.

#### Capital Migration Module

This module tracks capital movements between different markets and cryptocurrencies to identify potential opportunities or risks.

#### Strategic Bifurcation Module

This module analyzes strategic bifurcations in the market, identifying divergences in trading patterns that could indicate future price movements.

#### Technological Convergence Module

This module evaluates the impact of technological convergences on the XRP price, including regulatory news, partnerships, and technical developments.

#### Survivability Module

This module analyzes the system's ability to survive in extreme market conditions, implementing protective measures when necessary.

## Security Considerations

- Store your API keys securely
- Use API keys with the minimum necessary permissions
- Regularly rotate your API keys
- Monitor your account for unauthorized activity
- Use strong passwords for your Kraken and Pushover accounts

## Support and Contribution

For support or to contribute to the project, please visit the GitHub repository:
https://github.com/Karibusan/xrp-grid-trading-bot
