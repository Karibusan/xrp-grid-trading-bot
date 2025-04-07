#!/usr/bin/env python3

import os
import sys
import argparse
import time
import json
import pandas as pd
import numpy as np
import krakenex
from pykrakenapi import KrakenAPI
import datetime
import logging
import requests  # For Telegram notifications
import uuid  # For generating unique trade IDs

# Create necessary directories
os.makedirs('data', exist_ok=True)
os.makedirs('data/trades', exist_ok=True)  # Directory for individual trade records

# Set up logging
log_dir = 'data'
log_file = os.path.join(log_dir, 'trading_log.txt')
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# API credentials - replace with your actual credentials
API_KEY = "YOUR_KRAKEN_API_KEY_HERE"
API_SECRET = "YOUR_KRAKEN_API_SECRET_HERE"

# Telegram configuration - replace with your actual values
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN_HERE"
TELEGRAM_CHAT_ID = "YOUR_TELEGRAM_CHAT_ID_HERE"

# Flag to enable/disable Telegram notifications
ENABLE_TELEGRAM = False  # Set to True to enable Telegram notifications

# Trading performance tracking
trading_stats = {
    "total_trades": 0,
    "successful_trades": 0,
    "failed_trades": 0,
    "buy_volume": 0,
    "sell_volume": 0,
    "estimated_profit": 0,
    "start_time": time.time(),
    "last_report_time": time.time(),
    "trades": []  # List to store individual trade records
}

# Initialize Kraken API
kraken = krakenex.API(API_KEY, API_SECRET)
api = KrakenAPI(kraken)

