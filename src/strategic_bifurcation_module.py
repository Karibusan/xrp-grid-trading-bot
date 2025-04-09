#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Strategic Bifurcation Module for XRP Trading Bot
Version: 3.0.0
Description: Module that identifies and responds to market bifurcation events
where price action diverges across different timeframes.
"""

import numpy as np
import pandas as pd
import time
import json
import os
import logging
from datetime import datetime, timedelta

class StrategicBifurcationAnalyzer:
    """
    A module that identifies and responds to market bifurcation events
    where price action diverges across different timeframes.
    """
    
    def __init__(self, config_path=None, api_client=None, notification_manager=None, error_handler=None):
        """
        Initialize the Strategic Bifurcation Analyzer module.
        
        Args:
            config_path (str): Path to configuration file
            api_client: API client instance for market data
            notification_manager: Notification manager instance
            error_handler: Error handler instance
        """
        self.logger = logging.getLogger('strategic_bifurcation_module')
        self.api_client = api_client
        self.notification_manager = notification_manager
        self.error_handler = error_handler
        
        # Default configuration
        self.default_config = {
            "enabled": True,
            "trading_pair": "XRPGBP",
            "timeframes": [5, 15, 60, 240, 1440],  # Minutes
            "check_interval_minutes": 60,
            "divergence_threshold": 0.15,
            "min_timeframe_pairs": 2,
            "data_file": "data/strategic_bifurcation_data.json"
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
            
        self.market_data = {}
        self.trend_directions = {}
        self.bifurcation_detected = False
        self.bifurcation_details = {}
        self.last_check_time = None
        
        self.logger.info("Strategic Bifurcation Analyzer initialized")
        if self.notification_manager:
            self.notification_manager.send_status_notification(
                "Strategic Bifurcation Module Initialized",
                f"Monitoring {len(self.config['timeframes'])} timeframes for divergence"
            )
    
    def _handle_error(self, message, error_type="module_error", severity="medium"):
        """Handle errors with proper logging and notification"""
        self.logger.error(message)
        
        if self.error_handler:
            self.error_handler.handle_error(error_type, message, severity, module="strategic_bifurcation")
        
        if self.notification_manager:
            self.notification_manager.send_error_notification(
                f"Strategic Bifurcation Module - {error_type}",
                message,
                severity
            )
    
    def fetch_market_data(self):
        """
        Fetch market data for multiple timeframes
        
        Returns:
            bool: Success status
        """
        if not self.api_client:
            self._handle_error("API client not initialized", "api_client_error", "high")
            return False
            
        try:
            # Reset market data
            self.market_data = {}
            
            # Fetch data for each timeframe
            for timeframe in self.config["timeframes"]:
                # Convert timeframe to interval parameter
                interval = self._convert_timeframe_to_interval(timeframe)
                
                # Calculate lookback period
                lookback_minutes = timeframe * 30  # 30 candles
                since = datetime.now() - timedelta(minutes=lookback_minutes)
                since_unix = since.timestamp()
                
                # Fetch OHLC data
                pair = self.config["trading_pair"]
                ohlc_data = self.api_client.get_ohlc_data(pair, interval=interval, since=since_unix)
                
                if ohlc_data is not None and len(ohlc_data) > 0:
                    self.market_data[timeframe] = ohlc_data
            
            self.logger.info(f"Fetched market data for {len(self.market_data)} timeframes")
            return len(self.market_data) > 0
            
        except Exception as e:
            self._handle_error(f"Error fetching market data: {str(e)}", "market_data_error", "high")
            return False
    
    def _convert_timeframe_to_interval(self, timeframe):
        """
        Convert timeframe in minutes to interval parameter for API
        
        Args:
            timeframe (int): Timeframe in minutes
            
        Returns:
            int: Interval parameter for API
        """
        # Map common timeframes to Kraken API intervals
        if timeframe == 1:
            return 1
        elif timeframe == 5:
            return 5
        elif timeframe == 15:
            return 15
        elif timeframe == 30:
            return 30
        elif timeframe == 60:
            return 60
        elif timeframe == 240:
            return 240
        elif timeframe == 1440:
            return 1440
        else:
            # Default to closest available interval
            available_intervals = [1, 5, 15, 30, 60, 240, 1440]
            return min(available_intervals, key=lambda x: abs(x - timeframe))
    
    def analyze_trends(self):
        """
        Analyze trends across different timeframes
        
        Returns:
            bool: Success status
        """
        if not self.market_data or len(self.market_data) < 2:
            self._handle_error("Insufficient market data for trend analysis", "insufficient_data")
            return False
            
        try:
            # Reset trend directions
            self.trend_directions = {}
            
            # Analyze trend for each timeframe
            for timeframe, data in self.market_data.items():
                # Calculate trend direction using linear regression
                trend = self._calculate_trend(data)
                self.trend_directions[timeframe] = trend
            
            self.logger.info(f"Analyzed trends for {len(self.trend_directions)} timeframes")
            return True
            
        except Exception as e:
            self._handle_error(f"Error analyzing trends: {str(e)}", "trend_analysis_error")
            return False
    
    def _calculate_trend(self, data):
        """
        Calculate trend direction using linear regression
        
        Args:
            data: OHLC data
            
        Returns:
            float: Trend direction (positive for uptrend, negative for downtrend)
        """
        # Extract close prices
        close_prices = data['close'].values
        
        # Create x values (0, 1, 2, ...)
        x = np.arange(len(close_prices))
        
        # Calculate linear regression
        slope, _ = np.polyfit(x, close_prices, 1)
        
        # Normalize slope by average price
        avg_price = np.mean(close_prices)
        normalized_slope = slope / avg_price if avg_price > 0 else 0
        
        return normalized_slope
    
    def detect_bifurcation(self):
        """
        Detect bifurcation across timeframes
        
        Returns:
            bool: Success status
        """
        if not self.trend_directions or len(self.trend_directions) < 2:
            self._handle_error("Insufficient trend data for bifurcation detection", "insufficient_data")
            return False
            
        try:
            # Reset bifurcation detection
            self.bifurcation_detected = False
            self.bifurcation_details = {}
            
            # Check for divergence between timeframes
            timeframes = sorted(self.trend_directions.keys())
            divergent_pairs = []
            
            for i in range(len(timeframes)):
                for j in range(i+1, len(timeframes)):
                    tf1 = timeframes[i]
                    tf2 = timeframes[j]
                    
                    trend1 = self.trend_directions[tf1]
                    trend2 = self.trend_directions[tf2]
                    
                    # Check if trends are in opposite directions
                    if (trend1 > 0 and trend2 < 0) or (trend1 < 0 and trend2 > 0):
                        # Check if divergence exceeds threshold
                        divergence = abs(trend1 - trend2)
                        if divergence >= self.config["divergence_threshold"]:
                            divergent_pairs.append({
                                "timeframe1": tf1,
                                "timeframe2": tf2,
                                "trend1": trend1,
                                "trend2": trend2,
                                "divergence": divergence
                            })
            
            # Detect bifurcation if enough divergent pairs
            if len(divergent_pairs) >= self.config["min_timeframe_pairs"]:
                self.bifurcation_detected = True
                self.bifurcation_details = {
                    "divergent_pairs": divergent_pairs,
                    "total_pairs": len(divergent_pairs),
                    "threshold": self.config["divergence_threshold"]
                }
                
                # Save bifurcation data
                self._save_bifurcation_data()
                
                # Send notification
                if self.notification_manager:
                    self._send_bifurcation_notification()
            
            self.logger.info(f"Bifurcation detection completed. Detected: {self.bifurcation_detected}, Divergent pairs: {len(divergent_pairs)}")
            return True
            
        except Exception as e:
            self._handle_error(f"Error detecting bifurcation: {str(e)}", "bifurcation_detection_error")
            return False
    
    def _save_bifurcation_data(self):
        """
        Save bifurcation data to file
        """
        try:
            data = {
                "timestamp": datetime.now().isoformat(),
                "trend_directions": self.trend_directions,
                "bifurcation_detected": self.bifurcation_detected,
                "bifurcation_details": self.bifurcation_details
            }
            
            with open(self.config["data_file"], 'w') as f:
                json.dump(data, f, indent=4)
                
            self.logger.info(f"Bifurcation data saved to {self.config['data_file']}")
            
        except Exception as e:
            self._handle_error(f"Error saving bifurcation data: {str(e)}", "data_save_error")
    
    def _send_bifurcation_notification(self):
        """
        Send notification about detected bifurcation
        """
        if not self.notification_manager or not self.bifurcation_details:
            return
            
        # Prepare notification details
        details = []
        for pair in self.bifurcation_details.get("divergent_pairs", []):
            tf1 = pair["timeframe1"]
            tf2 = pair["timeframe2"]
            trend1 = pair["trend1"]
            trend2 = pair["trend2"]
            divergence = pair["divergence"]
            
            details.append(f"{tf1}m vs {tf2}m: {trend1:.4f} vs {trend2:.4f} (div: {divergence:.4f})")
        
        # Send notification
        self.notification_manager.send_efficiency_notification({
            "strategic_bifurcation": True,
            "details": "\n".join(details),
            "divergent_pairs": len(self.bifurcation_details.get("divergent_pairs", [])),
            "threshold": self.config["divergence_threshold"],
            "timestamp": datetime.now().isoformat()
        })
    
    def check_bifurcation(self):
        """
        Check for strategic bifurcation
        
        Returns:
            bool: True if bifurcation detected, False otherwise
        """
        # Check if it's time to run the check
        current_time = datetime.now()
        if self.last_check_time:
            elapsed_minutes = (current_time - self.last_check_time).total_seconds() / 60
            if elapsed_minutes < self.config["check_interval_minutes"]:
                return self.bifurcation_detected
        
        # Update last check time
        self.last_check_time = current_time
        
        # Skip if module is disabled
        if not self.config["enabled"]:
            return False
        
        # Fetch market data
        if not self.fetch_market_data():
            return False
        
        # Analyze trends
        if not self.analyze_trends():
            return False
        
        # Detect bifurcation
        if not self.detect_bifurcation():
            return False
        
        return self.bifurcation_detected
    
    def get_bifurcation_details(self):
        """
        Get details of detected bifurcation
        
        Returns:
            dict: Bifurcation details
        """
        return self.bifurcation_details
    
    def is_bifurcation_detected(self):
        """
        Check if bifurcation is detected
        
        Returns:
            bool: True if bifurcation detected, False otherwise
        """
        return self.bifurcation_detected
