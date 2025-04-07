# Trade Tracking and Margin Calculation

This document explains the trade tracking and margin calculation features added to the XRP Grid Trading Bot.

## Overview

The bot now includes a comprehensive trade tracking system that records individual trades and calculates precise margins. This addresses the need to know exactly how much profit each trade generates and provides detailed performance metrics.

## Key Features

### Individual Trade Tracking

Each trade is now tracked with a unique ID and comprehensive metadata:

- **Trade ID**: Unique identifier for each trade (UUID)
- **Order Type**: Buy or sell
- **Price and Volume**: The price and amount of XRP for the order
- **Status**: Pending, open, filled, canceled, or failed
- **Timestamps**: Creation time, update time, and fill time
- **Execution Details**: Actual execution price, filled volume, cost, and fees

### Trade Database

All trades are stored in a persistent database:

```
data/trades/trades.json
```

This database maintains a complete history of all trading activity and provides methods to:

- Add new trades
- Update existing trades
- Query trades by various criteria
- Calculate margins between buy and sell trades

### Margin Calculation

The bot implements a sophisticated margin calculation algorithm that:

1. Indexes all filled buy orders by price level
2. For each filled sell order, finds buy orders at lower prices
3. Matches sell orders with buy orders to calculate margins
4. Handles partial fills and multiple matches correctly
5. Calculates both absolute margin and percentage margin

### Performance Reporting

The bot now provides detailed performance reports:

- **Daily Summaries**: Sent via Telegram with key metrics
- **Trade Reports**: Generated on demand with comprehensive statistics
- **Performance History**: Saved to `data/performance_history.json`

## Using the Trade Tracking Features

### Generating Reports

You can generate a detailed trade report at any time:

```bash
python xrp_trading_bot.py --generate_report
```

This creates a comprehensive report with:

- Total trades executed
- Buy/sell volumes
- Costs and revenues
- Detailed margin calculations
- Recent trade history

You can specify the number of days to include:

```bash
python xrp_trading_bot.py --generate_report --report_days 30
```

### Viewing Performance Metrics

The bot sends daily performance summaries via Telegram (when enabled):

```
XRP Grid Trading Daily Summary:

Current XRPGBP price: 0.5123
Current XRP balance: 95.4321
Current GBP balance: 25.6789
Active orders: 12
Total trades: 48
Filled trades: 36
Total margin: 12.3456
Average margin %: 4.56%
```

### Accessing Trade Data

All trade data is stored in JSON format and can be accessed for further analysis:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "pair": "XRPGBP",
  "type": "buy",
  "price": 0.5000,
  "volume": 20.0,
  "status": "filled",
  "created_at": 1712345678,
  "updated_at": 1712345789,
  "filled_at": 1712345789,
  "order_id": "ABCDEF-12345-67890",
  "filled_volume": 20.0,
  "actual_price": 0.5000,
  "cost": 10.0,
  "fee": 0.026
}
```

## Implementation Details

### TradeDatabase Class

The `TradeDatabase` class manages all trade records:

```python
class TradeDatabase:
    def __init__(self, data_dir='data/trades'):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.trades_file = os.path.join(data_dir, 'trades.json')
        self.trades = self._load_trades()
    
    # Methods for managing trades
    def add_trade(self, trade):
        """Add a new trade to the database"""
        
    def update_trade(self, trade_id, updates):
        """Update an existing trade"""
        
    def get_trade_by_order_id(self, order_id):
        """Find a trade by its order ID"""
        
    def calculate_margins(self):
        """Calculate margins for completed trade pairs"""
        
    def get_performance_summary(self):
        """Get a summary of trading performance"""
```

### Order Lifecycle Tracking

The bot tracks the complete lifecycle of each order:

1. **Creation**: When an order is placed, a trade record is created with status "pending"
2. **Confirmation**: When the order is confirmed by Kraken, status changes to "open"
3. **Execution**: When the order is filled, status changes to "filled" with execution details
4. **Cancellation**: If the order is canceled, status changes to "canceled"
5. **Failure**: If the order fails, status changes to "failed" with error details

### Margin Calculation Algorithm

The margin calculation algorithm matches sell orders with buy orders:

```python
def calculate_margins(self):
    """Calculate margins for completed trade pairs"""
    buy_trades = {}
    margins = []
    
    # First, index all buy trades by price level
    for trade in self.trades:
        if trade.get('type') == 'buy' and trade.get('status') == 'filled':
            price_level = trade.get('price')
            if price_level not in buy_trades:
                buy_trades[price_level] = []
            buy_trades[price_level].append(trade)
    
    # Then match sell trades with buy trades
    for trade in self.trades:
        if trade.get('type') == 'sell' and trade.get('status') == 'filled':
            sell_price = trade.get('price')
            sell_volume = trade.get('volume')
            
            # Find buy trades at lower prices
            for buy_price in sorted(buy_trades.keys()):
                if buy_price < sell_price and buy_trades[buy_price]:
                    # Calculate margin
                    # ...
```

## Benefits

With these enhancements, you can now:

1. Track the exact profit/loss of each trade
2. Understand your trading performance in detail
3. Identify which price levels are most profitable
4. Make data-driven decisions to optimize your strategy
5. Have confidence in the accuracy of your trading results

The bot now provides complete transparency into your trading activity and profitability, addressing the feedback about tracking individual trades and calculating margins per trade.
