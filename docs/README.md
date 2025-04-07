# XRP Trading Bot Documentation

## Overview

The XRP Trading Bot is an advanced cryptocurrency trading system designed to automate trading of XRP (Ripple) on the Kraken exchange. The system implements a grid trading strategy with several advanced features to optimize performance and manage risk.

Version 2.0.0 introduces five advanced modules that significantly enhance the trading capabilities:

1. **Signal Collapse Detection** - Identifies when multiple technical indicators converge, indicating potential market risks
2. **Capital Migration** - Optimizes capital allocation across multiple trading pairs
3. **Strategic Bifurcation** - Automatically switches between different trading strategies based on market conditions
4. **Technological Convergence** - Integrates multiple data sources including technical analysis, sentiment analysis, and machine learning
5. **Survivability** - Ensures system resilience and continuity during adverse conditions

## Installation

### Prerequisites

- Python 3.8 or higher
- Docker (recommended for deployment)
- Kraken API key and secret

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/xrp-trading-bot.git
   cd xrp-trading-bot
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Configure the bot:
   - Copy `config/config.json.example` to `config/config.json`
   - Edit `config.json` to add your Kraken API credentials and adjust trading parameters
   - Copy each module's configuration example file and customize as needed

4. Create required directories:
   ```
   mkdir -p data backups
   ```

## Usage

### Running the Bot

To start the bot:

```
python src/enhanced_trading_system.py --config config/config.json
```

### Command Line Options

- `--config PATH` - Path to configuration file
- `--generate_report` - Generate a performance report and exit
- `--report_days N` - Number of days to include in report (default: 7)
- `--test` - Run a single trading cycle and exit (for testing)

### Docker Deployment

For production use, we recommend using Docker:

```
docker-compose up -d
```

## Configuration

The bot uses a hierarchical configuration system with a main config file and separate config files for each advanced module.

### Main Configuration

The main configuration file (`config.json`) contains the following parameters:

| Parameter | Description | Default |
|-----------|-------------|---------|
| trading_pair | Trading pair to use (e.g., XRPGBP) | XRPGBP |
| grid_range_percentage | Price range for grid in percentage | 4.0 |
| grid_levels | Number of grid levels | 16 |
| total_allocation | Total allocation in base currency | 100.0 |
| price_check_interval_minutes | Interval between price checks | 5 |
| order_timeout_hours | Timeout for orders | 24 |
| trend_check_interval | Interval for trend checks in hours | 6 |
| dynamic_sizing | Enable dynamic order sizing | true |
| stop_loss_percentage | Stop loss percentage | 12.0 |
| profit_reinvestment | Reinvest profits | true |
| api_key | Kraken API key | "" |
| api_secret | Kraken API secret | "" |
| data_dir | Directory for data files | "data" |
| log_file | Log file path | "data/trading_log.txt" |

### Module Configuration

Each advanced module has its own configuration file. See the example files in the `config` directory for details.

## Advanced Features

### Signal Collapse Detection

This module monitors multiple technical indicators and detects when they start showing high correlation, which can indicate increased market risk. When signal collapse is detected, the system automatically reduces risk exposure.

### Capital Migration

This module analyzes multiple trading pairs and optimizes capital allocation based on market opportunities. It can automatically migrate capital between different pairs to maximize returns.

### Strategic Bifurcation

This module implements multiple trading strategies and automatically switches between them based on detected market conditions. Strategies include:

- Trend Following
- Mean Reversion
- Range Trading
- Volatility Breakout

### Technological Convergence

This module integrates multiple data sources and analysis techniques:

- Technical Analysis
- Sentiment Analysis
- Machine Learning Predictions

It combines these inputs to generate trading recommendations with confidence levels.

### Survivability

This module implements resilience mechanisms to ensure the trading bot can continue to function effectively even when certain information sources or functionalities are compromised. Features include:

- System health monitoring
- Automatic backups
- Emergency mode with predefined actions
- Fallback APIs for price data

## Performance Monitoring

The bot generates performance reports that include:

- Price change percentage
- Volatility
- Maximum drawdown
- Number of completed orders
- Estimated profit

To generate a report:

```
python src/enhanced_trading_system.py --generate_report --report_days 30
```

## Troubleshooting

### Common Issues

1. **API Connection Errors**
   - Check your internet connection
   - Verify API key and secret
   - Ensure you have the correct permissions set for your API key

2. **Order Placement Failures**
   - Check account balance
   - Verify minimum order size requirements
   - Check for precision errors in price or volume

3. **High CPU/Memory Usage**
   - Adjust check intervals to reduce frequency
   - Disable unused modules
   - Reduce the number of grid levels

### Logs

Log files are stored in the `data` directory by default. Each module has its own log file for detailed troubleshooting.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
