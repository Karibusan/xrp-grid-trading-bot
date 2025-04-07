# XRP Grid Trading Bot

An income-focused XRP grid trading bot with Docker deployment for Synology NAS.

## Features

- **Non-linear Grid Distribution**: More efficient price capture than traditional linear grids
- **Dynamic Order Sizing**: Larger orders at more profitable price points
- **Market Trend Analysis**: Automatically adapts to market conditions
- **Performance Tracking**: Comprehensive metrics and reporting
- **Docker Deployment**: Easy setup on Synology NAS with automatic restart
- **Telegram Notifications**: Real-time updates on trading activities
- **Automatic Backups**: Daily backups and weekly log rotation
- **Income-Focused Strategy**: Designed to generate income from existing XRP holdings
- **Stop-Loss Protection**: Configurable protection against market downturns
- **Profit Reinvestment**: Automatic reinvestment of profits for compound growth

## Prerequisites

- Synology NAS with Docker package installed
- Kraken account with API keys
- Telegram bot (optional but recommended)
- Basic knowledge of Docker and Linux commands

## Quick Start

1. Clone this repository to your local machine
2. Update API credentials in `src/xrp_trading_bot.py`
3. Copy files to your Synology NAS
4. Deploy using Docker Compose

```bash
# On your Synology NAS
mkdir -p /volume1/docker/xrp_trading_bot/data
cp xrp_trading_bot.py /volume1/docker/xrp_trading_bot/
cp docker-compose.yml /volume1/docker/xrp_trading_bot/
cd /volume1/docker/xrp_trading_bot
docker-compose up -d
```

## Detailed Documentation

- [Setup Guide](docs/setup.md): Detailed installation instructions
- [Configuration Guide](docs/configuration.md): Explanation of all parameters
- [Architecture](docs/architecture.md): How the grid trading strategy works
- [Advanced Configuration](docs/advanced_configuration.md): New v1.2.0 features

## Grid Trading Strategy

This bot implements a grid trading strategy optimized for income generation:

1. Creates a non-linear price grid around the current XRP price
2. Places buy orders below current price and sell orders above
3. Uses dynamic order sizing for more efficient capital allocation
4. Adapts grid parameters based on market trends
5. Monitors and maintains the grid, recreating it when necessary
6. Implements stop-loss protection for capital preservation
7. Reinvests profits for compound growth (optional)

The strategy is specifically designed to work with existing XRP holdings without requiring additional funds.

## Configuration

Example configuration:

```json
{
  "trading_pair": "XRPGBP",
  "grid_range_percentage": 4.0,
  "grid_levels": 16,
  "total_allocation": 200.0,
  "price_check_interval_minutes": 3,
  "order_timeout_hours": 24,
  "trend_check_interval": 2,
  "dynamic_sizing": true,
  "stop_loss_percentage": 12.0,
  "profit_reinvestment": true
}
```

## Performance Monitoring

Generate detailed performance reports with:

```bash
python xrp_trading_bot.py --generate_report
```

## Disclaimer

**IMPORTANT**: This trading bot is provided for educational and informational purposes only. Cryptocurrency trading involves significant risk and you could lose your investment. Always start with small amounts and never trade with money you cannot afford to lose.

This project does not constitute financial advice. Users should conduct their own research and consult with financial professionals before making investment decisions.

Never share your API keys or credentials. This project requires API keys with trading permissions, which should be secured appropriately. The developers of this project are not responsible for any security breaches related to your API keys.

Past performance is not indicative of future results. The effectiveness of grid trading strategies varies with market conditions.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Developed with assistance from [Manus](https://manus.im/)
- Uses [krakenex](https://github.com/veox/python3-krakenex) and [pykrakenapi](https://github.com/dominiktraxl/pykrakenapi) for Kraken API interaction
