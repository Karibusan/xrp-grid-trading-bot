#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Signal Collapse Module for XRP Trading Bot
Version: 3.0.0
Description: Lightweight module that detects when multiple technical indicators
converge to give the same signals, reducing signal diversity.
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

class SignalCollapseDetector:
    """
    A module that detects when multiple technical indicators converge
    to give the same signals, reducing signal diversity.
    """
    
    def __init__(self, config_path=None, api_client=None, notification_manager=None, error_handler=None):
        """
        Initialize the Signal Collapse Detector module.
        
        Args:
            config_path (str): Path to configuration file
            api_client: API client instance for market data
            notification_manager: Notification manager instance
            error_handler: Error handler instance
        """
        self.logger = logging.getLogger('signal_collapse_module')
        self.api_client = api_client
        self.notification_manager = notification_manager
        self.error_handler = error_handler
        
        # Default configuration
        self.default_config = {
            "enabled": True,
            "trading_pair": "XRPGBP",
            "check_interval_minutes": 60,
            "correlation_threshold": 0.8,
            "indicators": ["rsi", "macd", "bollinger", "moving_averages"],
            "lookback_periods": 24,
            "data_file": "data/signal_collapse_data.json"
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
            
        self.market_data = None
        self.indicator_signals = {}
        self.correlation_matrix = None
        self.signal_collapse_detected = False
        self.last_check_time = None
        
        self.logger.info("Signal Collapse Detector initialized")
        if self.notification_manager:
            self.notification_manager.send_status_notification(
                "Signal Collapse Module Initialized",
                f"Configuration loaded with correlation threshold: {self.config['correlation_threshold']}"
            )
    
    def _handle_error(self, message, error_type="module_error", severity="medium"):
        """Handle errors with proper logging and notification"""
        self.logger.error(message)
        
        if self.error_handler:
            self.error_handler.handle_error(error_type, message, severity, module="signal_collapse")
        
        if self.notification_manager:
            self.notification_manager.send_error_notification(
                f"Signal Collapse Module - {error_type}",
                message,
                severity
            )
    
    def fetch_market_data(self):
        """
        Fetch market data from API client
        
        Returns:
            bool: Success status
        """
        if not self.api_client:
            self._handle_error("API client not initialized", "api_client_error", "high")
            return False
            
        try:
            # Calculate time period to fetch
            lookback_minutes = self.config["lookback_periods"] * 60
            since = datetime.now() - timedelta(minutes=lookback_minutes)
            since_unix = since.timestamp()
            
            # Fetch OHLC data (15 minute intervals)
            pair = self.config["trading_pair"]
            
            # Use the API client to fetch data
            ohlc_data = self.api_client.get_ohlc_data(pair, interval=15, since=since_unix)
            
            # Store data
            self.market_data = ohlc_data
            self.logger.info(f"Fetched {len(ohlc_data)} OHLC records")
            return True
            
        except Exception as e:
            self._handle_error(f"Error fetching market data: {str(e)}", "market_data_error", "high")
            return False
    
    def calculate_indicators(self):
        """
        Calculate technical indicators based on market data
        
        Returns:
            bool: Success status
        """
        if self.market_data is None or len(self.market_data) < 30:
            self._handle_error("Insufficient market data for indicator calculation", "insufficient_data", "medium")
            return False
            
        try:
            # Reset indicator signals
            self.indicator_signals = {}
            
            # Calculate RSI if enabled
            if "rsi" in self.config["indicators"]:
                self.indicator_signals["rsi"] = self._calculate_rsi_signals()
                
            # Calculate MACD if enabled
            if "macd" in self.config["indicators"]:
                self.indicator_signals["macd"] = self._calculate_macd_signals()
                
            # Calculate Bollinger Bands if enabled
            if "bollinger" in self.config["indicators"]:
                self.indicator_signals["bollinger"] = self._calculate_bollinger_signals()
                
            # Calculate Moving Averages if enabled
            if "moving_averages" in self.config["indicators"]:
                self.indicator_signals["moving_averages"] = self._calculate_ma_signals()
            
            self.logger.info(f"Calculated {len(self.indicator_signals)} indicators")
            return True
            
        except Exception as e:
            self._handle_error(f"Error calculating indicators: {str(e)}", "indicator_calculation_error")
            return False
    
    def _calculate_rsi_signals(self, periods=14):
        """
        Calculate RSI indicator signals
        
        Returns:
            list: Binary signals (1 for buy, -1 for sell, 0 for neutral)
        """
        close_prices = self.market_data['close'].values
        signals = np.zeros(len(close_prices))
        
        # Calculate RSI
        deltas = np.diff(close_prices)
        seed = deltas[:periods+1]
        up = seed[seed >= 0].sum()/periods
        down = -seed[seed < 0].sum()/periods
        rs = up/down if down != 0 else float('inf')
        rsi = np.zeros_like(close_prices)
        rsi[:periods] = 100. - 100./(1. + rs)
        
        for i in range(periods, len(close_prices)):
            delta = deltas[i-1]
            if delta > 0:
                upval = delta
                downval = 0.
            else:
                upval = 0.
                downval = -delta
                
            up = (up * (periods - 1) + upval) / periods
            down = (down * (periods - 1) + downval) / periods
            rs = up/down if down != 0 else float('inf')
            rsi[i] = 100. - 100./(1. + rs)
            
            # Generate signals
            if rsi[i] < 30:
                signals[i] = 1  # Buy signal
            elif rsi[i] > 70:
                signals[i] = -1  # Sell signal
            else:
                signals[i] = 0  # Neutral
        
        return signals
    
    def _calculate_macd_signals(self, fast=12, slow=26, signal=9):
        """
        Calculate MACD indicator signals
        
        Returns:
            list: Binary signals (1 for buy, -1 for sell, 0 for neutral)
        """
        close_prices = self.market_data['close'].values
        signals = np.zeros(len(close_prices))
        
        # Calculate MACD
        exp1 = pd.Series(close_prices).ewm(span=fast, adjust=False).mean()
        exp2 = pd.Series(close_prices).ewm(span=slow, adjust=False).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        
        # Generate signals
        for i in range(slow + signal, len(close_prices)):
            if macd[i] > signal_line[i] and macd[i-1] <= signal_line[i-1]:
                signals[i] = 1  # Buy signal (MACD crosses above signal line)
            elif macd[i] < signal_line[i] and macd[i-1] >= signal_line[i-1]:
                signals[i] = -1  # Sell signal (MACD crosses below signal line)
            else:
                signals[i] = 0  # Neutral
        
        return signals
    
    def _calculate_bollinger_signals(self, window=20, num_std=2):
        """
        Calculate Bollinger Bands indicator signals
        
        Returns:
            list: Binary signals (1 for buy, -1 for sell, 0 for neutral)
        """
        close_prices = self.market_data['close'].values
        signals = np.zeros(len(close_prices))
        
        # Calculate Bollinger Bands
        sma = pd.Series(close_prices).rolling(window=window).mean()
        std = pd.Series(close_prices).rolling(window=window).std()
        upper_band = sma + (std * num_std)
        lower_band = sma - (std * num_std)
        
        # Generate signals
        for i in range(window, len(close_prices)):
            if close_prices[i] < lower_band[i]:
                signals[i] = 1  # Buy signal (price below lower band)
            elif close_prices[i] > upper_band[i]:
                signals[i] = -1  # Sell signal (price above upper band)
            else:
                signals[i] = 0  # Neutral
        
        return signals
    
    def _calculate_ma_signals(self, short_window=10, long_window=50):
        """
        Calculate Moving Average crossover signals
        
        Returns:
            list: Binary signals (1 for buy, -1 for sell, 0 for neutral)
        """
        close_prices = self.market_data['close'].values
        signals = np.zeros(len(close_prices))
        
        # Calculate moving averages
        short_ma = pd.Series(close_prices).rolling(window=short_window).mean()
        long_ma = pd.Series(close_prices).rolling(window=long_window).mean()
        
        # Generate signals
        for i in range(long_window, len(close_prices)):
            if short_ma[i] > long_ma[i] and short_ma[i-1] <= long_ma[i-1]:
                signals[i] = 1  # Buy signal (short MA crosses above long MA)
            elif short_ma[i] < long_ma[i] and short_ma[i-1] >= long_ma[i-1]:
                signals[i] = -1  # Sell signal (short MA crosses below long MA)
            else:
                signals[i] = 0  # Neutral
        
        return signals
    
    def calculate_correlation(self):
        """
        Calculate correlation between indicator signals
        
        Returns:
            bool: Success status
        """
        if not self.indicator_signals or len(self.indicator_signals) < 2:
            self._handle_error("Insufficient indicator signals for correlation calculation", "insufficient_data")
            return False
            
        try:
            # Create a DataFrame from indicator signals
            signals_df = pd.DataFrame(self.indicator_signals)
            
            # Calculate correlation matrix
            self.correlation_matrix = signals_df.corr().abs()
            
            # Check for signal collapse
            high_correlation_count = 0
            total_pairs = 0
            
            # Count highly correlated pairs
            for i in range(len(self.correlation_matrix.columns)):
                for j in range(i+1, len(self.correlation_matrix.columns)):
                    total_pairs += 1
                    if self.correlation_matrix.iloc[i, j] >= self.config["correlation_threshold"]:
                        high_correlation_count += 1
            
            # Calculate percentage of highly correlated pairs
            if total_pairs > 0:
                correlation_percentage = high_correlation_count / total_pairs
                
                # Detect signal collapse
                self.signal_collapse_detected = correlation_percentage >= 0.5
                
                self.logger.info(f"Correlation calculation: {high_correlation_count}/{total_pairs} pairs highly correlated")
                
                # Save correlation data
                self._save_correlation_data(correlation_percentage)
                
                # Send notification if signal collapse detected
                if self.signal_collapse_detected and self.notification_manager:
                    self.notification_manager.send_efficiency_notification({
                        "signal_collapse": True,
                        "correlation_percentage": f"{correlation_percentage:.2%}",
                        "high_correlation_pairs": high_correlation_count,
                        "total_pairs": total_pairs,
                        "threshold": self.config["correlation_threshold"]
                    })
                
                return True
            else:
                self._handle_error("No indicator pairs available for correlation calculation", "insufficient_data")
                return False
                
        except Exception as e:
            self._handle_error(f"Error calculating correlation: {str(e)}", "correlation_calculation_error")
            return False
    
    def _save_correlation_data(self, correlation_percentage):
        """
        Save correlation data to file
        
        Args:
            correlation_percentage (float): Percentage of highly correlated pairs
        """
        try:
            data = {
                "timestamp": datetime.now().isoformat(),
                "correlation_percentage": correlation_percentage,
                "signal_collapse_detected": self.signal_collapse_detected,
                "correlation_threshold": self.config["correlation_threshold"],
                "correlation_matrix": self.correlation_matrix.to_dict() if self.correlation_matrix is not None else None
            }
            
            with open(self.config["data_file"], 'w') as f:
                json.dump(data, f, indent=4)
                
            self.logger.info(f"Correlation data saved to {self.config['data_file']}")
            
        except Exception as e:
            self._handle_error(f"Error saving correlation data: {str(e)}", "data_save_error")
    
    def check_signal_collapse(self):
        """
        Check for signal collapse
        
        Returns:
            bool: True if signal collapse detected, False otherwise
        """
        # Check if it's time to run the check
        current_time = datetime.now()
        if self.last_check_time:
            elapsed_minutes = (current_time - self.last_check_time).total_seconds() / 60
            if elapsed_minutes < self.config["check_interval_minutes"]:
                return self.signal_collapse_detected
        
        # Update last check time
        self.last_check_time = current_time
        
        # Skip if module is disabled
        if not self.config["enabled"]:
            return False
        
        # Fetch market data
        if not self.fetch_market_data():
            return False
        
        # Calculate indicators
        if not self.calculate_indicators():
            return False
        
        # Calculate correlation
        if not self.calculate_correlation():
            return False
        
        return self.signal_collapse_detected
    
    def get_correlation_matrix(self):
        """
        Get the correlation matrix
        
        Returns:
            pandas.DataFrame: Correlation matrix
        """
        return self.correlation_matrix
    
    def get_indicator_signals(self):
        """
        Get the indicator signals
        
        Returns:
            dict: Indicator signals
        """
        return self.indicator_signals
    
    def is_signal_collapse_detected(self):
        """
        Check if signal collapse is detected
        
        Returns:
            bool: True if signal collapse detected, False otherwise
        """
        return self.signal_collapse_detected
