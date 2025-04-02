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

# Create necessary directories
os.makedirs('/app/data', exist_ok=True)

# Set up logging
logging.basicConfig(
    filename='/app/data/trading_log.txt',
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
ENABLE_TELEGRAM = True  # Set to True to enable Telegram notifications

# Trading performance tracking
trading_stats = {
    "total_trades": 0,
    "successful_trades": 0,
    "failed_trades": 0,
    "buy_volume": 0,
    "sell_volume": 0,
    "estimated_profit": 0,
    "start_time": time.time(),
    "last_report_time": time.time()
}

# Initialize Kraken API
kraken = krakenex.API(API_KEY, API_SECRET)
api = KrakenAPI(kraken)

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

def place_order_direct(pair, order_type, price, volume):
    """Place an order on Kraken using direct krakenex API"""
    try:
        # Format price to exactly 4 decimal places as a string
        price_str = "{:.4f}".format(float(price))
        volume_str = "{:.8f}".format(float(volume))
        
        log_message(f"Attempting to place {order_type} order for {volume_str} {pair} at {price_str}")
        
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
            # Update trading stats
            trading_stats["failed_trades"] += 1
            return None
        
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
            f"Volume: {volume_str}"
        )
        
        return result
    except Exception as e:
        log_message(f"Error placing {order_type} order: {e}", "error")
        
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
        return open_orders
    except Exception as e:
        log_message(f"Error getting open orders: {e}", "error")
        send_telegram_notification("Error", f"Failed to get open orders: {e}")
        return None

def cancel_order(txid):
    """Cancel an open order"""
    try:
        result = api.cancel_open_order(txid)
        log_message(f"Cancelled order {txid}: {result}")
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

def create_nonlinear_grid(current_price, lower_bound, upper_bound, grid_levels):
    """Create a non-linear grid with more levels near the current price"""
    grid_prices = []
    
    # Find where current price falls in the range
    range_size = upper_bound - lower_bound
    current_position = (current_price - lower_bound) / range_size
    
    for i in range(grid_levels):
        # Non-linear distribution formula
        factor = (i / (grid_levels - 1)) ** 1.5  # Adjust exponent for density
        price = lower_bound + factor * range_size
        price = round(price, 4)
        grid_prices.append(price)
    
    return grid_prices

