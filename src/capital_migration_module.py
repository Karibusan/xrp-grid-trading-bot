#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Capital Migration Module for XRP Trading Bot
Version: 1.0.0
Description: Module that analyzes multiple trading pairs and recommends
optimal capital allocation between them based on market conditions.
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

class CapitalMigrationManager:
    """
    A module that analyzes multiple trading pairs and recommends
    optimal capital allocation between them based on market conditions.
    """
    
    def __init__(self, config_path=None, api_key=None, api_secret=None):
        """
        Initialize the Capital Migration Manager module.
        
        Args:
            config_path (str): Path to configuration file
            api_key (str): Kraken API key
            api_secret (str): Kraken API secret
        """
        # Default configuration
        self.default_config = {
            "enabled": True,
            "trading_pairs": ["XRPGBP", "XRPEUR", "XRPUSD"],
            "check_interval_hours": 6,
            "volatility_weight": 0.3,
            "trend_weight": 0.4,
            "volume_weight": 0.3,
            "min_allocation_percentage": 10,
            "max_allocation_percentage": 70,
            "log_file": "capital_migration_log.txt",
            "data_file": "capital_migration_data.json"
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
            
        self.market_data = {}
        self.pair_metrics = {}
        self.allocation_recommendation = {}
        self.last_check_time = None
        
        self._log_info("Capital Migration Manager initialized")
    
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
        Fetch market data for all trading pairs from Kraken API
        
        Returns:
            bool: Success status
        """
        if not self.kraken:
            self._log_error("Kraken API not initialized")
            return False
            
        try:
            # Calculate time period to fetch (7 days)
            since = datetime.now() - timedelta(days=7)
            since_unix = since.timestamp()
            
            # Reset market data
            self.market_data = {}
            
            # Fetch data for each trading pair
            for pair in self.config["trading_pairs"]:
                # Fetch OHLC data (1 hour intervals)
                ohlc, last = self.kraken.get_ohlc_data(pair, interval=60, since=since_unix)
                
                # Fetch recent trades
                trades, last = self.kraken.get_recent_trades(pair, since=since_unix)
                
                # Store data
                self.market_data[pair] = {
                    "ohlc": ohlc,
                    "trades": trades
                }
                
                self._log_info(f"Fetched data for {pair}: {len(ohlc)} OHLC records, {len(trades)} trades")
            
            return True
            
        except Exception as e:
            self._log_error(f"Error fetching market data: {str(e)}")
            return False
    
    def calculate_pair_metrics(self):
        """
        Calculate metrics for each trading pair
        
        Returns:
            bool: Success status
        """
        if not self.market_data:
            self._log_error("No market data available")
            return False
            
        try:
            # Reset pair metrics
            self.pair_metrics = {}
            
            for pair, data in self.market_data.items():
                ohlc = data["ohlc"]
                trades = data["trades"]
                
                if len(ohlc) < 24:
                    self._log_warning(f"Insufficient OHLC data for {pair}")
                    continue
                
                # Calculate volatility (standard deviation of returns)
                close_prices = ohlc['close'].values
                returns = np.diff(close_prices) / close_prices[:-1]
                volatility = np.std(returns) * 100  # Convert to percentage
                
                # Calculate trend (price change over period)
                start_price = close_prices[0]
                end_price = close_prices[-1]
                trend = ((end_price - start_price) / start_price) * 100  # Convert to percentage
                
                # Calculate volume
                volume = np.sum(ohlc['volume'].values)
                
                # Store metrics
                self.pair_metrics[pair] = {
                    "volatility": volatility,
                    "trend": trend,
                    "volume": volume,
                    "current_price": end_price
                }
                
                self._log_info(f"Calculated metrics for {pair}: volatility={volatility:.2f}%, trend={trend:.2f}%, volume={volume:.2f}")
            
            return True
            
        except Exception as e:
            self._log_error(f"Error calculating pair metrics: {str(e)}")
            return False
    
    def calculate_allocation(self):
        """
        Calculate optimal capital allocation between trading pairs
        
        Returns:
            bool: Success status
        """
        if not self.pair_metrics:
            self._log_error("No pair metrics available")
            return False
            
        try:
            # Extract metrics
            pairs = list(self.pair_metrics.keys())
            volatilities = np.array([self.pair_metrics[p]["volatility"] for p in pairs])
            trends = np.array([self.pair_metrics[p]["trend"] for p in pairs])
            volumes = np.array([self.pair_metrics[p]["volume"] for p in pairs])
            
            # Normalize metrics
            norm_volatilities = volatilities / np.max(volatilities) if np.max(volatilities) > 0 else volatilities
            norm_trends = (trends - np.min(trends)) / (np.max(trends) - np.min(trends)) if np.max(trends) > np.min(trends) else np.zeros_like(trends)
            norm_volumes = volumes / np.max(volumes) if np.max(volumes) > 0 else volumes
            
            # Calculate scores
            scores = (
                self.config["volatility_weight"] * norm_volatilities +
                self.config["trend_weight"] * norm_trends +
                self.config["volume_weight"] * norm_volumes
            )
            
            # Calculate raw allocations
            raw_allocations = scores / np.sum(scores) if np.sum(scores) > 0 else np.ones_like(scores) / len(scores)
            
            # Apply min/max constraints
            min_alloc = self.config["min_allocation_percentage"] / 100
            max_alloc = self.config["max_allocation_percentage"] / 100
            
            # Ensure all allocations are at least min_alloc
            allocations = np.maximum(raw_allocations, min_alloc)
            
            # Scale down if sum exceeds 1.0
            if np.sum(allocations) > 1.0:
                scale_factor = 1.0 / np.sum(allocations)
                allocations = allocations * scale_factor
            
            # Cap at max_alloc and redistribute excess
            while np.any(allocations > max_alloc):
                excess = np.sum(np.maximum(allocations - max_alloc, 0))
                allocations = np.minimum(allocations, max_alloc)
                
                # Redistribute excess to pairs below max_alloc
                below_max = allocations < max_alloc
                if np.any(below_max):
                    room = np.sum(max_alloc - allocations[below_max])
                    if room > 0:
                        ratio = excess / room
                        allocations[below_max] += (max_alloc - allocations[below_max]) * ratio
                else:
                    break
            
            # Convert to percentages
            allocation_percentages = allocations * 100
            
            # Store allocation recommendation
            self.allocation_recommendation = {
                "timestamp": datetime.now().isoformat(),
                "allocations": {
                    pair: {
                        "percentage": float(f"{pct:.2f}"),
                        "metrics": {
                            "volatility": float(f"{self.pair_metrics[pair]['volatility']:.2f}"),
                            "trend": float(f"{self.pair_metrics[pair]['trend']:.2f}"),
                            "volume": float(f"{self.pair_metrics[pair]['volume']:.2f}")
                        }
                    }
                    for pair, pct in zip(pairs, allocation_percentages)
                }
            }
            
            # Save recommendation
            try:
                with open(self.config["data_file"], 'w') as f:
                    json.dump(self.allocation_recommendation, f, indent=2)
            except Exception as e:
                self._log_error(f"Error saving allocation recommendation: {str(e)}")
            
            self._log_info(f"Calculated allocation recommendation: {self.allocation_recommendation}")
            return True
            
        except Exception as e:
            self._log_error(f"Error calculating allocation: {str(e)}")
            return False
    
    def generate_migration_plan(self, current_allocations=None):
        """
        Generate a migration plan from current allocations to recommended allocations
        
        Args:
            current_allocations (dict): Current allocation percentages by pair
            
        Returns:
            dict: Migration plan
        """
        if not self.allocation_recommendation:
            self._log_error("No allocation recommendation available")
            return None
            
        try:
            # Use current allocations if provided, otherwise assume equal distribution
            if current_allocations is None:
                pairs = list(self.allocation_recommendation["allocations"].keys())
                current_allocations = {pair: 100 / len(pairs) for pair in pairs}
            
            # Calculate changes needed
            migration_plan = {
                "timestamp": datetime.now().isoformat(),
                "current_allocations": current_allocations,
                "recommended_allocations": {
                    pair: data["percentage"]
                    for pair, data in self.allocation_recommendation["allocations"].items()
                },
                "changes": {}
            }
            
            # Calculate changes for each pair
            for pair, rec_pct in migration_plan["recommended_allocations"].items():
                curr_pct = current_allocations.get(pair, 0)
                change = rec_pct - curr_pct
                migration_plan["changes"][pair] = change
            
            # Generate action steps
            migration_plan["actions"] = []
            
            # Sort pairs by change (descending)
            sorted_pairs = sorted(
                migration_plan["changes"].keys(),
                key=lambda p: migration_plan["changes"][p],
                reverse=True
            )
            
            # Generate action steps
            for pair in sorted_pairs:
                change = migration_plan["changes"][pair]
                if change > 1:  # Only suggest changes greater than 1%
                    migration_plan["actions"].append({
                        "action": "increase",
                        "pair": pair,
                        "amount_percentage": float(f"{change:.2f}"),
                        "reason": self._get_reason_for_change(pair, change)
                    })
                elif change < -1:  # Only suggest changes greater than 1%
                    migration_plan["actions"].append({
                        "action": "decrease",
                        "pair": pair,
                        "amount_percentage": float(f"{-change:.2f}"),
                        "reason": self._get_reason_for_change(pair, change)
                    })
            
            self._log_info(f"Generated migration plan with {len(migration_plan['actions'])} actions")
            return migration_plan
            
        except Exception as e:
            self._log_error(f"Error generating migration plan: {str(e)}")
            return None
    
    def _get_reason_for_change(self, pair, change):
        """
        Generate a reason for allocation change
        
        Args:
            pair (str): Trading pair
            change (float): Percentage change
            
        Returns:
            str: Reason for change
        """
        metrics = self.allocation_recommendation["allocations"][pair]["metrics"]
        
        if change > 0:
            if metrics["trend"] > 5:
                return f"Strong upward trend ({metrics['trend']:.2f}%)"
            elif metrics["volatility"] > 5:
                return f"High volatility opportunity ({metrics['volatility']:.2f}%)"
            else:
                return f"Improved market conditions"
        else:
            if metrics["trend"] < -5:
                return f"Downward trend ({metrics['trend']:.2f}%)"
            elif metrics["volatility"] < 2:
                return f"Low volatility, reduced opportunity ({metrics['volatility']:.2f}%)"
            else:
                return f"Deteriorating market conditions"
    
    def run_analysis(self, current_allocations=None):
        """
        Run a complete analysis cycle
        
        Args:
            current_allocations (dict): Current allocation percentages by pair
            
        Returns:
            dict: Analysis results
        """
        if not self.config["enabled"]:
            self._log_info("Capital Migration Manager is disabled")
            return {"enabled": False}
            
        self._log_info("Starting capital migration analysis")
        
        # Check if it's time to run analysis
        current_time = datetime.now()
        if self.last_check_time:
            time_diff = (current_time - self.last_check_time).total_seconds() / 3600
            if time_diff < self.config["check_interval_hours"]:
                self._log_info(f"Skipping analysis, last check was {time_diff:.1f} hours ago")
                
                # Return last recommendation if available
                if self.allocation_recommendation:
                    return {
                        "skipped": True, 
                        "next_check_in_hours": self.config["check_interval_hours"] - time_diff,
                        "last_recommendation": self.allocation_recommendation
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
            
        # Calculate pair metrics
        if not self.calculate_pair_metrics():
            return {"error": "Failed to calculate pair metrics"}
            
        # Calculate allocation
        if not self.calculate_allocation():
            return {"error": "Failed to calculate allocation"}
            
        # Generate migration plan
        migration_plan = self.generate_migration_plan(current_allocations)
        
        self._log_info("Capital migration analysis completed")
        
        return {
            "timestamp": current_time.isoformat(),
            "allocation_recommendation": self.allocation_recommendation,
            "migration_plan": migration_plan,
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
        "trading_pairs": ["XRPGBP", "XRPEUR", "XRPUSD"],
        "check_interval_hours": 6,
        "volatility_weight": 0.3,
        "trend_weight": 0.4,
        "volume_weight": 0.3,
        "min_allocation_percentage": 10,
        "max_allocation_percentage": 70,
        "log_file": f"{data_dir}/capital_migration_log.txt",
        "data_file": f"{data_dir}/capital_migration_data.json"
    }
    
    # Save config
    with open(f"{data_dir}/capital_migration_config.json", 'w') as f:
        json.dump(config, f, indent=2)
        
    print("Capital Migration Manager module created.")
    print("To use this module with your XRP Trading Bot:")
    print("1. Place this file in the same directory as your main bot script")
    print("2. Import the module in your main script:")
    print("   from capital_migration_module import CapitalMigrationManager")
    print("3. Initialize the manager with your API keys:")
    print("   manager = CapitalMigrationManager(config_path='data/capital_migration_config.json', api_key=YOUR_API_KEY, api_secret=YOUR_API_SECRET)")
    print("4. Run the analysis periodically:")
    print("   results = manager.run_analysis(current_allocations={'XRPGBP': 50, 'XRPEUR': 30, 'XRPUSD': 20})")
    print("5. Use the allocation recommendations to adjust your capital distribution")
