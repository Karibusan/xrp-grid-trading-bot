#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Enhanced Trading System for XRP Trading Bot v3.0
Main trading system that integrates all modules and handles the trading logic.
"""

import os
import sys
import json
import time
import logging
import traceback
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime, timedelta
import threading

class EnhancedTradingSystem:
    """
    Enhanced trading system for the XRP Trading Bot v3.0.
    Integrates all modules and handles the trading logic.
    """
    
    def __init__(self, config_manager=None, api_client=None, 
                notification_manager=None, error_handler=None):
        """
        Initialize the enhanced trading system.
        
        Args:
            config_manager: ConfigManager instance
            api_client: KrakenClient instance
            notification_manager: NotificationManager instance
            error_handler: ErrorHandler instance
        """
        self.logger = logging.getLogger('enhanced_trading_system')
        self.config_manager = config_manager
        self.api_client = api_client
        self.notification_manager = notification_manager
        self.error_handler = error_handler
        
        # Initialize state
        self.running = False
        self.trading_thread = None
        self.last_price = None
        self.grid_orders = []
        self.modules = {}
        
        # Load configuration
        self._load_configuration()
        
        # Initialize modules
        self._initialize_modules()
        
        self.logger.info("Enhanced Trading System initialized")
    
    def _load_configuration(self):
        """Load configuration from config manager."""
        if not self.config_manager:
            self.logger.error("Config manager not provided")
            return
            
        # Load main configuration
        self.trading_pair = self.config_manager.get_config("trading_pair", "XRPGBP")
        self.grid_range_percentage = self.config_manager.get_config("grid_range_percentage", 4.0)
        self.grid_levels = self.config_manager.get_config("grid_levels", 16)
        self.total_allocation = self.config_manager.get_config("total_allocation", 100.0)
        self.price_check_interval = self.config_manager.get_config("price_check_interval_minutes", 5) * 60
        self.dynamic_sizing = self.config_manager.get_config("dynamic_sizing", True)
        self.stop_loss_percentage = self.config_manager.get_config("stop_loss_percentage", 0.0)
        self.profit_reinvestment = self.config_manager.get_config("profit_reinvestment", 0.0)
        self.emergency_mode = self.config_manager.get_config("emergency_mode", False)
        self.debug_mode = self.config_manager.get_config("debug_mode", False)
        
        self.logger.info(f"Configuration loaded: trading pair={self.trading_pair}, grid levels={self.grid_levels}")
    
    def _initialize_modules(self):
        """Initialize trading modules."""
        if not self.config_manager:
            self.logger.error("Config manager not provided, cannot initialize modules")
            return
            
        modules_config = self.config_manager.get_config("modules", {})
        
        # Initialize Signal Collapse module
        if self.config_manager.is_module_enabled("signal_collapse"):
            try:
                from signal_collapse_module import SignalCollapseModule
                signal_collapse_config = self.config_manager.get_module_config("signal_collapse")
                self.modules["signal_collapse"] = SignalCollapseModule(
                    config=signal_collapse_config,
                    api_client=self.api_client,
                    error_handler=self.error_handler
                )
                self.logger.info("Signal Collapse module initialized")
            except Exception as e:
                self._handle_module_init_error("signal_collapse", e)
        
        # Initialize Capital Migration module
        if self.config_manager.is_module_enabled("capital_migration"):
            try:
                from capital_migration_module import CapitalMigrationModule
                capital_migration_config = self.config_manager.get_module_config("capital_migration")
                self.modules["capital_migration"] = CapitalMigrationModule(
                    config=capital_migration_config,
                    api_client=self.api_client,
                    error_handler=self.error_handler
                )
                self.logger.info("Capital Migration module initialized")
            except Exception as e:
                self._handle_module_init_error("capital_migration", e)
        
        # Initialize Strategic Bifurcation module
        if self.config_manager.is_module_enabled("strategic_bifurcation"):
            try:
                from strategic_bifurcation_module import StrategicBifurcationModule
                strategic_bifurcation_config = self.config_manager.get_module_config("strategic_bifurcation")
                self.modules["strategic_bifurcation"] = StrategicBifurcationModule(
                    config=strategic_bifurcation_config,
                    api_client=self.api_client,
                    error_handler=self.error_handler
                )
                self.logger.info("Strategic Bifurcation module initialized")
            except Exception as e:
                self._handle_module_init_error("strategic_bifurcation", e)
        
        # Initialize Technological Convergence module
        if self.config_manager.is_module_enabled("technological_convergence"):
            try:
                from technological_convergence_module import TechnologicalConvergenceModule
                technological_convergence_config = self.config_manager.get_module_config("technological_convergence")
                self.modules["technological_convergence"] = TechnologicalConvergenceModule(
                    config=technological_convergence_config,
                    api_client=self.api_client,
                    error_handler=self.error_handler
                )
                self.logger.info("Technological Convergence module initialized")
            except Exception as e:
                self._handle_module_init_error("technological_convergence", e)
        
        # Initialize Survivability module
        if self.config_manager.is_module_enabled("survivability"):
            try:
                from survivability_module import SurvivabilityModule
                survivability_config = self.config_manager.get_module_config("survivability")
                self.modules["survivability"] = SurvivabilityModule(
                    config=survivability_config,
                    api_client=self.api_client,
                    error_handler=self.error_handler
                )
                self.logger.info("Survivability module initialized")
            except Exception as e:
                self._handle_module_init_error("survivability", e)
    
    def _handle_module_init_error(self, module_name: str, exception: Exception):
        """
        Handle module initialization error.
        
        Args:
            module_name: Name of the module
            exception: Exception that occurred
        """
        error_msg = f"Failed to initialize {module_name} module: {str(exception)}"
        self.logger.error(error_msg)
        
        if self.error_handler:
            self.error_handler.handle_error(
                error_type="module_initialization_error",
                error_message=error_msg,
                exception=exception,
                severity="high",
                category="module",
                context={"module": module_name}
            )
    
    def start(self):
        """Start the trading system."""
        if self.running:
            self.logger.warning("Trading system already running")
            return
            
        self.running = True
        self.trading_thread = threading.Thread(target=self._trading_loop)
        self.trading_thread.daemon = True
        self.trading_thread.start()
        
        self.logger.info("Trading system started")
        
        if self.notification_manager:
            self.notification_manager.send_notification(
                title="XRP Trading Bot Started",
                message=f"Trading system started with pair {self.trading_pair}",
                level="status"
            )
    
    def stop(self):
        """Stop the trading system."""
        if not self.running:
            self.logger.warning("Trading system not running")
            return
            
        self.running = False
        if self.trading_thread:
            self.trading_thread.join(timeout=30)
            
        self.logger.info("Trading system stopped")
        
        if self.notification_manager:
            self.notification_manager.send_notification(
                title="XRP Trading Bot Stopped",
                message="Trading system stopped",
                level="status"
            )
    
    def _trading_loop(self):
        """Main trading loop."""
        self.logger.info("Trading loop started")
        
        while self.running:
            try:
                # Execute trading cycle
                self.execute_trading_cycle()
                
                # Sleep until next cycle
                time.sleep(self.price_check_interval)
                
            except Exception as e:
                error_msg = f"Error in trading loop: {str(e)}"
                self.logger.error(error_msg)
                
                if self.error_handler:
                    self.error_handler.handle_error(
                        error_type="trading_loop_error",
                        error_message=error_msg,
                        exception=e,
                        severity="high",
                        category="trading"
                    )
                
                # Sleep a bit to avoid rapid error loops
                time.sleep(60)
        
        self.logger.info("Trading loop stopped")
    
    def execute_trading_cycle(self):
        """Execute a single trading cycle."""
        self.logger.info("Executing trading cycle")
        
        # Skip if in emergency mode
        if self.emergency_mode:
            self.logger.warning("Emergency mode active, skipping trading cycle")
            return
        
        # Get current price
        current_price = self._get_current_price()
        if not current_price:
            self.logger.error("Failed to get current price, skipping trading cycle")
            return
            
        self.logger.info(f"Current price: {current_price}")
        
        # Update last price
        self.last_price = current_price
        
        # Run advanced analysis
        analysis_results = self.run_advanced_analysis(current_price)
        
        # Check if trading should be skipped based on analysis
        if analysis_results.get("skip_trading", False):
            self.logger.info("Skipping trading based on advanced analysis")
            return
        
        # Update grid if needed
        self._update_grid(current_price, analysis_results)
        
        # Check open orders
        open_orders = self._get_open_orders()
        
        # Check for filled orders and process them
        self._process_filled_orders(open_orders)
        
        # Place new orders if needed
        self._place_new_orders(current_price, analysis_results)
        
        # Send status notification if enabled
        self._send_status_notification(current_price, open_orders, analysis_results)
        
        self.logger.info("Trading cycle completed")
    
    def run_advanced_analysis(self, current_price: float) -> Dict[str, Any]:
        """
        Run advanced analysis using all enabled modules.
        
        Args:
            current_price: Current price
            
        Returns:
            Dictionary with analysis results
        """
        self.logger.info("Running advanced analysis")
        
        results = {
            "skip_trading": False,
            "grid_adjustment": 0.0,
            "risk_factor": 1.0,
            "market_trend": "neutral",
            "recommendations": []
        }
        
        # Run Signal Collapse analysis
        if "signal_collapse" in self.modules:
            try:
                signal_collapse_results = self.modules["signal_collapse"].analyze(current_price)
                results["signal_collapse"] = signal_collapse_results
                
                # Update overall results based on signal collapse analysis
                if signal_collapse_results.get("emergency_stop", False):
                    results["skip_trading"] = True
                    results["recommendations"].append("Emergency stop triggered by Signal Collapse module")
                
                if "risk_adjustment" in signal_collapse_results:
                    results["risk_factor"] *= signal_collapse_results["risk_adjustment"]
                
                self.logger.debug(f"Signal Collapse analysis: {signal_collapse_results}")
            except Exception as e:
                self._handle_module_analysis_error("signal_collapse", e)
        
        # Run Capital Migration analysis
        if "capital_migration" in self.modules:
            try:
                capital_migration_results = self.modules["capital_migration"].analyze(current_price)
                results["capital_migration"] = capital_migration_results
                
                # Update overall results based on capital migration analysis
                if "grid_adjustment" in capital_migration_results:
                    results["grid_adjustment"] += capital_migration_results["grid_adjustment"]
                
                if "market_trend" in capital_migration_results:
                    results["market_trend"] = capital_migration_results["market_trend"]
                
                self.logger.debug(f"Capital Migration analysis: {capital_migration_results}")
            except Exception as e:
                self._handle_module_analysis_error("capital_migration", e)
        
        # Run Strategic Bifurcation analysis
        if "strategic_bifurcation" in self.modules:
            try:
                strategic_bifurcation_results = self.modules["strategic_bifurcation"].analyze(current_price)
                results["strategic_bifurcation"] = strategic_bifurcation_results
                
                # Update overall results based on strategic bifurcation analysis
                if "recommendations" in strategic_bifurcation_results:
                    results["recommendations"].extend(strategic_bifurcation_results["recommendations"])
                
                self.logger.debug(f"Strategic Bifurcation analysis: {strategic_bifurcation_results}")
            except Exception as e:
                self._handle_module_analysis_error("strategic_bifurcation", e)
        
        # Run Technological Convergence analysis
        if "technological_convergence" in self.modules:
            try:
                technological_convergence_results = self.modules["technological_convergence"].analyze(current_price)
                results["technological_convergence"] = technological_convergence_results
                
                # Update overall results based on technological convergence analysis
                if "risk_factor" in technological_convergence_results:
                    results["risk_factor"] *= technological_convergence_results["risk_factor"]
                
                self.logger.debug(f"Technological Convergence analysis: {technological_convergence_results}")
            except Exception as e:
                self._handle_module_analysis_error("technological_convergence", e)
        
        # Run Survivability analysis
        if "survivability" in self.modules:
            try:
                survivability_results = self.modules["survivability"].analyze(current_price)
                results["survivability"] = survivability_results
                
                # Update overall results based on survivability analysis
                if survivability_results.get("emergency_mode", False):
                    results["skip_trading"] = True
                    results["recommendations"].append("Emergency mode triggered by Survivability module")
                
                self.logger.debug(f"Survivability analysis: {survivability_results}")
            except Exception as e:
                self._handle_module_analysis_error("survivability", e)
        
        # Ensure risk factor is within reasonable bounds
        results["risk_factor"] = max(0.1, min(results["risk_factor"], 3.0))
        
        self.logger.info(f"Advanced analysis results: skip_trading={results['skip_trading']}, risk_factor={results['risk_factor']}, market_trend={results['market_trend']}")
        
        return results
    
    def _handle_module_analysis_error(self, module_name: str, exception: Exception):
        """
        Handle module analysis error.
        
        Args:
            module_name: Name of the module
            exception: Exception that occurred
        """
        error_msg = f"Error in {module_name} module analysis: {str(exception)}"
        self.logger.error(error_msg)
        
        if self.error_handler:
            self.error_handler.handle_error(
                error_type="module_analysis_error",
                error_message=error_msg,
                exception=exception,
                severity="medium",
                category="module",
                context={"module": module_name}
            )
    
    def _get_current_price(self) -> Optional[float]:
        """
        Get current price from API.
        
        Returns:
            Current price or None if failed
        """
        if not self.api_client:
            self.logger.error("API client not provided")
            return None
            
        try:
            ticker_info = self.api_client.get_ticker(self.trading_pair)
            
            if "result" in ticker_info and self.trading_pair in ticker_info["result"]:
                pair_data = ticker_info["result"][self.trading_pair]
                current_price = float(pair_data["c"][0])
                return current_price
            else:
                error_msg = f"Failed to get ticker data: {ticker_info.get('error', 'Unknown error')}"
                self.logger.error(error_msg)
                
                if self.error_handler:
                    self.error_handler.handle_error(
                        error_type="ticker_data_error",
                        error_message=error_msg,
                        severity="high",
                        category="api"
                    )
                
                return None
                
        except Exception as e:
            error_msg = f"Error getting current price: {str(e)}"
            self.logger.error(error_msg)
            
            if self.error_handler:
                self.error_handler.handle_error(
                    error_type="price_fetch_error",
                    error_message=error_msg,
                    exception=e,
                    severity="high",
                    category="api"
                )
            
            return None
    
    def _update_grid(self, current_price: float, analysis_results: Dict[str, Any]):
        """
        Update grid based on current price and analysis results.
        
        Args:
            current_price: Current price
            analysis_results: Analysis results from modules
        """
        # Calculate grid range
        adjusted_range = self.grid_range_percentage
        
        # Apply grid adjustment from analysis
        if "grid_adjustment" in analysis_results:
            adjusted_range += analysis_results["grid_adjustment"]
            
        # Ensure grid range is within reasonable bounds
        adjusted_range = max(0.5, min(adjusted_range, 20.0))
        
        # Calculate grid boundaries
        half_range = adjusted_range / 2
        lower_bound = current_price * (1 - half_range / 100)
        upper_bound = current_price * (1 + half_range / 100)
        
        # Calculate grid levels
        self.grid_prices = []
        for i in range(self.grid_levels):
            level_price = lower_bound + (upper_bound - lower_bound) * i / (self.grid_levels - 1)
            self.grid_prices.append(level_price)
            
        self.logger.info(f"Grid updated: {self.grid_levels} levels from {lower_bound:.4f} to {upper_bound:.4f}")
    
    def _get_open_orders(self) -> List[Dict[str, Any]]:
        """
        Get open orders from API.
        
        Returns:
            List of open orders
        """
        if not self.api_client:
            self.logger.error("API client not provided")
            return []
            
        try:
            open_orders_response = self.api_client.get_open_orders()
            
            if "result" in open_orders_response and "open" in open_orders_response["result"]:
                open_orders = []
                
                for order_id, order_data in open_orders_response["result"]["open"].items():
                    # Filter orders for our trading pair
                    if order_data["descr"]["pair"] == self.trading_pair:
                        order = {
                            "order_id": order_id,
                            "type": order_data["descr"]["type"],
                            "price": float(order_data["descr"]["price"]),
                            "volume": float(order_data["vol"]),
                            "status": order_data["status"]
                        }
                        open_orders.append(order)
                
                self.logger.info(f"Found {len(open_orders)} open orders for {self.trading_pair}")
                return open_orders
            else:
                error_msg = f"Failed to get open orders: {open_orders_response.get('error', 'Unknown error')}"
                self.logger.error(error_msg)
                
                if self.error_handler:
                    self.error_handler.handle_error(
                        error_type="open_orders_error",
                        error_message=error_msg,
                        severity="medium",
                        category="api"
                    )
                
                return []
                
        except Exception as e:
            error_msg = f"Error getting open orders: {str(e)}"
            self.logger.error(error_msg)
            
            if self.error_handler:
                self.error_handler.handle_error(
                    error_type="open_orders_fetch_error",
                    error_message=error_msg,
                    exception=e,
                    severity="medium",
                    category="api"
                )
            
            return []
    
    def _process_filled_orders(self, open_orders: List[Dict[str, Any]]):
        """
        Process filled orders.
        
        Args:
            open_orders: List of current open orders
        """
        # Compare with previous grid orders to find filled orders
        filled_orders = []
        
        for prev_order in self.grid_orders:
            # Check if order is no longer in open orders
            if not any(o["order_id"] == prev_order["order_id"] for o in open_orders):
                filled_orders.append(prev_order)
        
        # Update grid orders
        self.grid_orders = open_orders
        
        # Process each filled order
        for order in filled_orders:
            self.logger.info(f"Order filled: {order['order_id']} - {order['type']} {order['volume']} at {order['price']}")
            
            # Calculate total value
            total = order["price"] * order["volume"]
            
            # Send notification
            if self.notification_manager:
                self.notification_manager.send_trade_notification(
                    trade_type=order["type"],
                    volume=order["volume"],
                    price=order["price"],
                    total=total
                )
            
            # Place opposite order
            self._place_opposite_order(order)
    
    def _place_opposite_order(self, filled_order: Dict[str, Any]):
        """
        Place opposite order after a fill.
        
        Args:
            filled_order: Order that was filled
        """
        if not self.api_client:
            self.logger.error("API client not provided")
            return
            
        try:
            # Determine opposite order type
            opposite_type = "sell" if filled_order["type"] == "buy" else "buy"
            
            # Calculate price with profit margin for sell orders
            price = filled_order["price"]
            if opposite_type == "sell":
                # Add profit margin (e.g., 1%)
                price *= 1.01
            else:
                # Reduce price for buy orders
                price *= 0.99
            
            # Place order
            order_result = self.api_client.place_order(
                pair=self.trading_pair,
                type=opposite_type,
                ordertype="limit",
                volume=filled_order["volume"],
                price=price
            )
            
            if "result" in order_result and "txid" in order_result["result"]:
                order_id = order_result["result"]["txid"][0]
                self.logger.info(f"Placed opposite {opposite_type} order {order_id} at {price}")
            else:
                error_msg = f"Failed to place opposite order: {order_result.get('error', 'Unknown error')}"
                self.logger.error(error_msg)
                
                if self.error_handler:
                    self.error_handler.handle_error(
                        error_type="order_placement_error",
                        error_message=error_msg,
                        severity="medium",
                        category="trading"
                    )
                
        except Exception as e:
            error_msg = f"Error placing opposite order: {str(e)}"
            self.logger.error(error_msg)
            
            if self.error_handler:
                self.error_handler.handle_error(
                    error_type="order_placement_error",
                    error_message=error_msg,
                    exception=e,
                    severity="medium",
                    category="trading"
                )
    
    def _place_new_orders(self, current_price: float, analysis_results: Dict[str, Any]):
        """
        Place new orders based on grid and analysis.
        
        Args:
            current_price: Current price
            analysis_results: Analysis results from modules
        """
        if not self.api_client:
            self.logger.error("API client not provided")
            return
            
        # Get account balance
        balance = self._get_account_balance()
        if not balance:
            self.logger.error("Failed to get account balance, cannot place new orders")
            return
            
        # Calculate order size based on total allocation and grid levels
        base_order_size = self.total_allocation / self.grid_levels
        
        # Apply risk factor from analysis
        risk_factor = analysis_results.get("risk_factor", 1.0)
        adjusted_order_size = base_order_size * risk_factor
        
        # Ensure minimum order size
        min_order_size = 10.0  # Minimum order size in base currency
        adjusted_order_size = max(adjusted_order_size, min_order_size)
        
        # Place buy orders below current price
        for price in self.grid_prices:
            if price < current_price * 0.99:  # Avoid placing orders too close to current price
                # Check if we already have an open order at this price
                if any(abs(o["price"] - price) / price < 0.005 and o["type"] == "buy" for o in self.grid_orders):
                    continue
                    
                # Calculate volume in quote currency
                volume = adjusted_order_size / price
                
                try:
                    order_result = self.api_client.place_order(
                        pair=self.trading_pair,
                        type="buy",
                        ordertype="limit",
                        volume=volume,
                        price=price
                    )
                    
                    if "result" in order_result and "txid" in order_result["result"]:
                        order_id = order_result["result"]["txid"][0]
                        self.logger.info(f"Placed buy order {order_id} for {volume} at {price}")
                    else:
                        error_msg = f"Failed to place buy order: {order_result.get('error', 'Unknown error')}"
                        self.logger.error(error_msg)
                        
                        if self.error_handler:
                            self.error_handler.handle_error(
                                error_type="order_placement_error",
                                error_message=error_msg,
                                severity="medium",
                                category="trading"
                            )
                    
                except Exception as e:
                    error_msg = f"Error placing buy order: {str(e)}"
                    self.logger.error(error_msg)
                    
                    if self.error_handler:
                        self.error_handler.handle_error(
                            error_type="order_placement_error",
                            error_message=error_msg,
                            exception=e,
                            severity="medium",
                            category="trading"
                        )
        
        # Place sell orders above current price
        for price in self.grid_prices:
            if price > current_price * 1.01:  # Avoid placing orders too close to current price
                # Check if we already have an open order at this price
                if any(abs(o["price"] - price) / price < 0.005 and o["type"] == "sell" for o in self.grid_orders):
                    continue
                    
                # Calculate volume in base currency
                volume = adjusted_order_size / current_price
                
                try:
                    order_result = self.api_client.place_order(
                        pair=self.trading_pair,
                        type="sell",
                        ordertype="limit",
                        volume=volume,
                        price=price
                    )
                    
                    if "result" in order_result and "txid" in order_result["result"]:
                        order_id = order_result["result"]["txid"][0]
                        self.logger.info(f"Placed sell order {order_id} for {volume} at {price}")
                    else:
                        error_msg = f"Failed to place sell order: {order_result.get('error', 'Unknown error')}"
                        self.logger.error(error_msg)
                        
                        if self.error_handler:
                            self.error_handler.handle_error(
                                error_type="order_placement_error",
                                error_message=error_msg,
                                severity="medium",
                                category="trading"
                            )
                    
                except Exception as e:
                    error_msg = f"Error placing sell order: {str(e)}"
                    self.logger.error(error_msg)
                    
                    if self.error_handler:
                        self.error_handler.handle_error(
                            error_type="order_placement_error",
                            error_message=error_msg,
                            exception=e,
                            severity="medium",
                            category="trading"
                        )
    
    def _get_account_balance(self) -> Optional[Dict[str, float]]:
        """
        Get account balance from API.
        
        Returns:
            Dictionary with account balances or None if failed
        """
        if not self.api_client:
            self.logger.error("API client not provided")
            return None
            
        try:
            balance_response = self.api_client.get_account_balance()
            
            if "result" in balance_response:
                balances = {}
                
                for asset, amount in balance_response["result"].items():
                    balances[asset] = float(amount)
                
                self.logger.info(f"Account balance retrieved: {balances}")
                return balances
            else:
                error_msg = f"Failed to get account balance: {balance_response.get('error', 'Unknown error')}"
                self.logger.error(error_msg)
                
                if self.error_handler:
                    self.error_handler.handle_error(
                        error_type="balance_fetch_error",
                        error_message=error_msg,
                        severity="high",
                        category="api"
                    )
                
                return None
                
        except Exception as e:
            error_msg = f"Error getting account balance: {str(e)}"
            self.logger.error(error_msg)
            
            if self.error_handler:
                self.error_handler.handle_error(
                    error_type="balance_fetch_error",
                    error_message=error_msg,
                    exception=e,
                    severity="high",
                    category="api"
                )
            
            return None
    
    def _send_status_notification(self, current_price: float, open_orders: List[Dict[str, Any]], 
                                analysis_results: Dict[str, Any]):
        """
        Send status notification.
        
        Args:
            current_price: Current price
            open_orders: List of open orders
            analysis_results: Analysis results from modules
        """
        if not self.notification_manager:
            return
            
        # Count buy and sell orders
        buy_orders = sum(1 for o in open_orders if o["type"] == "buy")
        sell_orders = sum(1 for o in open_orders if o["type"] == "sell")
        
        # Get account balance
        balance = self._get_account_balance()
        
        # Prepare status data
        status_data = {
            "current_price": current_price,
            "open_orders": len(open_orders),
            "buy_orders": buy_orders,
            "sell_orders": sell_orders,
            "grid_levels": self.grid_levels,
            "risk_factor": analysis_results.get("risk_factor", 1.0),
            "market_trend": analysis_results.get("market_trend", "neutral"),
            "emergency_mode": self.emergency_mode,
            "balance": balance
        }
        
        # Send efficiency notification
        self.notification_manager.send_efficiency_notification({
            "cpu_usage": 0.0,  # Placeholder, would need system monitoring
            "memory_usage": 0.0,  # Placeholder, would need system monitoring
            "api_calls": self.api_client.get_api_stats()["calls"]["total"] if self.api_client else 0,
            "response_time": self.api_client.get_api_stats()["avg_response_time"] if self.api_client else 0,
            "execution_time": 0.0,  # Placeholder, would need timing
            "additional_metrics": f"Open Orders: {len(open_orders)}, Risk Factor: {analysis_results.get('risk_factor', 1.0)}"
        })


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create mock components
    class MockConfigManager:
        def get_config(self, key, default=None):
            config = {
                "trading_pair": "XRPGBP",
                "grid_range_percentage": 4.0,
                "grid_levels": 16,
                "total_allocation": 100.0,
                "price_check_interval_minutes": 5,
                "dynamic_sizing": True,
                "stop_loss_percentage": 10.0,
                "profit_reinvestment": 50.0,
                "emergency_mode": False,
                "debug_mode": True,
                "modules": {}
            }
            return config.get(key, default)
            
        def get_module_config(self, module_name, key=None, default=None):
            return {}
            
        def is_module_enabled(self, module_name):
            return False
    
    class MockAPIClient:
        def get_ticker(self, pair):
            return {"result": {pair: {"c": ["0.5000", "100"]}}}
            
        def get_open_orders(self):
            return {"result": {"open": {}}}
            
        def get_account_balance(self):
            return {"result": {"XRP": "1000.0", "GBP": "500.0"}}
            
        def place_order(self, pair, type, ordertype, volume, price):
            return {"result": {"txid": ["ABCDEF-12345"]}}
            
        def get_api_stats(self):
            return {"calls": {"total": 10}, "avg_response_time": 0.2}
    
    class MockNotificationManager:
        def send_notification(self, title, message, level=None):
            print(f"NOTIFICATION: {title} - {message}")
            
        def send_trade_notification(self, trade_type, volume, price, total):
            print(f"TRADE: {trade_type} {volume} at {price}, total: {total}")
            
        def send_efficiency_notification(self, metrics):
            print(f"EFFICIENCY: {metrics}")
    
    class MockErrorHandler:
        def handle_error(self, error_type, error_message, exception=None, severity=None, category=None, context=None):
            print(f"ERROR: {error_type} - {error_message}")
    
    # Create trading system
    trading_system = EnhancedTradingSystem(
        config_manager=MockConfigManager(),
        api_client=MockAPIClient(),
        notification_manager=MockNotificationManager(),
        error_handler=MockErrorHandler()
    )
    
    # Execute a trading cycle
    trading_system.execute_trading_cycle()