def calculate_trading_performance(pair, current_price):
    """Calculate and log trading performance metrics"""
    try:
        # Calculate runtime
        runtime_seconds = time.time() - trading_stats["start_time"]
        runtime_days = runtime_seconds / (24 * 3600)
        
        # Calculate estimated profit (very simplified)
        # This is just a rough estimate based on buy/sell volume and current price
        # For accurate P&L, you would need to track each trade individually
        estimated_profit = (trading_stats["sell_volume"] - trading_stats["buy_volume"]) * current_price
        trading_stats["estimated_profit"] = estimated_profit
        
        # Calculate trade frequency
        trades_per_day = trading_stats["total_trades"] / max(1, runtime_days)
        
        # Calculate success rate
        success_rate = 0
        if trading_stats["total_trades"] > 0:
            success_rate = (trading_stats["successful_trades"] / trading_stats["total_trades"]) * 100
        
        performance_message = (
            f"Trading Performance Summary:\n\n"
            f"Runtime: {runtime_days:.2f} days\n"
            f"Total Trades: {trading_stats['total_trades']}\n"
            f"Successful Trades: {trading_stats['successful_trades']}\n"
            f"Failed Trades: {trading_stats['failed_trades']}\n"
            f"Success Rate: {success_rate:.2f}%\n"
            f"Trades Per Day: {trades_per_day:.2f}\n"
            f"Buy Volume: {trading_stats['buy_volume']:.8f} XRP\n"
            f"Sell Volume: {trading_stats['sell_volume']:.8f} XRP\n"
            f"Current XRP Price: {current_price:.4f}\n"
            f"Estimated Profit: {estimated_profit:.4f} (simplified calculation)"
        )
        
        log_message(performance_message)
        send_telegram_notification("Performance Report", performance_message)
        
        # Save performance data to file
        try:
            performance_data = {
                "timestamp": time.time(),
                "runtime_days": runtime_days,
                "total_trades": trading_stats["total_trades"],
                "successful_trades": trading_stats["successful_trades"],
                "failed_trades": trading_stats["failed_trades"],
                "success_rate": success_rate,
                "trades_per_day": trades_per_day,
                "buy_volume": trading_stats["buy_volume"],
                "sell_volume": trading_stats["sell_volume"],
                "current_price": current_price,
                "estimated_profit": estimated_profit
            }
            
            with open('/app/data/performance_history.json', 'a') as f:
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
    grid_prices = create_nonlinear_grid(current_price, lower_bound, upper_bound, grid_levels)
    
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
    
    # Place grid orders with dynamic sizing
    for i, price in enumerate(grid_prices):
        if price < current_price and have_quote_currency:
            # Place buy order with dynamic sizing
            # Larger orders closer to current price
            distance_factor = 1 - 0.05 * (current_price_index - i)  # 5% decrease per level away
            adjusted_allocation = allocation_per_grid_base * max(0.7, distance_factor)
            order_volume = adjusted_allocation / price  # Calculate XRP amount to buy
            place_order_direct(pair, "buy", price, order_volume)
        elif price > current_price:
            # Place sell order with dynamic sizing
            # Larger orders further from current price
            distance_factor = 1 + 0.1 * (i - current_price_index)  # 10% increase per level
            adjusted_allocation = allocation_per_grid_base * distance_factor
            place_order_direct(pair, "sell", price, adjusted_allocation)
    
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
    trend_check_interval = 6 * 3600  # 6 hours in seconds
    
    # Variables for stop-loss
    initial_price = current_price
    stop_loss_percentage = 15  # 15% drop triggers stop-loss
    
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
            current_time = time.time()
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
                log_message("Performing market trend analysis")
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
            if have_quote_currency == False:
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
                    
                    send_telegram_notification(
                        "Daily Summary",
                        f"XRP Grid Trading Daily Summary:\n\n" +
                        f"Current {pair} price: {current_price}\n" +
                        f"Current {base_currency} balance: {base_balance}\n" +
                        f"Current {quote_currency} balance: {quote_balance}\n" +
                        f"Active orders: {len(open_orders)}\n" +
                        f"Estimated profit: {trading_stats['estimated_profit']:.4f}"
                    )
                
                last_summary_time = current_time
        
        except Exception as e:
            log_message(f"Error in grid monitoring loop: {e}", "error")
            send_telegram_notification("Error", f"Error in grid monitoring: {e}")
            time.sleep(60)  # Wait a minute before retrying

def load_config_from_file():
    """Load configuration from config file if it exists"""
    config_path = '/app/data/config.json'
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
    config_path = '/app/data/config.json'
    try:
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        log_message(f"Saved configuration to {config_path}")
    except Exception as e:
        log_message(f"Error saving configuration to file: {e}", "error")

def main():
    parser = argparse.ArgumentParser(description='XRP Income-Focused Grid Trading Bot')
    parser.add_argument('--trading_pair', type=str, default='XRPGBP', help='Trading pair (default: XRPGBP)')
    parser.add_argument('--grid_range_percentage', type=float, default=3.5, help='Grid range as percentage (default: 3.5)')
    parser.add_argument('--grid_levels', type=int, default=14, help='Number of grid levels (default: 14)')
    parser.add_argument('--total_allocation', type=float, default=100.0, help='Total XRP allocation (default: 100.0)')
    parser.add_argument('--price_check_interval_minutes', type=int, default=5, help='Price check interval in minutes (default: 5)')
    parser.add_argument('--order_timeout_hours', type=int, default=48, help='Order timeout in hours (default: 48)')
    parser.add_argument('--enable_telegram', action='store_true', help='Enable Telegram notifications')
    parser.add_argument('--config_file', action='store_true', help='Load configuration from file')
    
    args = parser.parse_args()
    
    # Set global Telegram flag
    global ENABLE_TELEGRAM
    ENABLE_TELEGRAM = args.enable_telegram
    
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
            "order_timeout_hours": args.order_timeout_hours
        }
        
        # Save config for future use
        save_config_to_file(config)
    
    log_message("Starting XRP Income-Focused Grid Trading Bot with config:")
    log_message(json.dumps(config, indent=2))
    
    # Implement grid trading
    implement_grid_trading(config)

if __name__ == "__main__":
    main()
