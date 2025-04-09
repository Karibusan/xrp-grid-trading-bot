# XRP Grid Trading Bot v3.0.2

![Version](https://img.shields.io/badge/version-3.0.2-blue)
![Python](https://img.shields.io/badge/python-3.9-green)
![License](https://img.shields.io/badge/license-MIT-orange)

An automated trading bot for XRP grid trading on Kraken, with advanced analysis modules and a Pushover notification system.

## New Features in v3.0.2

- **Fixed module integration**: All specialized modules from v2.0 now properly integrated
- **Enhanced error handling**: Improved error detection and recovery in all modules
- **Improved Pushover notifications**: Added dedicated notification levels with proper configuration
- **Updated deployment scripts**: Better support for Synology NAS deployment
- **Manual deployment instructions**: Added special instructions for macOS users
- **English documentation**: All documentation translated to English

## Features from v3.0.0

- **Pushover notification system**: Replacement of Telegram with Pushover featuring different notification levels (trades, daily reports, efficiency, errors, debugging)
- **Robust error handling**: Centralized system for error detection, logging, and recovery
- **Optimized API client**: Rate limiting and caching to reduce API calls
- **Advanced configuration management**: Configuration validation via JSON schemas
- **Unit tests** for all main components
- **Comprehensive documentation**

## Prerequisites

- Python 3.9 or higher
- Kraken account with API keys
- Pushover account with user key and application token
- Docker and Docker Compose (optional, for containerized deployment)

## Quick Installation

### Standard Installation

```bash
# Clone the repository
git clone https://github.com/Karibusan/xrp-grid-trading-bot.git
cd xrp-grid-trading-bot

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure the bot
cp config/config.json.example config/config.json
cp config/notification_config.json.example config/notification_config.json
cp config/error_handler_config.json.example config/error_handler_config.json
cp config/api_client_config.json.example config/api_client_config.json
cp config/signal_collapse_config.json.example config/signal_collapse_config.json
cp config/capital_migration_config.json.example config/capital_migration_config.json
cp config/strategic_bifurcation_config.json.example config/strategic_bifurcation_config.json
cp config/technological_convergence_config.json.example config/technological_convergence_config.json
cp config/survivability_config.json.example config/survivability_config.json

# Modify configuration files to add your API keys

# Launch the bot
python src/main.py
```

### Docker Installation

```bash
# Clone the repository
git clone https://github.com/Karibusan/xrp-grid-trading-bot.git
cd xrp-grid-trading-bot

# Configure the bot (as above)

# Launch with Docker Compose
docker-compose up -d
```

## Configuration

The bot uses multiple JSON configuration files:

- `config/config.json`: Main configuration
- `config/notification_config.json`: Pushover notification configuration
- `config/error_handler_config.json`: Error handling configuration
- `config/api_client_config.json`: API client configuration
- `config/signal_collapse_config.json`: Signal collapse module configuration
- `config/capital_migration_config.json`: Capital migration module configuration
- `config/strategic_bifurcation_config.json`: Strategic bifurcation module configuration
- `config/technological_convergence_config.json`: Technological convergence module configuration
- `config/survivability_config.json`: Survivability module configuration

See the [advanced configuration documentation](docs/advanced_configuration.md) for more details.

## Specialized Modules

The bot integrates several advanced analysis modules:

- **Signal Collapse**: Detects potential market collapses
- **Capital Migration**: Tracks capital movements between markets
- **Strategic Bifurcation**: Analyzes strategic bifurcations in the market
- **Technological Convergence**: Evaluates the impact of technological convergences
- **Survivability**: Analyzes the system's ability to survive in extreme market conditions

## Documentation

- [Detailed installation guide](docs/installation.md)
- [Advanced configuration](docs/advanced_configuration.md)
- [Notification system](docs/notification_system.md)
- [Implementation guide](IMPLEMENTATION_GUIDE.md)
- [Changelog](CHANGELOG.md)

## Utility Scripts

- `scripts/backup.sh`: Backup configurations and data
- `scripts/deploy_to_synology.sh`: Deployment to Synology NAS
- `scripts/deploy_to_synology_with_password.sh`: Password-based deployment to Synology NAS
- `scripts/test_notifications.py`: Test Pushover notifications

## Troubleshooting

If you encounter issues:

1. Check the logs in the `logs/` directory
2. Consult the error file in `data/error_log.json`
3. Ensure your API keys are correct and have the necessary permissions
4. Verify your Pushover configuration
5. For Synology deployment issues, refer to the manual deployment instructions

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a branch for your feature
3. Add your changes
4. Submit a pull request

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments

- Kraken for their API
- Pushover for their notification service
- All contributors and users of the bot
