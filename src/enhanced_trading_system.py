#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Enhanced Trading System for XRP Trading Bot
Version: 2.0.0
Description: Main script that integrates all advanced modules into a cohesive
trading system with proper error handling, configuration management, and reporting.
"""

import os
import sys
import json
import time
import logging
import argparse
import traceback
from datetime import datetime, timedelta
import krakenex
from pykrakenapi import KrakenAPI

# Import advanced modules
try:
    from signal_collapse_module import SignalCollapseDetector
    from capital_migration_module import CapitalMigrationManager
    from strategic_bifurcation_module import StrategicBifurcationManager
    from technological_convergence_module import TechnologicalConvergenceEngine
    from survivability_module import SurvivabilityManager
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure all module files are in the same directory as this script.")
    sys.exit(1)

class EnhancedTradingSystem:
    """
    Enhanced Trading System that integrates all advanced modules
    into a cohesive trading system.
    """
    
    def __init__(self, config_path=None):
        """
        Initialize the Enhanced Trading System.
        
        Args:
            config_path (str): Path to configuration file
        """
        # Default configuration
        self.default_config = {
            "trading_pair": "XRPGBP",
            "grid_range_percentage": 4.0,
            "grid_levels": 16,
            "total_allocation": 100.0,
            "price_check_interval_minutes": 5,
            "order_timeout_hours": 24,
            "trend_check_interval": 6,
            "dynamic_sizing": True,
            "stop_loss_percentage": 12.0,
            "profit_reinvestment": True,
            "api_key": "",
            "api_secret": "",
            "data_dir": "data",
            "log_file": "data/trading_log.txt",
            "modules": {
                "signal_collapse": {
                    "enabled": True,
                    "config_file": "data/signal_collapse_config.json"
                },
                "capital_migration": {
                    "enabled": True,
                    "config_file": "data/capital_migration_config.json"
                },
                "strategic_bifurcation": {
                    "enabled": True,
                    "config_file": "data/strategic_bifurcation_config.json"
                },
                "technological_convergence": {
                    "enabled": True,
                    "config_file": "data/technological_convergence_config.json"
                },
                "survivability": {
                    "enabled": True,
                    "config_file": "data/survivability_config.json"
                }
            }
        }
        
        # Load configuration
        self.config = self.default_config.copy()
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                    self._merge_config(user_config)
            except Exception as e:
                print(f"Error loading configuration: {e}")
                print("Using default configuration")
        
        # Create data directory if it doesn't exist
        self.data_dir = self.config["data_dir"]
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        
        # Setup logging
        log_file = self.config["log_file"]
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Initialize Kraken API
        self.kraken = None
        self._initialize_api()
        
        # Initialize advanced modules
        self.modules = {}
        self._initialize_modules()
        
        # Initialize trading state
        self.current_price = None
        self.portfolio_value = None
        self.active_orders = {}
        self.completed_orders = []
        self.grid_prices = []
        self.emergency_mode = False
        
        self._log_info("Enhanced Trading System initialized")
    
    def _merge_config(self, user_config):
        """
        Merge user configuration with default configuration
        
        Args:
            user_config (dict): User configuration
        """
        for key, value in user_config.items():
            if key == "modules" and isinstance(value, dict):
                # Merge modules configuration
                for module_name, module_config in value.items():
                    if module_name in self.config["modules"]:
                        self.config["modules"][module_name].update(module_config)
                    else:
                        self.config["modules"][module_name] = module_config
            else:
                # Update other configuration values
                self.config[key] = value
    
    def _initialize_api(self):
        """Initialize Kraken API"""
        try:
            api_key = self.config["api_key"]
            api_secret = self.config["api_secret"]
            
            if api_key and api_secret:
                api = krakenex.API(key=api_key, secret=api_secret)
                self.kraken = KrakenAPI(api)
                self._log_info("Kraken API initialized")
            else:
                self._log_warning("API key or secret not provided, running in read-only mode")
        except Exception as e:
            self._log_error(f"Error initializing Kraken API: {e}")
    
    def _initialize_modules(self):
        """Initialize advanced modules"""
        try:
            # Initialize Signal Collapse Detector
            if self.config["modules"]["signal_collapse"]["enabled"]:
                config_file = self.config["modules"]["signal_collapse"]["config_file"]
                self.modules["signal_collapse"] = SignalCollapseDetector(
                    config_path=config_file,
                    api_key=self.config["api_key"],
                    api_secret=self.config["api_secret"]
                )
                self._log_info("Signal Collapse Detector initialized")
            
            # Initialize Capital Migration Manager
            if self.config["modules"]["capital_migration"]["enabled"]:
                config_file = self.config["modules"]["capital_migration"]["config_file"]
                self.modules["capital_migration"] = CapitalMigrationManager(
                    config_path=config_file,
                    api_key=self.config["api_key"],
                    api_secret=self.config["api_secret"]
                )
                self._log_info("Capital Migration Manager initialized")
            
            # Initialize Strategic Bifurcation Manager
            if self.config["modules"]["strategic_bifurcation"]["enabled"]:
                config_file = self.config["modules"]["strategic_bifurcation"]["config_file"]
                self.modules["strategic_bifurcation"] = StrategicBifurcationManager(
                    config_path=config_file,
                    api_key=self.config["api_key"],
                    api_secret=self.config["api_secret"]
                )
                self._log_info("Strategic Bifurcation Manager initialized")
            
            # Initialize Technological Convergence Engine
            if self.config["modules"]["technological_convergence"]["enabled"]:
                config_file = self.config["modules"]["technological_convergence"]["config_file"]
                self.modules["technological_convergence"] = TechnologicalConvergenceEngine(
                    config_path=config_file,
                    api_key=self.config["api_key"],
                    api_secret=self.config["api_secret"]
                )
                self._log_info("Technological Convergence Engine initialized")
            
            # Initialize Survivability Manager
            if self.config["modules"]["survivability"]["enabled"]:
                config_file = self.config["modules"]["survivability"]["config_file"]
                self.modules["survivability"] = SurvivabilityManager(
                    config_path=config_file,
                    api_key=self.config["api_key"],
                    api_secret=self.config["api_secret"]
                )
                self._log_info("Survivability Manager initialized")
        except Exception as e:
            self._log_error(f"Error initializing modules: {e}")
    
    def _log_info(self, message):
        """Log informational message"""
        logging.info(message)
        print(f"INFO: {message}")
        
    def _log_error(self, message):
        """Log error message"""
        logging.error(message)
        print(f"ERROR: {message}")
        
    def _log_warning(self, message):
        """Log warning message"""
        logging.warning(message)
        print(f"WARNING: {message}")
    
    def get_current_price(self):
        """
        Get current price from Kraken API
        
        Returns:
            float: Current price
        """
        if not self.kraken:
            self._log_error("Kraken API not initialized")
            return None
            
        try:
            # Check if in emergency mode and survivability module is enabled
            if self.emergency_mode and "survivability" in self.modules:
                # Try to get fallback price
                fallback_price = self.modules["survivability"].get_fallback_price()
                if fallback_price:
                    self._log_info(f"Using fallback price: {fallback_price}")
                    return fallback_price
            
            # Get ticker information
            pair = self.config["trading_pair"]
            ticker = self.kraken.get_ticker_information(pair)
            
            # Get current price (last trade price)
            self.current_price = float(ticker['c'][0][0])
            self._log_info(f"Current {pair} price: {self.current_price}")
            return self.current_price
            
        except Exception as e:
            self._log_error(f"Error getting current price: {e}")
            return None
    
    def get_account_balance(self):
        """
        Get account balance from Kraken API
        
        Returns:
            dict: Account balance
        """
        if not self.kraken:
            self._log_error("Kraken API not initialized")
            return None
            
        try:
            # Get account balance
            balance = self.kraken.get_account_balance()
            
            # Get open orders
            open_orders = self.kraken.get_open_orders()
            
            # Calculate portfolio value
            portfolio = {}
            total_value = 0.0
            
            # Process balance
            for asset, amount in balance.items():
                if amount > 0:
                    portfolio[asset] = {
                        "amount": float(amount),
                        "value": 0.0
                    }
                    
                    # Get asset price if not base currency
                    if asset != "ZGBP" and asset != "ZEUR" and asset != "ZUSD":
                        try:
                            # Try to get price for asset/GBP pair
                            ticker = self.kraken.get_ticker_information(f"{asset}GBP")
                            price = float(ticker['c'][0][0])
                            value = amount * price
                            portfolio[asset]["price"] = price
                            portfolio[asset]["value"] = value
                            total_value += value
                        except Exception:
                            # If asset/GBP pair not available, skip valuation
                            portfolio[asset]["price"] = None
                            portfolio[asset]["value"] = 0.0
                    else:
                        # Base currency
                        portfolio[asset]["price"] = 1.0
                        portfolio[asset]["value"] = amount
                        total_value += amount
            
            # Update portfolio value
            self.portfolio_value = total_value
            
            return {
                "portfolio": portfolio,
                "total_value": total_value,
                "open_orders": len(open_orders)
            }
            
        except Exception as e:
            self._log_error(f"Error getting account balance: {e}")
            return None
    
    def calculate_grid_prices(self):
        """
        Calculate grid prices based on current price and configuration
        
        Returns:
            list: Grid prices
        """
        if not self.current_price:
            self._log_error("Current price not available")
            return []
            
        try:
            # Get configuration
            grid_range = self.config["grid_range_percentage"] / 100
            grid_levels = self.config["grid_levels"]
            
            # Check if strategic bifurcation module is enabled and has a recommendation
            if "strategic_bifurcation" in self.modules:
                try:
                    # Run analysis
                    results = self.modules["strategic_bifurcation"].run_analysis()
                    
                    # Check if analysis was successful and returned strategy parameters
                    if "strategy_parameters" in results:
                        params = results["strategy_parameters"]
                        
                        # Update grid parameters if available
                        if "grid_range_percentage" in params:
                            grid_range = params["grid_range_percentage"] / 100
                            self._log_info(f"Using bifurcation recommended grid range: {params['grid_range_percentage']}%")
                            
                        if "grid_levels" in params:
                            grid_levels = params["grid_levels"]
                            self._log_info(f"Using bifurcation recommended grid levels: {grid_levels}")
                            
                        if "grid_distribution" in params:
                            grid_distribution = params["grid_distribution"]
                            self._log_info(f"Using bifurcation recommended grid distribution: {grid_distribution}")
                except Exception as e:
                    self._log_error(f"Error getting strategic bifurcation recommendation: {e}")
            
            # Calculate price range
            price_min = self.current_price * (1 - grid_range)
            price_max = self.current_price * (1 + grid_range)
            
            # Calculate grid prices
            grid_prices = []
            
            # Use non-linear distribution for better results
            for i in range(grid_levels):
                # Quadratic distribution (more levels near current price)
                factor = (i / (grid_levels - 1)) ** 2
                price = price_min + (price_max - price_min) * factor
                
                # Round price to appropriate precision
                price = round(price, 5)  # 5 decimal places for XRP pairs
                
                grid_prices.append(price)
            
            self.grid_prices = grid_prices
            self._log_info(f"Calculated {len(grid_prices)} grid prices from {grid_prices[0]} to {grid_prices[-1]}")
            return grid_prices
            
        except Exception as e:
            self._log_error(f"Error calculating grid prices: {e}")
            return []
    
    def place_order(self, order_type, price, volume):
        """
        Place order on Kraken
        
        Args:
            order_type (str): Order type (buy or sell)
            price (float): Order price
            volume (float): Order volume
            
        Returns:
            str: Order ID or None if failed
        """
        if not self.kraken:
            self._log_error("Kraken API not initialized")
            return None
            
        try:
            # Check if in emergency mode
            if self.emergency_mode:
                self._log_warning("In emergency mode, skipping order placement")
                return None
            
            # Get trading pair
            pair = self.config["trading_pair"]
            
            # Round price and volume to appropriate precision
            price = round(price, 5)  # 5 decimal places for XRP pairs
            volume = round(volume, 1)  # 1 decimal place for XRP volume
            
            # Place order
            result = self.kraken.add_standard_order(
                pair=pair,
                type=order_type,
                ordertype="limit",
                price=price,
                volume=volume
            )
            
            # Extract order ID
            order_id = result["txid"][0]
            
            # Store order information
            self.active_orders[order_id] = {
                "type": order_type,
                "price": price,
                "volume": volume,
                "status": "open",
                "timestamp": datetime.now().isoformat()
            }
            
            self._log_info(f"Placed {order_type} order: {volume} {pair} at {price}, order ID: {order_id}")
            return order_id
            
        except Exception as e:
            self._log_error(f"Error placing order: {e}")
            return None
    
    def check_orders(self):
        """
        Check status of active orders
        
        Returns:
            dict: Order status
        """
        if not self.kraken:
            self._log_error("Kraken API not initialized")
            return None
            
        try:
            # Get open orders
            open_orders = self.kraken.get_open_orders()
            
            # Check each active order
            for order_id in list(self.active_orders.keys()):
                # Check if order is still open
                if order_id in open_orders.index:
                    # Order is still open, check if it has timed out
                    order_time = datetime.fromisoformat(self.active_orders[order_id]["timestamp"])
                    time_diff = (datetime.now() - order_time).total_seconds() / 3600
                    
                    if time_diff > self.config["order_timeout_hours"]:
                        # Order has timed out, cancel it
                        self._log_warning(f"Order {order_id} has timed out, cancelling")
                        self.cancel_order(order_id)
                else:
                    # Order is no longer open, mark as completed
                    self.active_orders[order_id]["status"] = "completed"
                    self.completed_orders.append(self.active_orders[order_id])
                    del self.active_orders[order_id]
                    self._log_info(f"Order {order_id} has been completed")
            
            return {
                "active_orders": len(self.active_orders),
                "completed_orders": len(self.completed_orders)
            }
            
        except Exception as e:
            self._log_error(f"Error checking orders: {e}")
            return None
    
    def cancel_order(self, order_id):
        """
        Cancel order on Kraken
        
        Args:
            order_id (str): Order ID
            
        Returns:
            bool: Success status
        """
        if not self.kraken:
            self._log_error("Kraken API not initialized")
            return False
            
        try:
            # Cancel order
            result = self.kraken.cancel_open_order(txid=order_id)
            
            # Check if order was cancelled
            if result["count"] > 0:
                # Update order status
                if order_id in self.active_orders:
                    self.active_orders[order_id]["status"] = "cancelled"
                    self.completed_orders.append(self.active_orders[order_id])
                    del self.active_orders[order_id]
                
                self._log_info(f"Order {order_id} cancelled successfully")
                return True
            else:
                self._log_warning(f"Failed to cancel order {order_id}")
                return False
            
        except Exception as e:
            self._log_error(f"Error cancelling order: {e}")
            return False
    
    def run_advanced_analysis(self):
        """
        Run analysis with all enabled advanced modules
        
        Returns:
            dict: Analysis results
        """
        analysis_results = {}
        
        try:
            # Run Signal Collapse analysis
            if "signal_collapse" in self.modules:
                try:
                    results = self.modules["signal_collapse"].run_analysis()
                    analysis_results["signal_collapse"] = results
                    
                    # Check for signal collapse
                    if results.get("signal_collapse_detected", False):
                        self._log_warning("Signal collapse detected, adjusting trading parameters")
                        # Implement risk reduction measures
                        self.config["grid_range_percentage"] *= 0.8
                        self.config["total_allocation"] *= 0.7
                except Exception as e:
                    self._log_error(f"Error running signal collapse analysis: {e}")
            
            # Run Capital Migration analysis
            if "capital_migration" in self.modules:
                try:
                    # Get current allocations (simplified)
                    current_allocations = {self.config["trading_pair"]: 100.0}
                    
                    results = self.modules["capital_migration"].run_analysis(current_allocations)
                    analysis_results["capital_migration"] = results
                    
                    # Check for migration recommendations
                    if "migration_plan" in results and "actions" in results["migration_plan"]:
                        actions = results["migration_plan"]["actions"]
                        if actions:
                            self._log_info(f"Capital migration recommends {len(actions)} actions")
                            # In a full implementation, would execute these actions
                except Exception as e:
                    self._log_error(f"Error running capital migration analysis: {e}")
            
            # Run Strategic Bifurcation analysis
            if "strategic_bifurcation" in self.modules:
                try:
                    results = self.modules["strategic_bifurcation"].run_analysis()
                    analysis_results["strategic_bifurcation"] = results
                    
                    # Check for strategy recommendations
                    if "active_strategy" in results:
                        self._log_info(f"Active strategy: {results['active_strategy']}")
                        # Strategy parameters are used in calculate_grid_prices()
                except Exception as e:
                    self._log_error(f"Error running strategic bifurcation analysis: {e}")
            
            # Run Technological Convergence analysis
            if "technological_convergence" in self.modules:
                try:
                    results = self.modules["technological_convergence"].run_analysis()
                    analysis_results["technological_convergence"] = results
                    
                    # Check for trading recommendations
                    if "recommendation" in results and "action" in results["recommendation"]:
                        action = results["recommendation"]["action"]
                        confidence = results["recommendation"]["confidence"]
                        self._log_info(f"Trading recommendation: {action} with {confidence} confidence")
                        # In a full implementation, would adjust trading based on recommendation
                except Exception as e:
                    self._log_error(f"Error running technological convergence analysis: {e}")
            
            # Run Survivability check
            if "survivability" in self.modules:
                try:
                    results = self.modules["survivability"].run_survivability_check(
                        current_price=self.current_price,
                        portfolio_value=self.portfolio_value
                    )
                    analysis_results["survivability"] = results
                    
                    # Check for emergency mode
                    if "emergency_mode" in results and results["emergency_mode"]:
                        self.emergency_mode = True
                        self._log_warning("Entering emergency mode")
                        
                        # Get emergency actions
                        if "emergency_actions" in results and "actions" in results["emergency_actions"]:
                            actions = results["emergency_actions"]["actions"]
                            self._log_warning(f"Emergency actions: {actions}")
                    else:
                        self.emergency_mode = False
                except Exception as e:
                    self._log_error(f"Error running survivability check: {e}")
            
            return analysis_results
            
        except Exception as e:
            self._log_error(f"Error running advanced analysis: {e}")
            return {"error": str(e)}
    
    def execute_trading_cycle(self):
        """
        Execute a complete trading cycle
        
        Returns:
            dict: Trading cycle results
        """
        try:
            self._log_info("Starting trading cycle")
            
            # Get current price
            price = self.get_current_price()
            if not price:
                return {"error": "Failed to get current price"}
            
            # Get account balance
            balance = self.get_account_balance()
            if not balance:
                return {"error": "Failed to get account balance"}
            
            # Run advanced analysis
            analysis_results = self.run_advanced_analysis()
            
            # Check if in emergency mode
            if self.emergency_mode:
                self._log_warning("In emergency mode, skipping trading operations")
                return {
                    "status": "emergency_mode",
                    "price": price,
                    "balance": balance,
                    "analysis_results": analysis_results
                }
            
            # Calculate grid prices
            grid_prices = self.calculate_grid_prices()
            if not grid_prices:
                return {"error": "Failed to calculate grid prices"}
            
            # Check existing orders
            order_status = self.check_orders()
            
            # Place new orders if needed
            new_orders = []
            
            # Determine allocation per grid level
            allocation_per_level = self.config["total_allocation"] / self.config["grid_levels"]
            
            # Place buy orders below current price
            for grid_price in grid_prices:
                if grid_price < self.current_price * 0.99:  # 1% buffer
                    # Calculate order volume based on allocation
                    volume = allocation_per_level / grid_price
                    
                    # Apply dynamic sizing if enabled
                    if self.config["dynamic_sizing"]:
                        # Increase volume for lower prices
                        distance = (self.current_price - grid_price) / self.current_price
                        volume *= (1 + distance * 2)
                    
                    # Place buy order
                    order_id = self.place_order("buy", grid_price, volume)
                    if order_id:
                        new_orders.append(order_id)
            
            # Place sell orders above current price
            for grid_price in grid_prices:
                if grid_price > self.current_price * 1.01:  # 1% buffer
                    # Calculate order volume
                    volume = allocation_per_level / grid_price
                    
                    # Apply dynamic sizing if enabled
                    if self.config["dynamic_sizing"]:
                        # Increase volume for higher prices
                        distance = (grid_price - self.current_price) / self.current_price
                        volume *= (1 + distance * 2)
                    
                    # Place sell order
                    order_id = self.place_order("sell", grid_price, volume)
                    if order_id:
                        new_orders.append(order_id)
            
            self._log_info(f"Trading cycle completed: {len(new_orders)} new orders placed")
            
            return {
                "status": "completed",
                "price": price,
                "balance": balance,
                "grid_prices": grid_prices,
                "order_status": order_status,
                "new_orders": len(new_orders),
                "analysis_results": analysis_results
            }
            
        except Exception as e:
            self._log_error(f"Error executing trading cycle: {e}")
            traceback.print_exc()
            return {"error": str(e)}
    
    def generate_report(self, days=7):
        """
        Generate performance report
        
        Args:
            days (int): Number of days to include in report
            
        Returns:
            dict: Performance report
        """
        try:
            self._log_info(f"Generating performance report for the last {days} days")
            
            # Get current price and balance
            current_price = self.get_current_price()
            balance = self.get_account_balance()
            
            # Get historical data
            if not self.kraken:
                return {"error": "Kraken API not initialized"}
                
            # Calculate time period
            since = datetime.now() - timedelta(days=days)
            since_unix = since.timestamp()
            
            # Get OHLC data
            pair = self.config["trading_pair"]
            ohlc, last = self.kraken.get_ohlc_data(pair, interval=1440, since=since_unix)  # Daily data
            
            # Calculate performance metrics
            start_price = ohlc['close'].iloc[0]
            end_price = ohlc['close'].iloc[-1]
            price_change = (end_price - start_price) / start_price * 100
            
            # Calculate volatility
            returns = ohlc['close'].pct_change().dropna()
            volatility = returns.std() * 100
            
            # Calculate max drawdown
            cumulative_returns = (1 + returns).cumprod()
            max_drawdown = (cumulative_returns / cumulative_returns.cummax() - 1).min() * 100
            
            # Get completed orders
            completed_orders_count = len(self.completed_orders)
            
            # Calculate profit from completed orders (simplified)
            profit = 0.0
            for order in self.completed_orders:
                if order["type"] == "sell":
                    profit += order["price"] * order["volume"]
                elif order["type"] == "buy":
                    profit -= order["price"] * order["volume"]
            
            # Create report
            report = {
                "timestamp": datetime.now().isoformat(),
                "period_days": days,
                "current_price": current_price,
                "portfolio_value": balance["total_value"] if balance else None,
                "price_change_percent": float(f"{price_change:.2f}"),
                "volatility_percent": float(f"{volatility:.2f}"),
                "max_drawdown_percent": float(f"{max_drawdown:.2f}"),
                "completed_orders": completed_orders_count,
                "estimated_profit": float(f"{profit:.2f}"),
                "active_orders": len(self.active_orders),
                "emergency_mode": self.emergency_mode
            }
            
            # Save report
            report_file = os.path.join(self.data_dir, f"performance_report_{datetime.now().strftime('%Y%m%d')}.json")
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            self._log_info(f"Performance report generated and saved to {report_file}")
            return report
            
        except Exception as e:
            self._log_error(f"Error generating report: {e}")
            return {"error": str(e)}
    
    def run(self):
        """
        Run the trading system continuously
        """
        self._log_info("Starting Enhanced Trading System")
        
        try:
            while True:
                # Execute trading cycle
                result = self.execute_trading_cycle()
                
                if "error" in result:
                    self._log_error(f"Trading cycle failed: {result['error']}")
                
                # Generate report once per day
                current_time = datetime.now()
                if current_time.hour == 0 and current_time.minute < 5:
                    self.generate_report()
                
                # Wait for next cycle
                wait_minutes = self.config["price_check_interval_minutes"]
                self._log_info(f"Waiting {wait_minutes} minutes until next cycle")
                time.sleep(wait_minutes * 60)
                
        except KeyboardInterrupt:
            self._log_info("Trading system stopped by user")
        except Exception as e:
            self._log_error(f"Unexpected error: {e}")
            traceback.print_exc()
        finally:
            self._log_info("Enhanced Trading System shutting down")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Enhanced XRP Trading Bot")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--generate_report", action="store_true", help="Generate performance report and exit")
    parser.add_argument("--report_days", type=int, default=7, help="Number of days to include in report")
    parser.add_argument("--test", action="store_true", help="Run in test mode (single cycle)")
    
    args = parser.parse_args()
    
    # Create trading system
    trading_system = EnhancedTradingSystem(config_path=args.config)
    
    # Generate report if requested
    if args.generate_report:
        report = trading_system.generate_report(days=args.report_days)
        print(json.dumps(report, indent=2))
        return
    
    # Run in test mode if requested
    if args.test:
        result = trading_system.execute_trading_cycle()
        print(json.dumps(result, indent=2))
        return
    
    # Run trading system
    trading_system.run()

if __name__ == "__main__":
    main()
