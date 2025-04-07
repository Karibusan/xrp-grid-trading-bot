#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Signal Collapse Module for XRP Trading Bot
Version: 1.0.0
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
    
    def __init__(self, config_path=None, api_key=None, api_secret=None):
        """
        Initialize the Signal Collapse Detector module.
        
        Args:
            config_path (str): Path to configuration file
            api_key (str): Kraken API key
            api_secret (str): Kraken API secret
        """
        # Default configuration
        self.default_config = {
            "enabled": True,
            "trading_pair": "XRPGBP",
            "check_interval_minutes": 60,
            "correlation_threshold": 0.8,
            "indicators": ["rsi", "macd", "bollinger", "moving_averages"],
            "lookback_periods": 24,
            "log_file": "signal_collapse_log.txt",
            "data_file": "signal_collapse_data.json"
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
        self.indicator_signals = {}
        self.correlation_matrix = None
        self.signal_collapse_detected = False
        self.last_check_time = None
        
        self._log_info("Signal Collapse Detector initialized")
    
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
            lookback_minutes = self.config["lookback_periods"] * 60
            since = datetime.now() - timedelta(minutes=lookback_minutes)
            since_unix = since.timestamp()
            
            # Fetch OHLC data (15 minute intervals)
            pair = self.config["trading_pair"]
            ohlc, last = self.kraken.get_ohlc_data(pair, interval=15, since=since_unix)
            
            # Store data
            self.market_data = ohlc
            self._log_info(f"Fetched {len(ohlc)} OHLC records")
            return True
            
        except Exception as e:
            self._log_error(f"Error fetching market data: {str(e)}")
            return False
    
    def calculate_indicators(self):
        """
        Calculate technical indicators based on market data
        
        Returns:
            bool: Success status
        """
        if self.market_data is None or len(self.market_data) < 30:
            self._log_error("Insufficient market data for indicator calculation")
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
            
            self._log_info(f"Calculated {len(self.indicator_signals)} indicators")
            return True
            
        except Exception as e:
            self._log_error(f"Error calculating indicators: {str(e)}")
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
        
        # Calculate Moving Averages
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
        if not self.indicator_signals:
            self._log_error("No indicator signals available")
            return False
            
        try:
            # Prepare signals for correlation calculation
            signals_df = pd.DataFrame()
            
            for indicator, signals in self.indicator_signals.items():
                signals_df[indicator] = signals
            
            # Drop rows with NaN values
            signals_df = signals_df.dropna()
            
            if len(signals_df) < 10:
                self._log_warning("Insufficient data for correlation calculation")
                return False
            
            # Calculate correlation matrix
            self.correlation_matrix = signals_df.corr().abs()
            
            self._log_info(f"Calculated correlation matrix: {self.correlation_matrix.to_dict()}")
            return True
            
        except Exception as e:
            self._log_error(f"Error calculating correlation: {str(e)}")
            return False
    
    def detect_signal_collapse(self):
        """
        Detect signal collapse based on correlation matrix
        
        Returns:
            bool: Signal collapse detected
        """
        if self.correlation_matrix is None:
            self._log_error("No correlation matrix available")
            return False
            
        try:
            # Calculate average correlation
            corr_values = []
            for i in range(len(self.correlation_matrix.columns)):
                for j in range(i+1, len(self.correlation_matrix.columns)):
                    col_i = self.correlation_matrix.columns[i]
                    col_j = self.correlation_matrix.columns[j]
                    corr_values.append(self.correlation_matrix.loc[col_i, col_j])
            
            avg_correlation = np.mean(corr_values) if corr_values else 0
            
            # Detect signal collapse
            threshold = self.config["correlation_threshold"]
            self.signal_collapse_detected = avg_correlation >= threshold
            
            if self.signal_collapse_detected:
                self._log_warning(f"Signal collapse detected: average correlation = {avg_correlation:.2f}")
            else:
                self._log_info(f"No signal collapse detected: average correlation = {avg_correlation:.2f}")
            
            # Save detection result
            try:
                with open(self.config["data_file"], 'w') as f:
                    json.dump({
                        "timestamp": datetime.now().isoformat(),
                        "average_correlation": avg_correlation,
                        "threshold": threshold,
                        "signal_collapse_detected": self.signal_collapse_detected,
                        "correlation_matrix": self.correlation_matrix.to_dict()
                    }, f, indent=2)
            except Exception as e:
                self._log_error(f"Error saving detection result: {str(e)}")
            
            return self.signal_collapse_detected
            
        except Exception as e:
            self._log_error(f"Error detecting signal collapse: {str(e)}")
            return False
    
    def generate_recommendation(self):
        """
        Generate trading recommendation based on signal collapse detection
        
        Returns:
            dict: Recommendation
        """
        if self.signal_collapse_detected:
            recommendation = {
                "timestamp": datetime.now().isoformat(),
                "signal_collapse_detected": True,
                "risk_level": "high",
                "actions": [
                    "Reduce position sizes by 50%",
                    "Widen stop-loss levels",
                    "Increase grid spacing",
                    "Disable automatic reinvestment",
                    "Wait for signal diversity to return"
                ],
                "explanation": "Multiple indicators are giving highly correlated signals, which reduces the reliability of your trading strategy. This often occurs during market regime changes or before significant price movements."
            }
        else:
            recommendation = {
                "timestamp": datetime.now().isoformat(),
                "signal_collapse_detected": False,
                "risk_level": "normal",
                "actions": [
                    "Maintain normal position sizes",
                    "Use standard grid spacing",
                    "Continue with current strategy"
                ],
                "explanation": "Indicators are showing healthy diversity in signals, suggesting normal market conditions."
            }
        
        self._log_info(f"Generated recommendation: {recommendation['risk_level']} risk level")
        return recommendation
    
    def run_analysis(self):
        """
        Run a complete analysis cycle
        
        Returns:
            dict: Analysis results
        """
        if not self.config["enabled"]:
            self._log_info("Signal Collapse Detector is disabled")
            return {"enabled": False}
            
        self._log_info("Starting signal collapse analysis")
        
        # Check if it's time to run analysis
        current_time = datetime.now()
        if self.last_check_time:
            time_diff = (current_time - self.last_check_time).total_seconds() / 60
            if time_diff < self.config["check_interval_minutes"]:
                self._log_info(f"Skipping analysis, last check was {time_diff:.1f} minutes ago")
                return {
                    "skipped": True, 
                    "next_check_in_minutes": self.config["check_interval_minutes"] - time_diff,
                    "signal_collapse_detected": self.signal_collapse_detected
                }
        
        # Update last check time
        self.last_check_time = current_time
        
        # Fetch market data
        if not self.fetch_market_data():
            return {"error": "Failed to fetch market data"}
            
        # Calculate indicators
        if not self.calculate_indicators():
            return {"error": "Failed to calculate indicators"}
            
        # Calculate correlation
        if not self.calculate_correlation():
            return {"error": "Failed to calculate correlation"}
            
        # Detect signal collapse
        self.detect_signal_collapse()
        
        # Generate recommendation
        recommendation = self.generate_recommendation()
        
        self._log_info("Signal collapse analysis completed")
        
        return {
            "timestamp": current_time.isoformat(),
            "signal_collapse_detected": self.signal_collapse_detected,
            "recommendation": recommendation,
            "next_check_in_minutes": self.config["check_interval_minutes"]
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
        "check_interval_minutes": 60,
        "correlation_threshold": 0.8,
        "indicators": ["rsi", "macd", "bollinger", "moving_averages"],
        "lookback_periods": 24,
        "log_file": f"{data_dir}/signal_collapse_log.txt",
        "data_file": f"{data_dir}/signal_collapse_data.json"
    }
    
    # Save config
    with open(f"{data_dir}/signal_collapse_config.json", 'w') as f:
        json.dump(config, f, indent=2)
        
    print("Signal Collapse Detector module created.")
    print("To use this module with your XRP Trading Bot:")
    print("1. Place this file in the same directory as your main bot script")
    print("2. Import the module in your main script:")
    print("   from signal_collapse_module import SignalCollapseDetector")
    print("3. Initialize the detector with your API keys:")
    print("   detector = SignalCollapseDetector(config_path='data/signal_collapse_config.json', api_key=YOUR_API_KEY, api_secret=YOUR_API_SECRET)")
    print("4. Run the analysis periodically:")
    print("   results = detector.run_analysis()")
    print("5. Check for signal collapse and adjust your strategy accordingly")
