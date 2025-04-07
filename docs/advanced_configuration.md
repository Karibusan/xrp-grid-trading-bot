# Advanced Configuration of the XRP Trading Bot

This document details the new advanced configuration parameters added in version 1.2.0 of the XRP trading bot.

## New Configuration Parameters

### 1. Dynamic Sizing

**Parameter**: `dynamic_sizing`  
**Type**: Boolean (true/false)  
**Default value**: false  
**Description**: Activates dynamic order sizing based on distance from the current price.

When this option is enabled:
- Buy orders are larger near the current price and gradually decrease for more distant levels
- Sell orders are larger far from the current price and gradually decrease for closer levels
- This strategy optimizes capital allocation to maximize potential profits

**Configuration example**:
```json
{
  "dynamic_sizing": true
}
```

**Command line**:
```bash
python xrp_trading_bot.py --dynamic_sizing
```

### 2. Stop Loss Percentage

**Parameter**: `stop_loss_percentage`  
**Type**: Floating point number  
**Default value**: 15.0  
**Description**: Defines the percentage drop in price that will trigger a stop-loss.

When the price drops by more than this percentage from the initial price:
- All current orders are canceled
- The bot waits one hour for the market to stabilize
- The grid is recreated with new parameters adapted to the current market
- This protection prevents significant losses during major market downturns

**Configuration example**:
```json
{
  "stop_loss_percentage": 12.5
}
```

**Command line**:
```bash
python xrp_trading_bot.py --stop_loss_percentage 12.5
```

### 3. Profit Reinvestment

**Parameter**: `profit_reinvestment`  
**Type**: Boolean (true/false)  
**Default value**: false  
**Description**: Activates automatic reinvestment of profits generated from sales.

When this option is enabled:
- After each successful sell order, the profit is calculated
- If the profit is sufficient, a new buy order is automatically placed at a price slightly below the current price
- This mechanism creates a self-sustaining trading cycle that maximizes capital utilization
- Particularly useful when starting with limited quote currency funds (GBP)

**Configuration example**:
```json
{
  "profit_reinvestment": true
}
```

**Command line**:
```bash
python xrp_trading_bot.py --profit_reinvestment
```

## Complete Optimized Configuration

Here is an example of a complete configuration using all the new parameters for an aggressive strategy:

```json
{
  "trading_pair": "XRPGBP",
  "grid_range_percentage": 4.2,
  "grid_levels": 16,
  "total_allocation": 200.0,
  "price_check_interval_minutes": 3,
  "order_timeout_hours": 24,
  "trend_check_interval": 1,
  "dynamic_sizing": true,
  "stop_loss_percentage": 12.0,
  "profit_reinvestment": true
}
```

## Using the New Parameters

### Via Configuration File

1. Create or modify the `data/config.json` file:
```json
{
  "trading_pair": "XRPGBP",
  "grid_range_percentage": 4.2,
  "grid_levels": 16,
  "total_allocation": 200.0,
  "price_check_interval_minutes": 3,
  "order_timeout_hours": 24,
  "trend_check_interval": 1,
  "dynamic_sizing": true,
  "stop_loss_percentage": 12.0,
  "profit_reinvestment": true
}
```

2. Launch the bot with the file configuration option:
```bash
python xrp_trading_bot.py --config_file
```

### Via Command Line

Use the new parameters directly in the command line:

```bash
python xrp_trading_bot.py --trading_pair XRPGBP --grid_range_percentage 4.2 --grid_levels 16 --total_allocation 200.0 --price_check_interval_minutes 3 --order_timeout_hours 24 --trend_check_interval 1 --dynamic_sizing --stop_loss_percentage 12.0 --profit_reinvestment
```

## Usage Recommendations

### Aggressive Strategy (High Volatility)

```json
{
  "grid_range_percentage": 4.5,
  "grid_levels": 18,
  "price_check_interval_minutes": 2,
  "trend_check_interval": 1,
  "dynamic_sizing": true,
  "stop_loss_percentage": 10.0,
  "profit_reinvestment": true
}
```

### Moderate Strategy (Medium Volatility)

```json
{
  "grid_range_percentage": 4.0,
  "grid_levels": 16,
  "price_check_interval_minutes": 3,
  "trend_check_interval": 2,
  "dynamic_sizing": true,
  "stop_loss_percentage": 12.0,
  "profit_reinvestment": true
}
```

### Conservative Strategy (Low Volatility)

```json
{
  "grid_range_percentage": 3.5,
  "grid_levels": 14,
  "price_check_interval_minutes": 5,
  "trend_check_interval": 4,
  "dynamic_sizing": false,
  "stop_loss_percentage": 15.0,
  "profit_reinvestment": false
}
```

## Performance Monitoring and Analysis

With these new parameters, it's even more important to monitor your bot's performance. Use the new report feature to analyze the results:

```bash
python xrp_trading_bot.py --generate_report
```

This will generate a detailed report of transactions and margins for the last 7 days. You can specify a different period:

```bash
python xrp_trading_bot.py --generate_report --report_days 30
```

## Conclusion

These new configuration parameters offer considerably increased flexibility and power for your XRP trading bot. Experiment with different combinations to find the configuration that works best in current market conditions.

Remember that more aggressive parameters can generate more profits but also carry more risks. Start with modest allocations until you're comfortable with the bot's behavior under different configurations.
