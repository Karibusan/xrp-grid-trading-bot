#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Strategic Bifurcation Module for XRP Trading Bot
Version: 1.0.0
Description: Module that implements multiple trading strategies and
automatically switches between them based on detected market conditions.
"""

import numpy as np
import pandas as pd
import time
import json
import os
import logging
from datetime import datetime, timedelta
import krakenex
from pykrakenapi import KrakenAPI

class StrategicBifurcationManager:
    """
    A module that implements multiple trading strategies and
    automatically switches between them based on detected market conditions.
    """
    
    def __init__(self, config_path=None, api_key=None, api_secret=None):
        """
        Initialize the Strategic Bifurcation Manager module.
        
        Args:
            config_path (str): Path to configuration file
            api_key (str): Kraken API key
            api_secret (str): Kraken API secret
        """
        # Default configuration
        self.default_config = {
            "enabled": True,
            "trading_pair": "XRPGBP",
            "check_interval_hours": 4,
            "market_regime_lookback_days": 7,
            "volatility_threshold": 5.0,
            "trend_threshold": 3.0,
            "range_threshold": 2.0,
            "strategies": ["trend_following", "mean_reversion", "range_trading", "volatility_breakout"],
            "log_file": "strategic_bifurcation_log.txt",
            "data_file": "strategic_bifurcation_data.json"
        }
        
        # Load configuration
        self.config = self.default_config.copy()
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                    self.config.update(user_config)
            except Exception as e:
                self._log_error(f"Error loading configuration: {str(e)}")
        
        # Setup logging
        self.log_dir = os.path.dirname(self.config["log_file"])
        if self.log_dir and not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
            
        logging.basicConfig(
            filename=self.config["log_file"],
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Initialize Kraken API
        self.kraken = None
        if api_key and api_secret:
            try:
                api = krakenex.API(key=api_key, secret=api_secret)
                self.kraken = KrakenAPI(api)
            except Exception as e:
                self._log_error(f"Error initializing Kraken API: {str(e)}")
        
        # Initialize data storage
        self.data_dir = os.path.dirname(self.config["data_file"])
        if self.data_dir and not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
        self.market_data = None
        self.market_regime = None
        self.active_strategy = None
        self.strategy_parameters = {}
        self.last_check_time = None
        
        self._log_info("Strategic Bifurcation Manager initialized")
    
    def _log_info(self, message):
        """Log informational message"""
        logging.info(message)
        
    def _log_error(self, message):
        """Log error message"""
        logging.error(message)
        
    def _log_warning(self, message):
        """Log warning message"""
        logging.warning(message)
    
    def fetch_market_data(self):
        """
        Fetch market data from Kraken API
        
        Returns:
            bool: Success status
        """
        if not self.kraken:
            self._log_error("Kraken API not initialized")
            return False
            
        try:
            # Calculate time period to fetch
            lookback_days = self.config["market_regime_lookback_days"]
            since = datetime.now() - timedelta(days=lookback_days)
            since_unix = since.timestamp()
            
            # Fetch OHLC data (1 hour intervals)
            pair = self.config["trading_pair"]
            ohlc, last = self.kraken.get_ohlc_data(pair, interval=60, since=since_unix)
            
            # Store data
            self.market_data = ohlc
            self._log_info(f"Fetched {len(ohlc)} OHLC records")
            return True
            
        except Exception as e:
            self._log_error(f"Error fetching market data: {str(e)}")
            return False
    
    def detect_market_regime(self):
        """
        Detect current market regime based on price action
        
        Returns:
            bool: Success status
        """
        if self.market_data is None or len(self.market_data) < 24:
            self._log_error("Insufficient market data for regime detection")
            return False
            
        try:
            # Extract close prices
            close_prices = self.market_data['close'].values
            
            # Calculate metrics
            returns = np.diff(close_prices) / close_prices[:-1]
            volatility = np.std(returns) * 100  # Convert to percentage
            
            # Calculate trend (price change over period)
            start_price = close_prices[0]
            end_price = close_prices[-1]
            trend = ((end_price - start_price) / start_price) * 100  # Convert to percentage
            
            # Calculate range (max - min) / min
            price_range = ((np.max(close_prices) - np.min(close_prices)) / np.min(close_prices)) * 100
            
            # Calculate directional consistency
            positive_returns = np.sum(returns > 0)
            negative_returns = np.sum(returns < 0)
            directional_consistency = abs(positive_returns - negative_returns) / len(returns)
            
            # Detect regime
            if volatility > self.config["volatility_threshold"] and directional_consistency < 0.3:
                regime = "volatile"
            elif abs(trend) > self.config["trend_threshold"] and directional_consistency > 0.6:
                regime = "trending" if trend > 0 else "downtrending"
            elif price_range < self.config["range_threshold"]:
                regime = "ranging"
            else:
                regime = "mixed"
            
            # Store regime information
            self.market_regime = {
                "timestamp": datetime.now().isoformat(),
                "regime": regime,
                "metrics": {
                    "volatility": float(f"{volatility:.2f}"),
                    "trend": float(f"{trend:.2f}"),
                    "price_range": float(f"{price_range:.2f}"),
                    "directional_consistency": float(f"{directional_consistency:.2f}")
                }
            }
            
            # Save regime information
            try:
                with open(self.config["data_file"], 'w') as f:
                    json.dump(self.market_regime, f, indent=2)
            except Exception as e:
                self._log_error(f"Error saving market regime: {str(e)}")
            
            self._log_info(f"Detected market regime: {regime}")
            return True
            
        except Exception as e:
            self._log_error(f"Error detecting market regime: {str(e)}")
            return False
    
    def select_strategy(self):
        """
        Select appropriate trading strategy based on market regime
        
        Returns:
            bool: Success status
        """
        if not self.market_regime:
            self._log_error("No market regime detected")
            return False
            
        try:
            regime = self.market_regime["regime"]
            
            # Select strategy based on regime
            if regime == "trending":
                strategy = "trend_following"
            elif regime == "downtrending":
                strategy = "trend_following"  # Same strategy but with different parameters
            elif regime == "volatile":
                strategy = "volatility_breakout"
            elif regime == "ranging":
                strategy = "range_trading"
            else:  # mixed
                strategy = "mean_reversion"
            
            # Check if strategy is enabled
            if strategy not in self.config["strategies"]:
                self._log_warning(f"Selected strategy {strategy} is not enabled, using mean_reversion as fallback")
                strategy = "mean_reversion"
            
            # Update active strategy
            self.active_strategy = strategy
            self._log_info(f"Selected strategy: {strategy}")
            
            # Generate strategy parameters
            self._generate_strategy_parameters()
            
            return True
            
        except Exception as e:
            self._log_error(f"Error selecting strategy: {str(e)}")
            return False
    
    def _generate_strategy_parameters(self):
        """
        Generate parameters for the active strategy
        
        Returns:
            bool: Success status
        """
        if not self.active_strategy:
            self._log_error("No active strategy selected")
            return False
            
        try:
            # Extract metrics
            metrics = self.market_regime["metrics"]
            volatility = metrics["volatility"]
            trend = metrics["trend"]
            price_range = metrics["price_range"]
            
            # Generate parameters based on strategy
            if self.active_strategy == "trend_following":
                # For trending markets, wider grid with more levels
                self.strategy_parameters = {
                    "grid_range_percentage": max(3.0, min(8.0, abs(trend) * 1.5)),
                    "grid_levels": max(10, min(20, int(abs(trend) * 1.2))),
                    "grid_distribution": "exponential",
                    "order_timeout_hours": 48,
                    "dynamic_sizing": True,
                    "stop_loss_percentage": 15.0,
                    "profit_reinvestment": True
                }
                
            elif self.active_strategy == "mean_reversion":
                # For mean reversion, tighter grid with more levels
                self.strategy_parameters = {
                    "grid_range_percentage": max(2.0, min(5.0, volatility * 0.8)),
                    "grid_levels": max(16, min(24, int(volatility * 2))),
                    "grid_distribution": "normal",
                    "order_timeout_hours": 24,
                    "dynamic_sizing": True,
                    "stop_loss_percentage": 10.0,
                    "profit_reinvestment": False
                }
                
            elif self.active_strategy == "range_trading":
                # For ranging markets, tight grid with many levels
                self.strategy_parameters = {
                    "grid_range_percentage": max(1.5, min(4.0, price_range * 0.7)),
                    "grid_levels": max(20, min(30, int(price_range * 3))),
                    "grid_distribution": "uniform",
                    "order_timeout_hours": 12,
                    "dynamic_sizing": False,
                    "stop_loss_percentage": 8.0,
                    "profit_reinvestment": True
                }
                
            elif self.active_strategy == "volatility_breakout":
                # For volatile markets, wider grid with fewer levels
                self.strategy_parameters = {
                    "grid_range_percentage": max(4.0, min(10.0, volatility * 1.2)),
                    "grid_levels": max(8, min(16, int(volatility))),
                    "grid_distribution": "power",
                    "order_timeout_hours": 6,
                    "dynamic_sizing": True,
                    "stop_loss_percentage": 20.0,
                    "profit_reinvestment": False
                }
            
            self._log_info(f"Generated parameters for {self.active_strategy}: {self.strategy_parameters}")
            return True
            
        except Exception as e:
            self._log_error(f"Error generating strategy parameters: {str(e)}")
            return False
    
    def get_strategy_configuration(self):
        """
        Get complete configuration for the active strategy
        
        Returns:
            dict: Strategy configuration
        """
        if not self.active_strategy or not self.strategy_parameters:
            self._log_error("No active strategy or parameters available")
            return None
            
        try:
            # Combine base configuration with strategy parameters
            strategy_config = {
                "trading_pair": self.config["trading_pair"],
                "strategy": self.active_strategy,
                "market_regime": self.market_regime["regime"],
                "parameters": self.strategy_parameters
            }
            
            return strategy_config
            
        except Exception as e:
            self._log_error(f"Error getting strategy configuration: {str(e)}")
            return None
    
    def run_analysis(self):
        """
        Run a complete analysis cycle
        
        Returns:
            dict: Analysis results
        """
        if not self.config["enabled"]:
            self._log_info("Strategic Bifurcation Manager is disabled")
            return {"enabled": False}
            
        self._log_info("Starting strategic bifurcation analysis")
        
        # Check if it's time to run analysis
        current_time = datetime.now()
        if self.last_check_time:
            time_diff = (current_time - self.last_check_time).total_seconds() / 3600
            if time_diff < self.config["check_interval_hours"]:
                self._log_info(f"Skipping analysis, last check was {time_diff:.1f} hours ago")
                
                # Return last strategy if available
                if self.active_strategy and self.strategy_parameters:
                    return {
                        "skipped": True, 
                        "next_check_in_hours": self.config["check_interval_hours"] - time_diff,
                        "active_strategy": self.active_strategy,
                        "strategy_parameters": self.strategy_parameters
                    }
                else:
                    return {
                        "skipped": True, 
                        "next_check_in_hours": self.config["check_interval_hours"] - time_diff
                    }
        
        # Update last check time
        self.last_check_time = current_time
        
        # Fetch market data
        if not self.fetch_market_data():
            return {"error": "Failed to fetch market data"}
            
        # Detect market regime
        if not self.detect_market_regime():
            return {"error": "Failed to detect market regime"}
            
        # Select strategy
        if not self.select_strategy():
            return {"error": "Failed to select strategy"}
            
        # Get strategy configuration
        strategy_config = self.get_strategy_configuration()
        
        self._log_info("Strategic bifurcation analysis completed")
        
        return {
            "timestamp": current_time.isoformat(),
            "market_regime": self.market_regime,
            "active_strategy": self.active_strategy,
            "strategy_parameters": self.strategy_parameters,
            "strategy_configuration": strategy_config,
            "next_check_in_hours": self.config["check_interval_hours"]
        }

# Example usage
if __name__ == "__main__":
    # Create data directory if it doesn't exist
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        
    # Configuration
    config = {
        "enabled": True,
        "trading_pair": "XRPGBP",
        "check_interval_hours": 4,
        "market_regime_lookback_days": 7,
        "volatility_threshold": 5.0,
        "trend_threshold": 3.0,
        "range_threshold": 2.0,
        "strategies": ["trend_following", "mean_reversion", "range_trading", "volatility_breakout"],
        "log_file": f"{data_dir}/strategic_bifurcation_log.txt",
        "data_file": f"{data_dir}/strategic_bifurcation_data.json"
    }
    
    # Save config
    with open(f"{data_dir}/strategic_bifurcation_config.json", 'w') as f:
        json.dump(config, f, indent=2)
        
    print("Strategic Bifurcation Manager module created.")
    print("To use this module with your XRP Trading Bot:")
    print("1. Place this file in the same directory as your main bot script")
    print("2. Import the module in your main script:")
    print("   from strategic_bifurcation_module import StrategicBifurcationManager")
    print("3. Initialize the manager with your API keys:")
    print("   manager = StrategicBifurcationManager(config_path='data/strategic_bifurcation_config.json', api_key=YOUR_API_KEY, api_secret=YOUR_API_SECRET)")
    print("4. Run the analysis periodically:")
    print("   results = manager.run_analysis()")
    print("5. Use the strategy configuration to adjust your trading parameters")
