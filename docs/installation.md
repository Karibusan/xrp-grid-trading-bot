# Installation Guide

This guide provides step-by-step instructions for installing and setting up the XRP Trading Bot v2.0.0.

## System Requirements

- Python 3.8 or higher
- 2GB RAM minimum (4GB+ recommended)
- 1GB free disk space
- Internet connection
- Kraken account with API access

## Installation Methods

### Method 1: Direct Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/xrp-trading-bot.git
   cd xrp-trading-bot
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Create required directories**:
   ```bash
   mkdir -p data backups
   ```

4. **Configure the bot**:
   - Copy configuration examples:
     ```bash
     cp config/config.json.example config/config.json
     cp config/signal_collapse_config.json.example data/signal_collapse_config.json
     cp config/capital_migration_config.json.example data/capital_migration_config.json
     cp config/strategic_bifurcation_config.json.example data/strategic_bifurcation_config.json
     cp config/technological_convergence_config.json.example data/technological_convergence_config.json
     cp config/survivability_config.json.example data/survivability_config.json
     ```
   - Edit `config/config.json` to add your Kraken API credentials and adjust trading parameters

5. **Run the bot**:
   ```bash
   python src/enhanced_trading_system.py --config config/config.json
   ```

### Method 2: Docker Installation (Recommended)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/xrp-trading-bot.git
   cd xrp-trading-bot
   ```

2. **Configure the bot**:
   - Copy configuration examples:
     ```bash
     cp config/config.json.example config/config.json
     mkdir -p data
     cp config/*.json.example data/
     ```
   - Edit `config/config.json` to add your Kraken API credentials and adjust trading parameters
   - Rename the example config files in the data directory:
     ```bash
     for file in data/*.json.example; do mv "$file" "${file%.example}"; done
     ```

3. **Build and start the Docker container**:
   ```bash
   docker-compose up -d
   ```

4. **Check the logs**:
   ```bash
   docker-compose logs -f
   ```

### Method 3: Synology NAS Installation

1. **Install Docker on your Synology NAS** through the Package Center

2. **Create directories on your NAS**:
   - Create a shared folder named `xrp_trading_bot`
   - Inside this folder, create the following structure:
     ```
     xrp_trading_bot/
     ├── config/
     ├── data/
     ├── backups/
     ├── src/
     └── docker-compose.yml
     ```

3. **Copy files to your NAS**:
   - Copy all source files to the `src` directory
   - Copy configuration examples to the `config` directory
   - Copy the `docker-compose.yml` file to the root directory

4. **Configure the bot**:
   - Edit `config/config.json` to add your Kraken API credentials and adjust trading parameters
   - Copy configuration files to the data directory:
     ```bash
     cp config/*.json.example data/
     ```
   - Rename the example config files in the data directory:
     ```bash
     for file in data/*.json.example; do mv "$file" "${file%.example}"; done
     ```

5. **Launch the Docker container**:
   - Open Docker in the Synology DSM
   - Go to Registry and search for "python"
   - Download the official Python image (python:3.9)
   - Go to Container and click Create
   - Select "Import from docker-compose.yml"
   - Browse to your docker-compose.yml file
   - Click Next and then Apply

6. **Set up automatic startup**:
   - In the Docker application, select your container
   - Click Settings
   - Check "Enable auto-restart"

## Configuration

After installation, you need to configure the bot with your Kraken API credentials and trading parameters.

### Obtaining Kraken API Credentials

1. Log in to your Kraken account
2. Go to Security > API
3. Click "Add API Key"
4. Set the following permissions:
   - Query Funds
   - Query Open Orders & Trades
   - Query Closed Orders & Trades
   - Create & Modify Orders
5. Save the API key and secret

### Configuring the Bot

Edit `config/config.json` and add your API credentials:

```json
{
  "api_key": "your-api-key",
  "api_secret": "your-api-secret",
  "trading_pair": "XRPGBP",
  "grid_range_percentage": 4.0,
  "grid_levels": 16,
  "total_allocation": 100.0
}
```

## Verification

To verify that the installation was successful:

1. Run the bot in test mode:
   ```bash
   python src/enhanced_trading_system.py --test
   ```

2. Check the output for any errors

3. Verify that the bot can connect to the Kraken API and retrieve the current price

## Troubleshooting

### Common Installation Issues

1. **Missing dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Permission errors**:
   ```bash
   chmod +x src/*.py
   ```

3. **Docker issues**:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

4. **API connection errors**:
   - Check your internet connection
   - Verify API key and secret
   - Ensure you have the correct permissions set for your API key

### Getting Help

If you encounter any issues during installation, please:

1. Check the logs in the `data` directory
2. Refer to the troubleshooting section in the main documentation
3. Open an issue on the GitHub repository

## Next Steps

After successful installation:

1. Review the [Advanced Configuration Guide](advanced_configuration.md) to optimize your trading parameters
2. Set up [Telegram notifications](telegram_setup.md) for real-time alerts
3. Configure [automatic backups](backup_configuration.md) to protect your trading data