# Trade database
class TradeDatabase:
    def __init__(self, data_dir='data/trades'):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.trades_file = os.path.join(data_dir, 'trades.json')
        self.trades = self._load_trades()
        
    def _load_trades(self):
        """Load existing trades from file"""
        if os.path.exists(self.trades_file):
            try:
                with open(self.trades_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logging.error(f"Error loading trades: {e}")
                return []
        return []
    
    def save_trades(self):
        """Save trades to file"""
        try:
            with open(self.trades_file, 'w') as f:
                json.dump(self.trades, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving trades: {e}")
    
    def add_trade(self, trade):
        """Add a new trade to the database"""
        self.trades.append(trade)
        self.save_trades()
        
    def get_trades(self, status=None, trade_type=None, limit=None):
        """Get trades with optional filtering"""
        result = self.trades
        
        if status:
            result = [t for t in result if t.get('status') == status]
        
        if trade_type:
            result = [t for t in result if t.get('type') == trade_type]
            
        if limit:
            result = result[-limit:]
            
        return result
    
    def update_trade(self, trade_id, updates):
        """Update an existing trade"""
        for i, trade in enumerate(self.trades):
            if trade.get('id') == trade_id:
                self.trades[i].update(updates)
                self.save_trades()
                return True
        return False
    
    def get_trade_by_order_id(self, order_id):
        """Find a trade by its order ID"""
        for trade in self.trades:
            if trade.get('order_id') == order_id:
                return trade
        return None
    
    def get_trade_by_id(self, trade_id):
        """Find a trade by its trade ID"""
        for trade in self.trades:
            if trade.get('id') == trade_id:
                return trade
        return None
    
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
                sell_total = sell_price * sell_volume
                
                # Find buy trades at lower prices
                for buy_price in sorted(buy_trades.keys()):
                    if buy_price < sell_price and buy_trades[buy_price]:
                        buy_trade = buy_trades[buy_price][0]
                        buy_volume = buy_trade.get('volume')
                        buy_total = buy_price * buy_volume
                        
                        # Calculate margin
                        volume = min(buy_volume, sell_volume)
                        buy_cost = volume * buy_price
                        sell_revenue = volume * sell_price
                        margin = sell_revenue - buy_cost
                        margin_percentage = (margin / buy_cost) * 100
                        
                        margin_data = {
                            'buy_trade_id': buy_trade.get('id'),
                            'sell_trade_id': trade.get('id'),
                            'buy_price': buy_price,
                            'sell_price': sell_price,
                            'volume': volume,
                            'margin': margin,
                            'margin_percentage': margin_percentage,
                            'timestamp': time.time()
                        }
                        
                        margins.append(margin_data)
                        
                        # Update the buy trade volume
                        remaining_volume = buy_volume - volume
                        if remaining_volume > 0:
                            buy_trade['volume'] = remaining_volume
                        else:
                            buy_trades[buy_price].pop(0)
                        
                        # Update the sell trade volume
                        sell_volume -= volume
                        if sell_volume <= 0:
                            break
        
        return margins
    
    def get_performance_summary(self):
        """Get a summary of trading performance"""
        margins = self.calculate_margins()
        
        total_margin = sum(m.get('margin', 0) for m in margins)
        total_buy_volume = sum(t.get('volume', 0) for t in self.trades if t.get('type') == 'buy' and t.get('status') == 'filled')
        total_sell_volume = sum(t.get('volume', 0) for t in self.trades if t.get('type') == 'sell' and t.get('status') == 'filled')
        
        avg_margin_percentage = 0
        if margins:
            avg_margin_percentage = sum(m.get('margin_percentage', 0) for m in margins) / len(margins)
        
        return {
            'total_trades': len(self.trades),
            'filled_trades': len([t for t in self.trades if t.get('status') == 'filled']),
            'buy_trades': len([t for t in self.trades if t.get('type') == 'buy']),
            'sell_trades': len([t for t in self.trades if t.get('type') == 'sell']),
            'total_margin': total_margin,
            'avg_margin_percentage': avg_margin_percentage,
            'total_buy_volume': total_buy_volume,
            'total_sell_volume': total_sell_volume,
            'net_volume': total_buy_volume - total_sell_volume
        }

# Initialize trade database
trade_db = TradeDatabase()

def log_message(message, level="info"):
    """Log message to file and print to console"""
    print(message)
    if level == "info":
        logging.info(message)
    elif level == "warning":
        logging.warning(message)
    elif level == "error":
        logging.error(message)

def send_telegram_notification(subject, message):
    """Send notification via Telegram"""
    if not ENABLE_TELEGRAM:
        log_message(f"Telegram notifications disabled. Would have sent: {subject}")
        return
        
    try:
        full_message = f"*XRP Trading Bot: {subject}*\n\n{message}"
        
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": full_message,
            "parse_mode": "Markdown"
        }
        
        response = requests.post(url, data=data) 
        if response.status_code == 200:
            log_message(f"Telegram notification sent: {subject}")
        else:
            log_message(f"Error sending Telegram notification: {response.text}", "error")
    except Exception as e:
        log_message(f"Error sending Telegram notification: {e}", "error")

def get_account_balance():
    """Get account balance from Kraken"""
    try:
        balance = api.get_account_balance()
        return balance
    except Exception as e:
        log_message(f"Error getting account balance: {e}", "error")
        send_telegram_notification("Error", f"Failed to get account balance: {e}")
        return None

def get_asset_price(pair):
    """Get current price for an asset pair"""
    try:
        ticker = api.get_ticker_information(pair)
        current_price = float(ticker['c'][0][0])
        # Round to 4 decimal places
        current_price = round(current_price, 4)
        return current_price
    except Exception as e:
        log_message(f"Error getting price for {pair}: {e}", "error")
        send_telegram_notification("Error", f"Failed to get price for {pair}: {e}")
        return None

def place_order_direct(pair, order_type, price, volume, config):
    """Place an order on Kraken using direct krakenex API"""
    try:
        # Format price to exactly 4 decimal places as a string
        price_str = "{:.4f}".format(float(price))
        volume_str = "{:.8f}".format(float(volume))
        
        log_message(f"Attempting to place {order_type} order for {volume_str} {pair} at {price_str}")
        
        # Generate a unique trade ID
        trade_id = str(uuid.uuid4())
        
        # Create trade record
        trade = {
            'id': trade_id,
            'pair': pair,
            'type': order_type,
            'price': float(price),
            'volume': float(volume),
            'status': 'pending',
            'created_at': time.time(),
            'updated_at': time.time(),
            'order_id': None,
            'filled_volume': 0,
            'cost': 0,
            'fee': 0
        }
        
        # Use krakenex directly instead of pykrakenapi
        params = {
            'pair': pair,
            'type': order_type,
            'ordertype': 'limit',
            'price': price_str,
            'volume': volume_str
        }
        
        result = kraken.query_private('AddOrder', params)
        
        if 'error' in result and result['error']:
            log_message(f"Error placing {order_type} order: {result['error']}", "error")
            send_telegram_notification(
                f"Order Error",
                f"Error placing {order_type} order:\n\n" +
                f"Pair: {pair}\n" +
                f"Price: {price_str}\n" +
                f"Volume: {volume_str}\n\n" +
                f"Error: {result['error']}"
            )
            # Update trade record
            trade['status'] = 'failed'
            trade['error'] = str(result['error'])
            trade_db.add_trade(trade)
            
            # Update trading stats
            trading_stats["failed_trades"] += 1
            return None
        
        # Update trade record with order ID
        if 'result' in result and 'txid' in result['result']:
            order_id = result['result']['txid'][0]
            trade['order_id'] = order_id
            trade['status'] = 'open'
            trade_db.add_trade(trade)
        
        log_message(f"Placed {order_type} order for {volume_str} {pair} at {price_str}: {result}")
        
        # Update trading stats
        trading_stats["total_trades"] += 1
        trading_stats["successful_trades"] += 1
        if order_type == "buy":
            trading_stats["buy_volume"] += float(volume_str)
        else:
            trading_stats["sell_volume"] += float(volume_str)
        
        # Send notification for order placement
        send_telegram_notification(
            f"New {order_type.upper()} Order",
            f"A new {order_type} order has been placed:\n\n" +
            f"Pair: {pair}\n" +
            f"Price: {price_str}\n" +
            f"Volume: {volume_str}\n" +
            f"Trade ID: {trade_id[:8]}"
        )
        
        return result
    except Exception as e:
        log_message(f"Error placing {order_type} order: {e}", "error")
        
        # Create failed trade record
        trade = {
            'id': str(uuid.uuid4()),
            'pair': pair,
            'type': order_type,
            'price': float(price),
            'volume': float(volume),
            'status': 'failed',
            'created_at': time.time(),
            'updated_at': time.time(),
            'error': str(e)
        }
        trade_db.add_trade(trade)
        
        # Update trading stats
        trading_stats["failed_trades"] += 1
        
        # Send notification for order error
        send_telegram_notification(
            f"Order Error",
            f"Error placing {order_type} order:\n\n" +
            f"Pair: {pair}\n" +
            f"Price: {price}\n" +
            f"Volume: {volume}\n\n" +
            f"Error: {e}"
        )
        
        return None

def get_open_orders():
    """Get all open orders"""
    try:
        open_orders = api.get_open_orders()
        
        # Update trade records for open orders
        for txid, order in open_orders.iterrows():
            trade = trade_db.get_trade_by_order_id(txid)
            if trade:
                # Update trade with latest information
                updates = {
                    'updated_at': time.time(),
                    'status': 'open'
                }
                trade_db.update_trade(trade['id'], updates)
        
        return open_orders
    except Exception as e:
        log_message(f"Error getting open orders: {e}", "error")
        send_telegram_notification("Error", f"Failed to get open orders: {e}")
        return None

def check_closed_orders(config):
    """Check for recently closed orders and update trade records"""
    try:
        # Get closed orders from the last 24 hours
        since = time.time() - 86400  # 24 hours ago
        closed_orders = api.get_closed_orders(start=since)
        
        for txid, order in closed_orders.iterrows():
            trade = trade_db.get_trade_by_order_id(txid)
            if trade and trade['status'] != 'filled':
                status = order['status']
                
                if status == 'closed':
                    # Order was filled
                    vol_exec = float(order['vol_exec'])
                    price = float(order['price'])
                    cost = float(order['cost'])
                    fee = float(order['fee'])
                    
                    updates = {
                        'status': 'filled',
                        'filled_volume': vol_exec,
                        'actual_price': price,
                        'cost': cost,
                        'fee': fee,
                        'updated_at': time.time(),
                        'filled_at': order['closetm']
                    }
                    
                    trade_db.update_trade(trade['id'], updates)
                    
                    # Send notification
                    send_telegram_notification(
                        f"Order Filled",
                        f"Your {trade['type']} order has been filled:\n\n" +
                        f"Pair: {trade['pair']}\n" +
                        f"Price: {price}\n" +
                        f"Volume: {vol_exec}\n" +
                        f"Cost: {cost}\n" +
                        f"Fee: {fee}"
                    )
                    
                    # Calculate and log margins
                    if trade['type'] == 'sell':
                        margins = trade_db.calculate_margins()
                        if margins:
                            latest_margin = margins[-1]
                            send_telegram_notification(
                                f"Trade Margin",
                                f"Margin calculated for recent trade:\n\n" +
                                f"Buy Price: {latest_margin['buy_price']}\n" +
                                f"Sell Price: {latest_margin['sell_price']}\n" +
                                f"Volume: {latest_margin['volume']}\n" +
                                f"Margin: {latest_margin['margin']:.4f}\n" +
                                f"Margin %: {latest_margin['margin_percentage']:.2f}%"
                            )
                    
                    # Handle profit reinvestment if enabled
                    if config.get("profit_reinvestment", False) and trade['type'] == 'sell':
                        log_message("Profit reinvestment enabled. Checking for reinvestment opportunities.")
                        # Get current price
                        current_price = get_asset_price(trade['pair'])
                        if current_price:
                            # Calculate profit
                            profit = cost - fee
                            if profit > 0:
                                # Calculate how much of the base currency we can buy with the profit
                                reinvest_volume = profit / current_price
                                if reinvest_volume > 0.1:  # Only reinvest if we can buy at least 0.1 XRP
                                    # Calculate a buy price below current price
                                    buy_price = round(current_price * 0.99, 4)  # 1% below current price
                                    log_message(f"Reinvesting profit of {profit:.4f} to buy {reinvest_volume:.8f} XRP at {buy_price}")
                                    # Place a buy order
                                    place_order_direct(trade['pair'], "buy", buy_price, reinvest_volume, config)
                
                elif status == 'canceled':
                    # Order was canceled
                    updates = {
                        'status': 'canceled',
                        'updated_at': time.time()
                    }
                    trade_db.update_trade(trade['id'], updates)
        
        return closed_orders
    except Exception as e:
        log_message(f"Error checking closed orders: {e}", "error")
        return None

def cancel_order(txid):
    """Cancel an open order"""
    try:
        result = api.cancel_open_order(txid)
        log_message(f"Cancelled order {txid}: {result}")
        
        # Update trade record
        trade = trade_db.get_trade_by_order_id(txid)
        if trade:
            updates = {
                'status': 'canceled',
                'updated_at': time.time()
            }
            trade_db.update_trade(trade['id'], updates)
        
        return result
    except Exception as e:
        log_message(f"Error cancelling order {txid}: {e}", "error")
        send_telegram_notification("Error", f"Failed to cancel order {txid}: {e}")
        return None

def check_quote_currency_balance(pair, config):
    """Check if we have enough of the quote currency (e.g., GBP) for buy orders"""
    try:
        balance = get_account_balance()
        if balance is None:
            return False
            
        # Extract quote currency (e.g., GBP from XRPGBP)
        quote_currency = pair[3:]
        quote_balance = 0
        
        # Kraken may use different asset codes internally
        kraken_quote_map = {
            'GBP': 'ZGBP',
            'USD': 'ZUSD',
            'EUR': 'ZEUR',
            'JPY': 'ZJPY',
            'CAD': 'ZCAD',
            'AUD': 'ZAUD'
        }
        
        kraken_quote = kraken_quote_map.get(quote_currency, quote_currency)
        
        for asset, amount in balance.iterrows():
            if asset == kraken_quote:
                quote_balance = float(amount['vol'])
                break
        
        # Calculate how much quote currency we need for all buy orders
        current_price = get_asset_price(pair)
        if current_price is None:
            return False
            
        grid_range_percentage = config.get("grid_range_percentage", 3.5)
        grid_levels = config.get("grid_levels", 14)
        
        lower_bound = round(current_price * (1 - grid_range_percentage / 100), 4)
        upper_bound = round(current_price * (1 + grid_range_percentage / 100), 4)
        
        # Count how many grid levels are below current price (buy orders)
        buy_levels = 0
        grid_step = round((upper_bound - lower_bound) / (grid_levels - 1), 4)
        
        for i in range(grid_levels):
            price = round(lower_bound + i * grid_step, 4)
            if price < current_price:
                buy_levels += 1
        
        # Calculate required quote currency amount
        allocation_per_grid = config.get("total_allocation", 100.0) / grid_levels
        required_quote = 0
        
        for i in range(buy_levels):
            price = round(lower_bound + i * grid_step, 4)
            required_quote += allocation_per_grid
        
        log_message(f"Quote currency ({quote_currency}) balance: {quote_balance}")
        log_message(f"Required quote currency for buy orders: {required_quote}")
        
        if quote_balance < required_quote:
            log_message(f"Insufficient {quote_currency} balance. Required: {required_quote}, Available: {quote_balance}", "warning")
            return False
        
        return True
    except Exception as e:
        log_message(f"Error checking quote currency balance: {e}", "error")
        return False

def create_nonlinear_grid(current_price, lower_bound, upper_bound, grid_levels, config):
    """Create a non-linear grid with more levels near the current price"""
    grid_prices = []
    
    # Determine if we should use dynamic sizing
    dynamic_sizing = config.get("dynamic_sizing", False)
    
    # Find where current price falls in the range
    range_size = upper_bound - lower_bound
    current_position = (current_price - lower_bound) / range_size
    
    # Adjust the exponent based on dynamic sizing
    exponent = 1.5
    if dynamic_sizing:
        # More aggressive non-linear distribution
        exponent = 2.0
        log_message("Using dynamic sizing with more aggressive non-linear distribution")
    
    for i in range(grid_levels):
        # Non-linear distribution formula
        factor = (i / (grid_levels - 1)) ** exponent
        price = lower_bound + factor * range_size
        price = round(price, 4)
        grid_prices.append(price)
    
    return grid_prices

def calculate_trading_performance(pair, current_price):
    """Calculate and log trading performance metrics"""
    try:
        # Get performance summary from trade database
        performance = trade_db.get_performance_summary()
        
        # Calculate runtime
        runtime_seconds = time.time() - trading_stats["start_time"]
        runtime_days = runtime_seconds / (24 * 3600)
        
        # Calculate trade frequency
        trades_per_day = performance['total_trades'] / max(1, runtime_days)
        
        # Calculate success rate
        success_rate = 0
        if performance['total_trades'] > 0:
            success_rate = (performance['filled_trades'] / performance['total_trades']) * 100
        
        performance_message = (
            f"Trading Performance Summary:\n\n"
            f"Runtime: {runtime_days:.2f} days\n"
            f"Total Trades: {performance['total_trades']}\n"
            f"Filled Trades: {performance['filled_trades']}\n"
            f"Buy Trades: {performance['buy_trades']}\n"
            f"Sell Trades: {performance['sell_trades']}\n"
            f"Success Rate: {success_rate:.2f}%\n"
            f"Trades Per Day: {trades_per_day:.2f}\n"
            f"Total Margin: {performance['total_margin']:.4f}\n"
            f"Average Margin %: {performance['avg_margin_percentage']:.2f}%\n"
            f"Buy Volume: {performance['total_buy_volume']:.8f} XRP\n"
            f"Sell Volume: {performance['total_sell_volume']:.8f} XRP\n"
            f"Net Volume: {performance['net_volume']:.8f} XRP\n"
            f"Current XRP Price: {current_price:.4f}"
        )
        
        log_message(performance_message)
        send_telegram_notification("Performance Report", performance_message)
        
        # Save performance data to file
        try:
            performance_data = {
                "timestamp": time.time(),
                "runtime_days": runtime_days,
                "total_trades": performance['total_trades'],
                "filled_trades": performance['filled_trades'],
                "buy_trades": performance['buy_trades'],
                "sell_trades": performance['sell_trades'],
                "success_rate": success_rate,
                "trades_per_day": trades_per_day,
                "total_margin": performance['total_margin'],
                "avg_margin_percentage": performance['avg_margin_percentage'],
                "buy_volume": performance['total_buy_volume'],
                "sell_volume": performance['total_sell_volume'],
                "net_volume": performance['net_volume'],
                "current_price": current_price
            }
            
            with open('data/performance_history.json', 'a') as f:
                f.write(json.dumps(performance_data) + '\n')
        except Exception as e:
            log_message(f"Error saving performance data: {e}", "error")
        
        return performance_message
    except Exception as e:
        log_message(f"Error calculating trading performance: {e}", "error")
        return None

def check_market_trend(pair, days=7):
    """Check market trend for the pair over specified days"""
    try:
        # Get OHLC data
        ohlc, last = api.get_ohlc_data(pair, interval=1440, since=None)  # 1440 = 1 day in minutes
        
        # Limit to the specified number of days
        ohlc = ohlc.tail(days)
        
        # Calculate simple moving average
        sma = ohlc['close'].mean()
        current_price = ohlc['close'].iloc[-1]
        
        # Calculate price change percentage
        price_change = ((current_price - ohlc['close'].iloc[0]) / ohlc['close'].iloc[0]) * 100
        
        # Determine trend
        trend = "neutral"
        if current_price > sma * 1.03:  # 3% above SMA
            trend = "bullish"
        elif current_price < sma * 0.97:  # 3% below SMA
            trend = "bearish"
        
        log_message(f"Market trend analysis for {pair} over {days} days:")
        log_message(f"Current price: {current_price:.4f}")
        log_message(f"{days}-day SMA: {sma:.4f}")
        log_message(f"Price change: {price_change:.2f}%")
        log_message(f"Trend: {trend}")
        
        return {
            "trend": trend,
            "price_change": price_change,
            "current_price": current_price,
            "sma": sma
        }
    except Exception as e:
        log_message(f"Error checking market trend: {e}", "error")
        return None

def adjust_grid_parameters(config, trend_data):
    """Adjust grid parameters based on market trend"""
    if not trend_data:
        return config
    
    new_config = config.copy()
    
    # Adjust grid range based on trend
    if trend_data["trend"] == "bullish":
        # In bullish trend, slightly increase upper range and decrease lower range
        new_config["grid_range_percentage"] = min(5.0, config["grid_range_percentage"] * 1.2)
        log_message(f"Bullish trend detected. Increasing grid range to {new_config['grid_range_percentage']}%")
    elif trend_data["trend"] == "bearish":
        # In bearish trend, tighten the grid range
        new_config["grid_range_percentage"] = max(2.0, config["grid_range_percentage"] * 0.8)
        log_message(f"Bearish trend detected. Decreasing grid range to {new_config['grid_range_percentage']}%")
    
    # Adjust allocation based on trend
    if abs(trend_data["price_change"]) > 10:  # If price changed more than 10%
        # Adjust allocation to be more conservative
        new_config["total_allocation"] = max(50, config["total_allocation"] * 0.9)
        log_message(f"High volatility detected. Reducing allocation to {new_config['total_allocation']}")
    
    return new_config

def implement_grid_trading(config):
    """Implement grid trading strategy with actual orders"""
    log_message("Starting XRP Income-Focused Grid Trading Strategy")
    send_telegram_notification("Strategy Started", "XRP Income-Focused Grid Trading Strategy has been initiated")
    log_message(f"Configuration: {config}")
    
    # Get trading pair from config
    pair = config.get("trading_pair", "XRPGBP")
    
    # Check market trend
    trend_data = check_market_trend(pair)
    if trend_data:
        # Adjust grid parameters based on trend
        config = adjust_grid_parameters(config, trend_data)
        log_message(f"Adjusted configuration based on market trend: {config}")
    
    # Get current price
    current_price = get_asset_price(pair)
    if current_price is None:
        log_message(f"Could not get current price for {pair}. Exiting.", "error")
        send_telegram_notification("Critical Error", f"Could not get current price for {pair}. Strategy stopped.")
        return
    
    log_message(f"Current {pair} price: {current_price}")
    
    # Calculate grid levels with proper rounding
    grid_range_percentage = config.get("grid_range_percentage", 3.5)
    grid_levels = config.get("grid_levels", 14)
    
    # Ensure all calculations are rounded to 4 decimal places
    lower_bound = round(current_price * (1 - grid_range_percentage / 100), 4)
    upper_bound = round(current_price * (1 + grid_range_percentage / 100), 4)
    
    # Create non-linear grid for more efficient price capture
    grid_prices = create_nonlinear_grid(current_price, lower_bound, upper_bound, grid_levels, config)
    
    log_message(f"Grid range: {lower_bound} to {upper_bound}")
    log_message(f"Grid step: Non-linear distribution")
    log_message(f"Grid prices: {grid_prices}")
    
    # Send notification about grid setup
    send_telegram_notification(
        "Grid Setup",
        f"Grid trading setup for {pair}:\n\n" +
        f"Current price: {current_price}\n" +
        f"Grid range: {lower_bound} to {upper_bound}\n" +
        f"Grid levels: {grid_levels}\n" +
        f"Grid distribution: Non-linear (optimized)"
    )
    
    # Check if we have enough quote currency for buy orders
    have_quote_currency = check_quote_currency_balance(pair, config)
    
    # Get account balance
    balance = get_account_balance()
    if balance is None:
        log_message("Could not get account balance. Exiting.", "error")
        send_telegram_notification("Critical Error", "Could not get account balance. Strategy stopped.")
        return
    
    # Check if we have the base currency (XRP)
    base_currency = pair[:3]
    base_balance = 0
    
    for asset, amount in balance.iterrows():
        if asset == "XXRP":  # Kraken uses XXRP for XRP
            base_balance = float(amount['vol'])
    
    log_message(f"{base_currency} balance: {base_balance}")
    
    if base_balance < config.get("total_allocation", 100.0):
        log_message(f"Insufficient {base_currency} balance. Required: {config.get('total_allocation', 100.0)}, Available: {base_balance}", "warning")
        send_telegram_notification(
            "Warning: Insufficient Balance",
            f"Insufficient {base_currency} balance.\n" +
            f"Required: {config.get('total_allocation', 100.0)}\n" +
            f"Available: {base_balance}"
        )
        return
    
    # Cancel any existing open orders
    open_orders = get_open_orders()
    if open_orders is not None and not open_orders.empty:
        log_message(f"Cancelling {len(open_orders)} existing open orders")
        for txid in open_orders.index:
            cancel_order(txid)
    
    # Calculate order sizes
    allocation_per_grid_base = config.get("total_allocation", 100.0) / grid_levels
    
    # Find index of current price in grid
    current_price_index = 0
    for i, price in enumerate(grid_prices):
        if price > current_price:
            current_price_index = i
            break
    
    # Place grid orders with dynamic sizing if enabled
    dynamic_sizing = config.get("dynamic_sizing", False)
    
    for i, price in enumerate(grid_prices):
        if price < current_price and have_quote_currency:
            # Place buy order with dynamic sizing
            if dynamic_sizing:
                # Larger orders closer to current price
                distance_factor = 1 - 0.05 * (current_price_index - i)  # 5% decrease per level away
                adjusted_allocation = allocation_per_grid_base * max(0.7, distance_factor)
            else:
                adjusted_allocation = allocation_per_grid_base
                
            order_volume = adjusted_allocation / price  # Calculate XRP amount to buy
            place_order_direct(pair, "buy", price, order_volume, config)
        elif price > current_price:
            # Place sell order with dynamic sizing
            if dynamic_sizing:
                # Larger orders further from current price
                distance_factor = 1 + 0.1 * (i - current_price_index)  # 10% increase per level
                adjusted_allocation = allocation_per_grid_base * distance_factor
            else:
                adjusted_allocation = allocation_per_grid_base
                
            place_order_direct(pair, "sell", price, adjusted_allocation, config)
    
    log_message("Initial grid orders placed successfully")
    send_telegram_notification("Grid Active", "Initial grid orders have been placed successfully")
    
    # Monitor and maintain grid
    price_check_interval = config.get("price_check_interval_minutes", 5) * 60  # Convert to seconds
    order_timeout_hours = config.get("order_timeout_hours", 48) * 3600  # Convert to seconds
    
    log_message(f"Monitoring grid every {price_check_interval/60} minutes")
    
    # Variables for daily summary
    last_summary_time = time.time()
    daily_summary_interval = 24 * 3600  # 24 hours in seconds
    
    # Variables for trend check
    last_trend_check_time = time.time()
    trend_check_interval = config.get("trend_check_interval", 6) * 3600  # Convert hours to seconds
    
    # Variables for order check
    last_order_check_time = time.time()
    order_check_interval = 15 * 60  # 15 minutes in seconds
    
    # Variables for stop-loss
    initial_price = current_price
    stop_loss_percentage = config.get("stop_loss_percentage", 15)  # Default 15% drop triggers stop-loss
    
    while True:
        try:
            time.sleep(price_check_interval)
            
            # Get current price
            current_price = get_asset_price(pair)
            if current_price is None:
                continue
            
            log_message(f"Current {pair} price: {current_price}")
            
            # Check stop-loss
            if current_price < initial_price * (1 - stop_loss_percentage/100):
                log_message(f"Stop-loss triggered. Price dropped more than {stop_loss_percentage}% from initial price.", "warning")
                send_telegram_notification(
                    "Stop-Loss Triggered",
                    f"Price dropped from {initial_price} to {current_price} ({((current_price/initial_price)-1)*100:.2f}%).\n" +
                    "Cancelling all orders and waiting for market to stabilize."
                )
                
                # Cancel all orders
                open_orders = get_open_orders()
                if open_orders is not None and not open_orders.empty:
                    for txid in open_orders.index:
                        cancel_order(txid)
                
                # Wait for market to stabilize
                log_message("Waiting 1 hour for market to stabilize before restarting grid")
                time.sleep(3600)  # 1 hour
                
                # Restart with new parameters
                implement_grid_trading(config)
                return
            
            # Check for closed orders periodically
            current_time = time.time()
            if current_time - last_order_check_time > order_check_interval:
                log_message("Checking for closed orders...")
                check_closed_orders(config)
                last_order_check_time = current_time
            
            # Get open orders
            open_orders = get_open_orders()
            if open_orders is None:
                continue
            
            # Check for filled orders and create new orders
            if open_orders.empty:
                log_message("All orders have been filled. Creating new grid.")
                implement_grid_trading(config)  # Restart grid
                return
            
            # Check for orders that have been open too long
            orders_to_cancel = []
            
            for txid, order in open_orders.iterrows():
                order_age = current_time - order['opentm']
                if order_age > order_timeout_hours:
                    log_message(f"Order {txid} has been open for {order_age/3600:.2f} hours. Cancelling.")
                    orders_to_cancel.append(txid)
            
            # Cancel old orders
            for txid in orders_to_cancel:
                cancel_order(txid)
            
            # If we cancelled any orders, recreate the grid
            if orders_to_cancel:
                log_message("Recreating grid after cancelling old orders")
                implement_grid_trading(config)
                return
            
            # Check if it's time for a trend analysis
            if current_time - last_trend_check_time > trend_check_interval:
                log_message(f"Performing market trend analysis (interval: {trend_check_interval/3600} hours)")
                trend_data = check_market_trend(pair)
                if trend_data:
                    # If trend has changed significantly, consider recreating the grid
                    if trend_data["trend"] != "neutral" and abs(trend_data["price_change"]) > 7:
                        log_message(f"Significant market trend change detected: {trend_data['trend']} with {trend_data['price_change']:.2f}% change")
                        log_message("Recreating grid with adjusted parameters")
                        
                        # Adjust config based on trend
                        new_config = adjust_grid_parameters(config, trend_data)
                        
                        # Only recreate if parameters actually changed
                        if new_config != config:
                            log_message(f"Parameters adjusted. Old: {config}, New: {new_config}")
                            implement_grid_trading(new_config)
                            return
                
                last_trend_check_time = current_time
            
            # Check for profit reinvestment opportunities
            if have_quote_currency == False and config.get("profit_reinvestment", False):
                # Check if we now have enough quote currency for buy orders
                have_quote_currency = check_quote_currency_balance(pair, config)
                if have_quote_currency:
                    log_message("Quote currency balance increased. Recreating grid to place buy orders.")
                    implement_grid_trading(config)
                    return
            
            # Send daily summary and performance report
            if current_time - last_summary_time > daily_summary_interval:
                # Calculate and log trading performance
                calculate_trading_performance(pair, current_price)
                
                # Get account balance for summary
                balance = get_account_balance()
                if balance is not None:
                    base_balance = 0
                    quote_balance = 0
                    
                    # Extract quote currency (e.g., GBP from XRPGBP)
                    quote_currency = pair[3:]
                    
                    # Kraken may use different asset codes internally
                    kraken_quote_map = {
                        'GBP': 'ZGBP',
                        'USD': 'ZUSD',
                        'EUR': 'ZEUR',
                        'JPY': 'ZJPY',
                        'CAD': 'ZCAD',
                        'AUD': 'ZAUD'
                    }
                    
                    kraken_quote = kraken_quote_map.get(quote_currency, quote_currency)
                    
                    for asset, amount in balance.iterrows():
                        if asset == "XXRP":
                            base_balance = float(amount['vol'])
                        if asset == kraken_quote:
                            quote_balance = float(amount['vol'])
                    
                    # Get margin statistics
                    performance = trade_db.get_performance_summary()
                    
                    send_telegram_notification(
                        "Daily Summary",
                        f"XRP Grid Trading Daily Summary:\n\n" +
                        f"Current {pair} price: {current_price}\n" +
                        f"Current {base_currency} balance: {base_balance}\n" +
                        f"Current {quote_currency} balance: {quote_balance}\n" +
                        f"Active orders: {len(open_orders)}\n" +
                        f"Total trades: {performance['total_trades']}\n" +
                        f"Filled trades: {performance['filled_trades']}\n" +
                        f"Total margin: {performance['total_margin']:.4f}\n" +
                        f"Average margin %: {performance['avg_margin_percentage']:.2f}%"
                    )
                
                last_summary_time = current_time
        
        except Exception as e:
            log_message(f"Error in grid monitoring loop: {e}", "error")
            send_telegram_notification("Error", f"Error in grid monitoring: {e}")
            time.sleep(60)  # Wait a minute before retrying

def load_config_from_file():
    """Load configuration from config file if it exists"""
    config_path = 'data/config.json'
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            log_message(f"Loaded configuration from {config_path}")
            return config
        except Exception as e:
            log_message(f"Error loading configuration from file: {e}", "error")
    return None

def save_config_to_file(config):
    """Save configuration to file for persistence"""
    config_path = 'data/config.json'
    try:
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        log_message(f"Saved configuration to {config_path}")
    except Exception as e:
        log_message(f"Error saving configuration to file: {e}", "error")

def generate_trade_report(days=7):
    """Generate a detailed trade report for a specified period"""
    try:
        # Get all trades
        all_trades = trade_db.trades
        
        # Filter trades from the specified period
        cutoff_time = time.time() - (days * 24 * 3600)
        recent_trades = [t for t in all_trades if t.get('created_at', 0) > cutoff_time]
        
        # Get filled trades
        filled_trades = [t for t in recent_trades if t.get('status') == 'filled']
        
        # Calculate statistics
        buy_trades = [t for t in filled_trades if t.get('type') == 'buy']
        sell_trades = [t for t in filled_trades if t.get('type') == 'sell']
        
        buy_volume = sum(t.get('filled_volume', 0) for t in buy_trades)
        sell_volume = sum(t.get('filled_volume', 0) for t in sell_trades)
        
        buy_cost = sum(t.get('cost', 0) for t in buy_trades)
        sell_revenue = sum(t.get('cost', 0) for t in sell_trades)
        
        total_fees = sum(t.get('fee', 0) for t in filled_trades)
        
        # Calculate margins
        margins = trade_db.calculate_margins()
        recent_margins = [m for m in margins if m.get('timestamp', 0) > cutoff_time]
        
        total_margin = sum(m.get('margin', 0) for m in recent_margins)
        avg_margin_pct = 0
        if recent_margins:
            avg_margin_pct = sum(m.get('margin_percentage', 0) for m in recent_margins) / len(recent_margins)
        
        # Generate report
        report = f"Trade Report for the Last {days} Days\n\n"
        report += f"Total Trades: {len(recent_trades)}\n"
        report += f"Filled Trades: {len(filled_trades)}\n"
        report += f"Buy Trades: {len(buy_trades)}\n"
        report += f"Sell Trades: {len(sell_trades)}\n\n"
        
        report += f"Buy Volume: {buy_volume:.8f} XRP\n"
        report += f"Sell Volume: {sell_volume:.8f} XRP\n"
        report += f"Net Volume Change: {buy_volume - sell_volume:.8f} XRP\n\n"
        
        report += f"Buy Cost: {buy_cost:.4f}\n"
        report += f"Sell Revenue: {sell_revenue:.4f}\n"
        report += f"Total Fees: {total_fees:.4f}\n\n"
        
        report += f"Total Margin: {total_margin:.4f}\n"
        report += f"Average Margin %: {avg_margin_pct:.2f}%\n\n"
        
        report += "Recent Trades:\n"
        for trade in sorted(filled_trades, key=lambda x: x.get('filled_at', 0), reverse=True)[:10]:
            report += f"- {trade.get('type').upper()} {trade.get('filled_volume', 0):.8f} XRP at {trade.get('actual_price', 0):.4f} ({trade.get('status')})\n"
        
        report += "\nRecent Margins:\n"
        for margin in sorted(recent_margins, key=lambda x: x.get('timestamp', 0), reverse=True)[:10]:
            report += f"- Buy: {margin.get('buy_price'):.4f}, Sell: {margin.get('sell_price'):.4f}, Volume: {margin.get('volume'):.8f}, Margin: {margin.get('margin'):.4f} ({margin.get('margin_percentage'):.2f}%)\n"
        
        # Save report to file
        report_path = f"data/trade_report_{time.strftime('%Y%m%d')}.txt"
        with open(report_path, 'w') as f:
            f.write(report)
        
        log_message(f"Trade report generated and saved to {report_path}")
        send_telegram_notification("Trade Report", report)
        
        return report
    except Exception as e:
        log_message(f"Error generating trade report: {e}", "error")
        return None

def main():
    parser = argparse.ArgumentParser(description='XRP Income-Focused Grid Trading Bot')
    parser.add_argument('--trading_pair', type=str, default='XRPGBP', help='Trading pair (default: XRPGBP)')
    parser.add_argument('--grid_range_percentage', type=float, default=3.5, help='Grid range as percentage (default: 3.5)')
    parser.add_argument('--grid_levels', type=int, default=14, help='Number of grid levels (default: 14)')
    parser.add_argument('--total_allocation', type=float, default=100.0, help='Total XRP allocation (default: 100.0)')
    parser.add_argument('--price_check_interval_minutes', type=int, default=5, help='Price check interval in minutes (default: 5)')
    parser.add_argument('--order_timeout_hours', type=int, default=48, help='Order timeout in hours (default: 48)')
    parser.add_argument('--trend_check_interval', type=int, default=6, help='Trend check interval in hours (default: 6)')
    parser.add_argument('--dynamic_sizing', action='store_true', help='Enable dynamic order sizing')
    parser.add_argument('--stop_loss_percentage', type=float, default=15.0, help='Stop-loss percentage (default: 15.0)')
    parser.add_argument('--profit_reinvestment', action='store_true', help='Enable profit reinvestment')
    parser.add_argument('--enable_telegram', action='store_true', help='Enable Telegram notifications')
    parser.add_argument('--config_file', action='store_true', help='Load configuration from file')
    parser.add_argument('--generate_report', action='store_true', help='Generate trade report and exit')
    parser.add_argument('--report_days', type=int, default=7, help='Number of days to include in report (default: 7)')
    
    args = parser.parse_args()
    
    # Set global Telegram flag
    global ENABLE_TELEGRAM
    ENABLE_TELEGRAM = args.enable_telegram
    
    # Generate report if requested
    if args.generate_report:
        generate_trade_report(args.report_days)
        return
    
    # Try to load config from file if requested
    config = None
    if args.config_file:
        config = load_config_from_file()
    
    # If no config from file or not requested, use command line arguments
    if config is None:
        config = {
            "trading_pair": args.trading_pair,
            "grid_range_percentage": args.grid_range_percentage,
            "grid_levels": args.grid_levels,
            "total_allocation": args.total_allocation,
            "price_check_interval_minutes": args.price_check_interval_minutes,
            "order_timeout_hours": args.order_timeout_hours,
            "trend_check_interval": args.trend_check_interval,
            "dynamic_sizing": args.dynamic_sizing,
            "stop_loss_percentage": args.stop_loss_percentage,
            "profit_reinvestment": args.profit_reinvestment
        }
        
        # Save config for future use
        save_config_to_file(config)
    
    log_message("Starting XRP Income-Focused Grid Trading Bot with config:")
    log_message(json.dumps(config, indent=2))
    
    # Implement grid trading
    implement_grid_trading(config)

if __name__ == "__main__":
    main()
