#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Capital Migration Module for XRP Trading Bot
Version: 3.0.0
Description: Module that detects and responds to significant capital movements
between different exchanges and trading pairs.
"""

import numpy as np
import pandas as pd
import time
import json
import os
import logging
from datetime import datetime, timedelta
import requests

class CapitalMigrationAnalyzer:
    """
    A module that detects and responds to significant capital movements
    between different exchanges and trading pairs.
    """
    
    def __init__(self, config_path=None, api_client=None, notification_manager=None, error_handler=None):
        """
        Initialize the Capital Migration Analyzer module.
        
        Args:
            config_path (str): Path to configuration file
            api_client: API client instance for market data
            notification_manager: Notification manager instance
            error_handler: Error handler instance
        """
        self.logger = logging.getLogger('capital_migration_module')
        self.api_client = api_client
        self.notification_manager = notification_manager
        self.error_handler = error_handler
        
        # Default configuration
        self.default_config = {
            "enabled": True,
            "primary_pair": "XRPGBP",
            "secondary_pairs": ["XRPUSD", "XRPEUR", "XRPBTC"],
            "exchanges": ["kraken", "binance", "bitstamp"],
            "check_interval_minutes": 120,
            "volume_change_threshold": 0.25,
            "price_impact_threshold": 0.05,
            "data_file": "data/capital_migration_data.json"
        }
        
        # Load configuration
        self.config = self.default_config.copy()
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                    self.config.update(user_config)
            except Exception as e:
                self._handle_error(f"Error loading configuration: {str(e)}", "configuration_error")
        
        # Initialize data storage
        self.data_dir = os.path.dirname(self.config["data_file"])
        if self.data_dir and not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir, exist_ok=True)
            
        self.volume_data = {}
        self.price_data = {}
        self.migration_detected = False
        self.migration_details = {}
        self.last_check_time = None
        
        self.logger.info("Capital Migration Analyzer initialized")
        if self.notification_manager:
            self.notification_manager.send_status_notification(
                "Capital Migration Module Initialized",
                f"Monitoring {len(self.config['secondary_pairs'])} pairs across {len(self.config['exchanges'])} exchanges"
            )
    
    def _handle_error(self, message, error_type="module_error", severity="medium"):
        """Handle errors with proper logging and notification"""
        self.logger.error(message)
        
        if self.error_handler:
            self.error_handler.handle_error(error_type, message, severity, module="capital_migration")
        
        if self.notification_manager:
            self.notification_manager.send_error_notification(
                f"Capital Migration Module - {error_type}",
                message,
                severity
            )
    
    def fetch_market_data(self):
        """
        Fetch market data from multiple exchanges
        
        Returns:
            bool: Success status
        """
        if not self.api_client:
            self._handle_error("API client not initialized", "api_client_error", "high")
            return False
            
        try:
            # Reset data
            self.volume_data = {}
            self.price_data = {}
            
            # Fetch data for primary pair on primary exchange (Kraken)
            primary_data = self.api_client.get_recent_trades(self.config["primary_pair"])
            if primary_data is not None:
                self.volume_data["kraken"] = {self.config["primary_pair"]: self._calculate_volume(primary_data)}
                self.price_data["kraken"] = {self.config["primary_pair"]: self._calculate_average_price(primary_data)}
            
            # Fetch data for secondary pairs and exchanges
            for exchange in self.config["exchanges"]:
                if exchange not in self.volume_data:
                    self.volume_data[exchange] = {}
                    self.price_data[exchange] = {}
                
                # Skip primary pair on Kraken (already fetched)
                if exchange == "kraken" and self.config["primary_pair"] in self.volume_data["kraken"]:
                    continue
                
                # Fetch data for all pairs on this exchange
                pairs_to_fetch = [self.config["primary_pair"]] + self.config["secondary_pairs"]
                for pair in pairs_to_fetch:
                    try:
                        # Use external API for other exchanges
                        if exchange != "kraken":
                            data = self._fetch_external_exchange_data(exchange, pair)
                        else:
                            data = self.api_client.get_recent_trades(pair)
                        
                        if data is not None:
                            self.volume_data[exchange][pair] = self._calculate_volume(data)
                            self.price_data[exchange][pair] = self._calculate_average_price(data)
                    except Exception as e:
                        self.logger.warning(f"Error fetching data for {pair} on {exchange}: {str(e)}")
            
            self.logger.info(f"Fetched market data from {len(self.volume_data)} exchanges")
            return True
            
        except Exception as e:
            self._handle_error(f"Error fetching market data: {str(e)}", "market_data_error", "high")
            return False
    
    def _fetch_external_exchange_data(self, exchange, pair):
        """
        Fetch data from external exchanges using public APIs
        
        Args:
            exchange (str): Exchange name
            pair (str): Trading pair
            
        Returns:
            pandas.DataFrame: Trade data
        """
        # This is a simplified implementation
        # In a real-world scenario, you would use the appropriate API for each exchange
        
        # For demonstration purposes, we'll return None
        # This would be replaced with actual API calls in production
        return None
    
    def _calculate_volume(self, trade_data):
        """
        Calculate trading volume from trade data
        
        Args:
            trade_data: Trade data
            
        Returns:
            float: Trading volume
        """
        if trade_data is None or len(trade_data) == 0:
            return 0.0
            
        # Sum up the volume column
        return trade_data['volume'].sum()
    
    def _calculate_average_price(self, trade_data):
        """
        Calculate volume-weighted average price from trade data
        
        Args:
            trade_data: Trade data
            
        Returns:
            float: Average price
        """
        if trade_data is None or len(trade_data) == 0:
            return 0.0
            
        # Calculate volume-weighted average price
        return (trade_data['price'] * trade_data['volume']).sum() / trade_data['volume'].sum()
    
    def analyze_capital_migration(self):
        """
        Analyze capital migration between exchanges and pairs
        
        Returns:
            bool: Success status
        """
        if not self.volume_data or not self.price_data:
            self._handle_error("No market data available for analysis", "insufficient_data")
            return False
            
        try:
            # Load previous data for comparison
            previous_data = self._load_previous_data()
            
            # Reset migration detection
            self.migration_detected = False
            self.migration_details = {}
            
            # Skip if no previous data available
            if not previous_data:
                self._save_current_data()
                return False
            
            # Compare volumes across exchanges and pairs
            for exchange in self.volume_data:
                for pair in self.volume_data[exchange]:
                    current_volume = self.volume_data[exchange][pair]
                    
                    # Skip if no volume data
                    if current_volume == 0:
                        continue
                    
                    # Check if this exchange/pair was in previous data
                    if exchange in previous_data.get("volume_data", {}) and pair in previous_data["volume_data"][exchange]:
                        previous_volume = previous_data["volume_data"][exchange][pair]
                        
                        # Skip if previous volume was zero
                        if previous_volume == 0:
                            continue
                        
                        # Calculate volume change
                        volume_change = (current_volume - previous_volume) / previous_volume
                        
                        # Check if volume change exceeds threshold
                        if abs(volume_change) >= self.config["volume_change_threshold"]:
                            # Check price impact
                            current_price = self.price_data[exchange][pair]
                            previous_price = previous_data["price_data"][exchange][pair]
                            
                            if previous_price > 0:
                                price_change = (current_price - previous_price) / previous_price
                                
                                # Record migration if price change is significant
                                if abs(price_change) >= self.config["price_impact_threshold"]:
                                    self.migration_detected = True
                                    
                                    # Record details
                                    if exchange not in self.migration_details:
                                        self.migration_details[exchange] = {}
                                    
                                    self.migration_details[exchange][pair] = {
                                        "volume_change": volume_change,
                                        "price_change": price_change,
                                        "current_volume": current_volume,
                                        "previous_volume": previous_volume,
                                        "current_price": current_price,
                                        "previous_price": previous_price
                                    }
            
            # Save current data for future comparison
            self._save_current_data()
            
            # Send notification if migration detected
            if self.migration_detected and self.notification_manager:
                self._send_migration_notification()
            
            self.logger.info(f"Capital migration analysis completed. Migration detected: {self.migration_detected}")
            return True
            
        except Exception as e:
            self._handle_error(f"Error analyzing capital migration: {str(e)}", "analysis_error")
            return False
    
    def _load_previous_data(self):
        """
        Load previous data from file
        
        Returns:
            dict: Previous data
        """
        try:
            if os.path.exists(self.config["data_file"]):
                with open(self.config["data_file"], 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            self.logger.warning(f"Error loading previous data: {str(e)}")
            return None
    
    def _save_current_data(self):
        """
        Save current data to file
        """
        try:
            data = {
                "timestamp": datetime.now().isoformat(),
                "volume_data": self.volume_data,
                "price_data": self.price_data,
                "migration_detected": self.migration_detected,
                "migration_details": self.migration_details
            }
            
            with open(self.config["data_file"], 'w') as f:
                json.dump(data, f, indent=4)
                
            self.logger.info(f"Data saved to {self.config['data_file']}")
            
        except Exception as e:
            self._handle_error(f"Error saving data: {str(e)}", "data_save_error")
    
    def _send_migration_notification(self):
        """
        Send notification about detected capital migration
        """
        if not self.notification_manager:
            return
            
        # Prepare notification details
        details = []
        for exchange in self.migration_details:
            for pair in self.migration_details[exchange]:
                migration = self.migration_details[exchange][pair]
                details.append(f"{exchange.upper()} {pair}: Volume {migration['volume_change']*100:.1f}%, Price {migration['price_change']*100:.1f}%")
        
        # Send notification
        self.notification_manager.send_efficiency_notification({
            "capital_migration": True,
            "details": "\n".join(details),
            "exchanges_affected": len(self.migration_details),
            "pairs_affected": sum(len(pairs) for pairs in self.migration_details.values()),
            "timestamp": datetime.now().isoformat()
        })
    
    def check_capital_migration(self):
        """
        Check for capital migration
        
        Returns:
            bool: True if capital migration detected, False otherwise
        """
        # Check if it's time to run the check
        current_time = datetime.now()
        if self.last_check_time:
            elapsed_minutes = (current_time - self.last_check_time).total_seconds() / 60
            if elapsed_minutes < self.config["check_interval_minutes"]:
                return self.migration_detected
        
        # Update last check time
        self.last_check_time = current_time
        
        # Skip if module is disabled
        if not self.config["enabled"]:
            return False
        
        # Fetch market data
        if not self.fetch_market_data():
            return False
        
        # Analyze capital migration
        if not self.analyze_capital_migration():
            return False
        
        return self.migration_detected
    
    def get_migration_details(self):
        """
        Get details of detected capital migration
        
        Returns:
            dict: Migration details
        """
        return self.migration_details
    
    def is_migration_detected(self):
        """
        Check if capital migration is detected
        
        Returns:
            bool: True if migration detected, False otherwise
        """
        return self.migration_detected
