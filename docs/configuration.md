# Configuration Guide for XRP Grid Trading Bot

This guide explains all configuration parameters and provides recommendations for optimizing your trading strategy.

## Configuration Parameters

The XRP Grid Trading Bot can be configured through command-line arguments or a configuration file. Here's a detailed explanation of each parameter:

### Basic Parameters

| Parameter | Description | Default | Recommended Range |
|-----------|-------------|---------|------------------|
| `trading_pair` | The trading pair on Kraken (e.g., XRPGBP, XRPUSD) | XRPGBP | Depends on your preferred currency |
| `grid_range_percentage` | The price range above and below current price | 4.0% | 2.0% - 5.0% |
| `grid_levels` | Number of price levels in the grid | 16 | 10 - 20 |
| `total_allocation` | Total XRP to allocate to the grid | 200.0 | Depends on your holdings |
| `price_check_interval_minutes` | How often to check price and update grid | 3 | 1 - 15 |
| `order_timeout_hours` | How long to keep unfilled orders before replacing | 24 | 24 - 72 |
| `trend_check_interval` | How often to analyze market trends (hours) | 2 | 1 - 6 |

### New Advanced Parameters (v1.2.0)

| Parameter | Description | Default | Recommended Range |
|-----------|-------------|---------|------------------|
| `dynamic_sizing` | Enables dynamic order sizing based on distance from price | false | true/false |
| `stop_loss_percentage` | Price drop that triggers stop-loss | 15.0% | 10.0% - 20.0% |
| `profit_reinvestment` | Automatically reinvests profits from sales | false | true/false |

For detailed information about these new parameters, see [Advanced Configuration](advanced_configuration.md).

## Configuration Methods

### Method 1: Command Line Arguments

Run the bot with specific parameters:

```bash
python xrp_trading_bot.py --trading_pair XRPGBP --grid_range_percentage 4.0 --grid_levels 16 --total_allocation 200.0 --price_check_interval_minutes 3 --order_timeout_hours 24 --trend_check_interval 2 --dynamic_sizing --stop_loss_percentage 12.0 --profit_reinvestment --enable_telegram
```

### Method 2: Configuration File

Create a `config.json` file in the `data` directory:

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

Then run with the `--config_file` flag:

```bash
python xrp_trading_bot.py --config_file --enable_telegram
```

## Strategy Optimization

### Market Condition Adaptations

The bot automatically adapts to different market conditions:

1. **Bullish Markets**:
   - Increases grid range to capture more upside
   - Adjusts allocation to prioritize sell orders
   - Uses dynamic sizing for better profit capture

2. **Bearish Markets**:
   - Decreases grid range to minimize downside exposure
   - Reduces overall allocation for risk management
   - Relies on stop-loss protection to limit losses

3. **Volatile Markets**:
   - Reduces allocation to minimize risk
   - Implements more conservative grid parameters
   - Uses profit reinvestment to capitalize on price swings

### Parameter Recommendations by Market Type

| Market Type | Grid Range | Grid Levels | Dynamic Sizing | Stop Loss | Profit Reinvestment |
|-------------|------------|-------------|----------------|-----------|---------------------|
| Sideways | 3.5% - 4.0% | 16 - 18 | true | 15.0% | true |
| Bullish | 4.0% - 5.0% | 14 - 16 | true | 12.0% | true |
| Bearish | 2.5% - 3.5% | 18 - 20 | false | 10.0% | false |
| Volatile | 4.5% - 6.0% | 12 - 14 | true | 10.0% | true |

### Income Optimization

For maximizing income generation:

1. **Grid Density**:
   - Use more grid levels (16-18) for more trading opportunities
   - Moderate grid range (3.5%-4.5%) for balanced trade frequency and profit

2. **Dynamic Sizing**:
   - Enable dynamic sizing for more efficient capital allocation
   - Places larger buy orders near current price and larger sell orders at distant levels

3. **Profit Reinvestment**:
   - Enable profit reinvestment to create a self-sustaining trading cycle
   - Particularly effective when starting with limited quote currency (GBP)

4. **Stop-Loss Protection**:
   - Set stop-loss percentage based on your risk tolerance (10%-15% recommended)
   - Protects capital during significant market downturns

## Performance Monitoring

The bot tracks several performance metrics:

1. **Trade Statistics**:
   - Total trades executed
   - Success rate
   - Trade frequency

2. **Volume Metrics**:
   - Buy volume
   - Sell volume
   - Net position change

3. **Profit Estimation**:
   - Precise margin calculation per transaction
   - Performance over time

These metrics are saved to `data/performance_history.json` and can be analyzed to optimize your strategy.

You can also generate detailed reports using:

```bash
python xrp_trading_bot.py --generate_report
```

## Configuration Examples

### Conservative Income Strategy

```json
{
  "trading_pair": "XRPGBP",
  "grid_range_percentage": 3.5,
  "grid_levels": 14,
  "total_allocation": 150.0,
  "price_check_interval_minutes": 5,
  "order_timeout_hours": 48,
  "trend_check_interval": 4,
  "dynamic_sizing": false,
  "stop_loss_percentage": 15.0,
  "profit_reinvestment": false
}
```

### Balanced Strategy

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

### Aggressive Strategy

```json
{
  "trading_pair": "XRPGBP",
  "grid_range_percentage": 4.5,
  "grid_levels": 18,
  "total_allocation": 250.0,
  "price_check_interval_minutes": 2,
  "order_timeout_hours": 24,
  "trend_check_interval": 1,
  "dynamic_sizing": true,
  "stop_loss_percentage": 10.0,
  "profit_reinvestment": true
}
```

## Telegram Notifications

When enabled, the bot sends several types of notifications:

1. **Order Notifications**:
   - New orders placed
   - Orders filled
   - Orders cancelled

2. **Performance Reports**:
   - Daily summaries
   - Performance metrics
   - Account balance updates

3. **Error Notifications**:
   - API connection issues
   - Order placement failures
   - Critical errors

4. **Stop-Loss Notifications**:
   - Alerts when stop-loss is triggered
   - Grid recreation notifications

To enable Telegram notifications:
1. Update the `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` in the script
2. Run with the `--enable_telegram` flag
