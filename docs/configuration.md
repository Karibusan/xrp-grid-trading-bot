# Configuration Guide for XRP Grid Trading Bot

This guide explains all configuration parameters and provides recommendations for optimizing your trading strategy.

## Configuration Parameters

The XRP Grid Trading Bot can be configured through command-line arguments or a configuration file. Here's a detailed explanation of each parameter:

### Basic Parameters

| Parameter | Description | Default | Recommended Range |
|-----------|-------------|---------|------------------|
| `trading_pair` | The trading pair on Kraken (e.g., XRPGBP, XRPUSD) | XRPGBP | Depends on your preferred currency |
| `grid_range_percentage` | The price range above and below current price | 3.5% | 2.0% - 5.0% |
| `grid_levels` | Number of price levels in the grid | 14 | 10 - 20 |
| `total_allocation` | Total XRP to allocate to the grid | 100.0 | Depends on your holdings |
| `price_check_interval_minutes` | How often to check price and update grid | 5 | 1 - 15 |
| `order_timeout_hours` | How long to keep unfilled orders before replacing | 48 | 24 - 72 |

### Advanced Parameters

These parameters are not directly configurable via command line but can be modified in the script:

| Parameter | Description | Default | Notes |
|-----------|-------------|---------|-------|
| `stop_loss_percentage` | Price drop that triggers stop-loss | 15% | Adjust based on risk tolerance |
| `trend_check_interval` | How often to analyze market trends | 6 hours | Lower for more adaptability |
| `daily_summary_interval` | How often to send performance reports | 24 hours | Can be reduced for more frequent updates |

## Configuration Methods

### Method 1: Command Line Arguments

Run the bot with specific parameters:

```bash
python xrp_trading_bot.py --trading_pair XRPGBP --grid_range_percentage 3.5 --grid_levels 14 --total_allocation 100.0 --price_check_interval_minutes 5 --order_timeout_hours 48 --enable_telegram
```

### Method 2: Configuration File

Create a `config.json` file in the `data` directory:

```json
{
  "trading_pair": "XRPGBP",
  "grid_range_percentage": 3.5,
  "grid_levels": 14,
  "total_allocation": 100.0,
  "price_check_interval_minutes": 5,
  "order_timeout_hours": 48
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

2. **Bearish Markets**:
   - Decreases grid range to minimize downside exposure
   - Reduces overall allocation for risk management

3. **Volatile Markets**:
   - Reduces allocation to minimize risk
   - Implements more conservative grid parameters

### Parameter Recommendations by Market Type

| Market Type | Grid Range | Grid Levels | Order Timeout |
|-------------|------------|-------------|---------------|
| Sideways | 2.5% - 3.5% | 14 - 16 | 48 hours |
| Bullish | 3.5% - 5.0% | 12 - 14 | 72 hours |
| Bearish | 2.0% - 3.0% | 16 - 20 | 24 hours |
| Volatile | 4.0% - 6.0% | 10 - 12 | 24 hours |

### Income Optimization

For maximizing income generation:

1. **Grid Density**:
   - Use more grid levels (14-16) for more trading opportunities
   - Tighter grid range (2.5%-3.5%) for more frequent trades

2. **Dynamic Sizing**:
   - The bot uses non-linear grid distribution for more efficient price capture
   - Larger sell orders are placed at higher prices for better profit

3. **Allocation Strategy**:
   - For income focus, allocate 70-80% of your XRP to the grid
   - Keep 20-30% in reserve for market opportunities

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
   - Simplified profit calculation
   - Performance over time

These metrics are saved to `data/performance_history.json` and can be analyzed to optimize your strategy.

## Configuration Examples

### Conservative Income Strategy

```json
{
  "trading_pair": "XRPGBP",
  "grid_range_percentage": 2.5,
  "grid_levels": 16,
  "total_allocation": 80.0,
  "price_check_interval_minutes": 5,
  "order_timeout_hours": 48
}
```

### Balanced Strategy

```json
{
  "trading_pair": "XRPGBP",
  "grid_range_percentage": 3.5,
  "grid_levels": 14,
  "total_allocation": 100.0,
  "price_check_interval_minutes": 5,
  "order_timeout_hours": 48
}
```

### Aggressive Strategy

```json
{
  "trading_pair": "XRPGBP",
  "grid_range_percentage": 5.0,
  "grid_levels": 12,
  "total_allocation": 120.0,
  "price_check_interval_minutes": 3,
  "order_timeout_hours": 72
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

To enable Telegram notifications:
1. Update the `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` in the script
2. Run with the `--enable_telegram` flag
