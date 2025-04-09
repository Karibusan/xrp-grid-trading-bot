#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Survivability Module for XRP Trading Bot
Version: 3.0.0
Description: Module that assesses market conditions and adjusts trading
parameters to ensure long-term survivability of the trading strategy.
"""

import numpy as np
import pandas as pd
import time
import json
import os
import logging
from datetime import datetime, timedelta

class SurvivabilityAnalyzer:
    """
    A module that assesses market conditions and adjusts trading
    parameters to ensure long-term survivability of the trading strategy.
    """
    
    def __init__(self, config_path=None, api_client=None, notification_manager=None, error_handler=None):
        """
        Initialize the Survivability Analyzer module.
        
        Args:
            config_path (str): Path to configuration file
            api_client: API client instance for market data
            notification_manager: Notification manager instance
            error_handler: Error handler instance
        """
        self.logger = logging.getLogger('survivability_module')
        self.api_client = api_client
        self.notification_manager = notification_manager
        self.error_handler = error_handler
        
        # Default configuration
        self.default_config = {
            "enabled": True,
            "trading_pair": "XRPGBP",
            "check_interval_hours": 6,
            "volatility_window": 24,  # Hours
            "volume_window": 24,  # Hours
            "high_volatility_threshold": 0.05,
            "low_volume_threshold": 0.5,  # 50% of average
            "max_drawdown_threshold": 0.15,
            "risk_adjustment_factor": 0.5,
            "data_file": "data/survivability_data.json"
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
        self.risk_assessment = {}
        self.survival_mode = False
        self.recommended_adjustments = {}
        self.last_check_time = None
        
        self.logger.info("Survivability Analyzer initialized")
        if self.notification_manager:
            self.notification_manager.send_status_notification(
                "Survivability Module Initialized",
                f"Monitoring market conditions with {self.config['volatility_window']}h volatility window"
            )
    
    def _handle_error(self, message, error_type="module_error", severity="medium"):
        """Handle errors with proper logging and notification"""
        self.logger.error(message)
        
        if self.error_handler:
            self.error_handler.handle_error(error_type, message, severity, module="survivability")
        
        if self.notification_manager:
            self.notification_manager.send_error_notification(
                f"Survivability Module - {error_type}",
                message,
                severity
            )
    
    def fetch_market_data(self):
        """
        Fetch market data for survivability analysis
        
        Returns:
            bool: Success status
        """
        if not self.api_client:
            self._handle_error("API client not initialized", "api_client_error", "high")
            return False
            
        try:
            # Calculate time period to fetch
            lookback_hours = max(self.config["volatility_window"], self.config["volume_window"])
            since = datetime.now() - timedelta(hours=lookback_hours)
            since_unix = since.timestamp()
            
            # Fetch OHLC data (1 hour intervals)
            pair = self.config["trading_pair"]
            ohlc_data = self.api_client.get_ohlc_data(pair, interval=60, since=since_unix)
            
            if ohlc_data is not None and len(ohlc_data) > 0:
                self.market_data = ohlc_data
                self.logger.info(f"Fetched {len(ohlc_data)} hours of market data")
                return True
            else:
                self._handle_error("Failed to fetch market data", "market_data_error", "high")
                return False
            
        except Exception as e:
            self._handle_error(f"Error fetching market data: {str(e)}", "market_data_error", "high")
            return False
    
    def analyze_market_conditions(self):
        """
        Analyze market conditions for survivability assessment
        
        Returns:
            bool: Success status
        """
        if self.market_data is None or len(self.market_data) < self.config["volatility_window"]:
            self._handle_error("Insufficient market data for survivability analysis", "insufficient_data")
            return False
            
        try:
            # Reset risk assessment
            self.risk_assessment = {}
            
            # Calculate volatility
            volatility = self._calculate_volatility()
            self.risk_assessment["volatility"] = volatility
            self.risk_assessment["high_volatility"] = volatility >= self.config["high_volatility_threshold"]
            
            # Calculate volume trend
            volume_ratio = self._calculate_volume_ratio()
            self.risk_assessment["volume_ratio"] = volume_ratio
            self.risk_assessment["low_volume"] = volume_ratio <= self.config["low_volume_threshold"]
            
            # Calculate drawdown
            max_drawdown = self._calculate_max_drawdown()
            self.risk_assessment["max_drawdown"] = max_drawdown
            self.risk_assessment["excessive_drawdown"] = max_drawdown >= self.config["max_drawdown_threshold"]
            
            # Determine overall risk level
            risk_factors = [
                self.risk_assessment["high_volatility"],
                self.risk_assessment["low_volume"],
                self.risk_assessment["excessive_drawdown"]
            ]
            risk_count = sum(1 for factor in risk_factors if factor)
            
            if risk_count >= 2:
                self.survival_mode = True
                risk_level = "high"
            elif risk_count == 1:
                self.survival_mode = False
                risk_level = "medium"
            else:
                self.survival_mode = False
                risk_level = "low"
                
            self.risk_assessment["risk_level"] = risk_level
            
            # Calculate recommended adjustments
            self._calculate_recommended_adjustments()
            
            # Save risk assessment data
            self._save_risk_assessment()
            
            # Send notification if in survival mode
            if self.survival_mode and self.notification_manager:
                self._send_survivability_notification()
            
            self.logger.info(f"Survivability analysis completed. Risk level: {risk_level}, Survival mode: {self.survival_mode}")
            return True
            
        except Exception as e:
            self._handle_error(f"Error analyzing market conditions: {str(e)}", "analysis_error")
            return False
    
    def _calculate_volatility(self):
        """
        Calculate price volatility over the specified window
        
        Returns:
            float: Volatility (standard deviation of returns)
        """
        # Get close prices for volatility window
        close_prices = self.market_data['close'].values[-self.config["volatility_window"]:]
        
        # Calculate returns
        returns = np.diff(close_prices) / close_prices[:-1]
        
        # Calculate volatility (standard deviation of returns)
        volatility = np.std(returns)
        
        return volatility
    
    def _calculate_volume_ratio(self):
        """
        Calculate volume ratio (recent volume / historical average)
        
        Returns:
            float: Volume ratio
        """
        # Get volumes for volume window
        volumes = self.market_data['volume'].values[-self.config["volume_window"]:]
        
        # Calculate recent volume (last 6 hours)
        recent_volume = np.mean(volumes[-6:])
        
        # Calculate historical average volume
        historical_volume = np.mean(volumes)
        
        # Calculate volume ratio
        volume_ratio = recent_volume / historical_volume if historical_volume > 0 else 0
        
        return volume_ratio
    
    def _calculate_max_drawdown(self):
        """
        Calculate maximum drawdown over the specified window
        
        Returns:
            float: Maximum drawdown
        """
        # Get close prices for drawdown calculation
        close_prices = self.market_data['close'].values[-self.config["volatility_window"]:]
        
        # Calculate running maximum
        running_max = np.maximum.accumulate(close_prices)
        
        # Calculate drawdowns
        drawdowns = (running_max - close_prices) / running_max
        
        # Get maximum drawdown
        max_drawdown = np.max(drawdowns)
        
        return max_drawdown
    
    def _calculate_recommended_adjustments(self):
        """
        Calculate recommended trading parameter adjustments based on risk assessment
        """
        # Reset recommended adjustments
        self.recommended_adjustments = {}
        
        # Base adjustment factor
        adjustment_factor = self.config["risk_adjustment_factor"]
        
        # Adjust grid spacing
        if self.risk_assessment.get("high_volatility", False):
            # Increase grid spacing in high volatility
            self.recommended_adjustments["grid_spacing"] = 1 + adjustment_factor
        elif self.risk_assessment.get("low_volume", False):
            # Decrease grid spacing in low volume
            self.recommended_adjustments["grid_spacing"] = 1 - (adjustment_factor * 0.5)
        else:
            # No adjustment needed
            self.recommended_adjustments["grid_spacing"] = 1.0
        
        # Adjust order size
        if self.risk_assessment.get("excessive_drawdown", False):
            # Decrease order size in excessive drawdown
            self.recommended_adjustments["order_size"] = 1 - adjustment_factor
        elif self.risk_assessment.get("high_volatility", False):
            # Decrease order size in high volatility
            self.recommended_adjustments["order_size"] = 1 - (adjustment_factor * 0.7)
        else:
            # No adjustment needed
            self.recommended_adjustments["order_size"] = 1.0
        
        # Adjust profit target
        if self.risk_assessment.get("high_volatility", False):
            # Increase profit target in high volatility
            self.recommended_adjustments["profit_target"] = 1 + (adjustment_factor * 0.5)
        else:
            # No adjustment needed
            self.recommended_adjustments["profit_target"] = 1.0
    
    def _save_risk_assessment(self):
        """
        Save risk assessment data to file
        """
        try:
            data = {
                "timestamp": datetime.now().isoformat(),
                "risk_assessment": self.risk_assessment,
                "survival_mode": self.survival_mode,
                "recommended_adjustments": self.recommended_adjustments
            }
            
            with open(self.config["data_file"], 'w') as f:
                json.dump(data, f, indent=4)
                
            self.logger.info(f"Risk assessment data saved to {self.config['data_file']}")
            
        except Exception as e:
            self._handle_error(f"Error saving risk assessment data: {str(e)}", "data_save_error")
    
    def _send_survivability_notification(self):
        """
        Send notification about survivability mode and recommended adjustments
        """
        if not self.notification_manager:
            return
            
        # Prepare notification details
        risk_factors = []
        if self.risk_assessment.get("high_volatility", False):
            risk_factors.append(f"High volatility: {self.risk_assessment.get('volatility', 0):.4f}")
        if self.risk_assessment.get("low_volume", False):
            risk_factors.append(f"Low volume: {self.risk_assessment.get('volume_ratio', 0):.2f}x average")
        if self.risk_assessment.get("excessive_drawdown", False):
            risk_factors.append(f"Excessive drawdown: {self.risk_assessment.get('max_drawdown', 0):.2%}")
        
        adjustments = []
        for param, value in self.recommended_adjustments.items():
            direction = "increase" if value > 1 else "decrease"
            percent = abs(value - 1) * 100
            adjustments.append(f"{param.replace('_', ' ').title()}: {direction} by {percent:.1f}%")
        
        # Send notification
        self.notification_manager.send_efficiency_notification({
            "survivability_mode": True,
            "risk_level": self.risk_assessment.get("risk_level", "unknown"),
            "risk_factors": "\n".join(risk_factors),
            "recommended_adjustments": "\n".join(adjustments),
            "timestamp": datetime.now().isoformat()
        })
    
    def check_survivability(self):
        """
        Check market conditions for survivability assessment
        
        Returns:
            bool: True if in survival mode, False otherwise
        """
        # Check if it's time to run the check
        current_time = datetime.now()
        if self.last_check_time:
            elapsed_hours = (current_time - self.last_check_time).total_seconds() / 3600
            if elapsed_hours < self.config["check_interval_hours"]:
                return self.survival_mode
        
        # Update last check time
        self.last_check_time = current_time
        
        # Skip if module is disabled
        if not self.config["enabled"]:
            return False
        
        # Fetch market data
        if not self.fetch_market_data():
            return False
        
        # Analyze market conditions
        if not self.analyze_market_conditions():
            return False
        
        return self.survival_mode
    
    def get_risk_assessment(self):
        """
        Get risk assessment details
        
        Returns:
            dict: Risk assessment details
        """
        return self.risk_assessment
    
    def get_recommended_adjustments(self):
        """
        Get recommended trading parameter adjustments
        
        Returns:
            dict: Recommended adjustments
        """
        return self.recommended_adjustments
    
    def is_survival_mode(self):
        """
        Check if in survival mode
        
        Returns:
            bool: True if in survival mode, False otherwise
        """
        return self.survival_mode
