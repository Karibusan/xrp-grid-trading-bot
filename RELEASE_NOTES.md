# XRP Trading Bot v1.2.0 - Release Notes

## Advanced New Features

This version 1.2.0 introduces three new advanced configuration parameters that allow you to further optimize your trading strategy:

### 1. Dynamic Order Sizing
- Automatically adjusts order sizes based on their distance from the current price
- Optimizes capital allocation to maximize potential profits
- Places larger orders at the most profitable price levels

### 2. Configurable Stop-Loss Protection
- Defines a percentage drop that automatically triggers a stop-loss
- Protects your capital in case of significant market downturns
- Allows the bot to recreate the grid at lower price levels if necessary

### 3. Automatic Profit Reinvestment
- Automatically reinvests profits generated from sales
- Creates a self-sustaining trading cycle that maximizes capital utilization
- Particularly useful when starting with limited quote currency funds

## Additional Improvements

- **Non-Linear Price Distribution**: Implementation of a non-linear distribution of price levels for more efficient price movement capture
- **Detailed Report Generation**: New `--generate_report` command to analyze trading performance
- **Precise Margin Calculation**: Improved tracking and calculation of margins per transaction
- **Better Handling of Insufficient Funds**: Intelligent adaptation when quote currency funds are limited

## How to Update

1. Download the new `xrp_trading_bot_v1.2.0.py` script
2. Copy it to your Docker container:
   ```bash
   docker cp xrp_trading_bot_v1.2.0.py kraken_trading:/app/xrp_grid_trading.py
   ```
3. Restart your container:
   ```bash
   docker restart kraken_trading
   ```

## Documentation

See the new `docs/advanced_configuration.md` document for detailed instructions on using the new parameters and configuration recommendations for different market conditions.

## Configuration Examples

### Aggressive Configuration
```json
{
  "trading_pair": "XRPGBP",
  "grid_range_percentage": 4.5,
  "grid_levels": 18,
  "total_allocation": 200.0,
  "price_check_interval_minutes": 2,
  "trend_check_interval": 1,
  "dynamic_sizing": true,
  "stop_loss_percentage": 10.0,
  "profit_reinvestment": true
}
```

### Moderate Configuration
```json
{
  "trading_pair": "XRPGBP",
  "grid_range_percentage": 4.0,
  "grid_levels": 16,
  "total_allocation": 200.0,
  "price_check_interval_minutes": 3,
  "trend_check_interval": 2,
  "dynamic_sizing": true,
  "stop_loss_percentage": 12.0,
  "profit_reinvestment": true
}
```
