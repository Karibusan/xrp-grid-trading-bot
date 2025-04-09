#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Notification Manager for XRP Trading Bot v3.0
Provides a unified interface for sending notifications through various channels.
"""

import os
import json
import logging
import requests
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union
from datetime import datetime

class NotificationManager:
    """
    Manages notifications for the XRP Trading Bot.
    Provides a unified interface for sending notifications through various channels.
    """
    
    # Notification levels
    LEVEL_TRADE = "trade"
    LEVEL_DAILY_REPORT = "daily_report"
    LEVEL_EFFICIENCY = "efficiency"
    LEVEL_ERROR = "error"
    LEVEL_DEBUG = "debug"
    LEVEL_STATUS = "status"  # Added status level
    
    def __init__(self, config_path: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the notification manager.
        
        Args:
            config_path: Path to the notification configuration file
            config: Configuration dictionary (overrides config_path if provided)
        """
        self.logger = logging.getLogger('notification_manager')
        self.notifiers = {}
        self.config = {}
        
        # Load configuration
        if config:
            self.config = config
        elif config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    self.config = json.load(f)
            except Exception as e:
                self.logger.error(f"Failed to load notification config from {config_path}: {e}")
                self.config = {}
        
        # Initialize notifiers
        self._initialize_notifiers()
        
        # Initialize notification counters and timestamps for throttling
        self.notification_counts = {
            self.LEVEL_TRADE: 0,
            self.LEVEL_DAILY_REPORT: 0,
            self.LEVEL_EFFICIENCY: 0,
            self.LEVEL_ERROR: 0,
            self.LEVEL_DEBUG: 0,
            self.LEVEL_STATUS: 0  # Added status level counter
        }
        self.last_notification_time = {
            self.LEVEL_TRADE: None,
            self.LEVEL_DAILY_REPORT: None,
            self.LEVEL_EFFICIENCY: None,
            self.LEVEL_ERROR: None,
            self.LEVEL_DEBUG: None,
            self.LEVEL_STATUS: None  # Added status level timestamp
        }
    
    def _initialize_notifiers(self):
        """Initialize notification providers based on configuration."""
        # Initialize Pushover notifier if enabled
        if self.config.get('pushover', {}).get('enabled', False):
            pushover_config = self.config.get('pushover', {})
            self.notifiers['pushover'] = PushoverNotifier(
                user_key=pushover_config.get('user_key', ''),
                app_token=pushover_config.get('app_token', ''),
                device=pushover_config.get('device', ''),
                sound=pushover_config.get('sound', 'pushover'),
                priority=pushover_config.get('priority', 0)
            )
            self.logger.info("Pushover notifier initialized")
        
        # Initialize console notifier (always enabled as fallback)
        self.notifiers['console'] = ConsoleNotifier()
        self.logger.info("Console notifier initialized")
    
    def _should_throttle(self, level: str) -> bool:
        """
        Check if notification should be throttled based on configuration.
        
        Args:
            level: Notification level
            
        Returns:
            True if notification should be throttled, False otherwise
        """
        throttling = self.config.get('throttling', {})
        if not throttling.get('enabled', False):
            return False
            
        # Check if level is enabled
        if not self.config.get('notification_levels', {}).get(level, True):
            return True
            
        # Check max notifications per hour
        max_per_hour = throttling.get('max_notifications_per_hour', {}).get(level, 20)
        if self.notification_counts[level] >= max_per_hour:
            self.logger.warning(f"Throttling {level} notification: exceeded max per hour ({max_per_hour})")
            return True
            
        # Check min time between notifications
        min_seconds = throttling.get('min_time_between_notifications_seconds', {}).get(level, 30)
        last_time = self.last_notification_time[level]
        if last_time:
            elapsed = (datetime.now() - last_time).total_seconds()
            if elapsed < min_seconds:
                self.logger.warning(f"Throttling {level} notification: too soon after last one ({elapsed:.1f}s < {min_seconds}s)")
                return True
                
        return False
    
    def _update_throttling_stats(self, level: str):
        """
        Update notification counts and timestamps for throttling.
        
        Args:
            level: Notification level
        """
        self.notification_counts[level] += 1
        self.last_notification_time[level] = datetime.now()
    
    def _get_level_config(self, level: str) -> Dict[str, Any]:
        """
        Get configuration for a specific notification level.
        
        Args:
            level: Notification level
            
        Returns:
            Configuration dictionary for the level
        """
        level_config = self.config.get('level_settings', {}).get(level, {})
        
        # Set defaults based on level if not specified
        if 'priority' not in level_config:
            if level == self.LEVEL_ERROR:
                level_config['priority'] = 1  # High priority for errors
            elif level == self.LEVEL_TRADE:
                level_config['priority'] = 0  # Normal priority for trades
            elif level == self.LEVEL_DAILY_REPORT:
                level_config['priority'] = -1  # Low priority for daily reports
            elif level == self.LEVEL_STATUS:
                level_config['priority'] = 0  # Normal priority for status updates
            else:
                level_config['priority'] = 0  # Normal priority for others
                
        if 'sound' not in level_config:
            if level == self.LEVEL_ERROR:
                level_config['sound'] = 'siren'  # Attention-grabbing sound for errors
            elif level == self.LEVEL_TRADE:
                level_config['sound'] = 'cashregister'  # Money sound for trades
            elif level == self.LEVEL_DAILY_REPORT:
                level_config['sound'] = 'classical'  # Calm sound for reports
            elif level == self.LEVEL_EFFICIENCY:
                level_config['sound'] = 'mechanical'  # Technical sound for efficiency
            elif level == self.LEVEL_STATUS:
                level_config['sound'] = 'pushover'  # Default sound for status updates
            else:
                level_config['sound'] = 'pushover'  # Default sound for others
                
        return level_config
    
    def send_notification(self, title: str, message: str, 
                         level: str = None,
                         priority: Optional[int] = None, 
                         sound: Optional[str] = None,
                         url: Optional[str] = None,
                         attachment: Optional[str] = None,
                         notifier_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Send a notification through all enabled notifiers or specified ones.
        
        Args:
            title: Notification title
            message: Notification message
            level: Notification level (trade, daily_report, efficiency, error, debug, status)
            priority: Priority level (-2 to 2, with 2 being emergency)
            sound: Sound to play
            url: URL to include in notification
            attachment: Path to attachment file
            notifier_types: List of notifier types to use (e.g., ['pushover', 'console'])
                           If None, uses all enabled notifiers
        
        Returns:
            Dictionary with results from each notifier
        """
        # Set default level if not provided
        if level is None:
            level = self.LEVEL_STATUS  # Changed default to status
            
        # Check if notification should be throttled
        if self._should_throttle(level):
            return {"throttled": True, "level": level}
            
        # Update throttling statistics
        self._update_throttling_stats(level)
        
        # Get level-specific configuration
        level_config = self._get_level_config(level)
        
        # Override with provided values or use level defaults
        if priority is None:
            priority = level_config.get('priority')
            
        if sound is None:
            sound = level_config.get('sound')
        
        results = {}
        
        # Determine which notifiers to use
        notifiers_to_use = {}
        if notifier_types:
            for notifier_type in notifier_types:
                if notifier_type in self.notifiers:
                    notifiers_to_use[notifier_type] = self.notifiers[notifier_type]
                else:
                    self.logger.warning(f"Requested notifier '{notifier_type}' not available")
        else:
            notifiers_to_use = self.notifiers
        
        # Send notification through each notifier
        for notifier_type, notifier in notifiers_to_use.items():
            try:
                result = notifier.send(title, message, priority, sound, url, attachment)
                results[notifier_type] = result
                self.logger.debug(f"Notification sent via {notifier_type}: {result}")
            except Exception as e:
                self.logger.error(f"Failed to send notification via {notifier_type}: {e}")
                results[notifier_type] = {"success": False, "error": str(e)}
        
        return results
    
    def send_trade_notification(self, trade_type: str, volume: float, price: float, 
                               total: float, margin: Optional[float] = None) -> Dict[str, Any]:
        """
        Send a trade notification.
        
        Args:
            trade_type: Type of trade (buy/sell)
            volume: Trade volume
            price: Trade price
            total: Total value
            margin: Profit margin (for sell trades)
        
        Returns:
            Dictionary with results from each notifier
        """
        trade_type = trade_type.upper()
        title = f"XRP {trade_type} EXECUTED"
        
        message = f"{trade_type} {volume:.8f} XRP at {price:.4f}\n"
        message += f"Total: {total:.4f}\n"
        
        if margin is not None and trade_type == "SELL":
            message += f"Profit: {margin:.4f} ({(margin/total)*100:.2f}%)"
        
        return self.send_notification(title, message, level=self.LEVEL_TRADE)
    
    def send_daily_report_notification(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a daily report notification.
        
        Args:
            report_data: Dictionary containing report data
                - trades_executed: Number of trades executed
                - profit_loss: Profit/loss percentage
                - current_balance: Current balance
                - open_orders: Number of open orders
                - additional_metrics: Any additional metrics
        
        Returns:
            Dictionary with results from each notifier
        """
        title = f"XRP Bot Daily Report: {datetime.now().strftime('%Y-%m-%d')}"
        
        message = "=== DAILY TRADING REPORT ===\n\n"
        
        if 'trades_executed' in report_data:
            message += f"Trades Executed: {report_data['trades_executed']}\n"
            
        if 'profit_loss' in report_data:
            message += f"Profit/Loss: {report_data['profit_loss']}\n"
            
        if 'current_balance' in report_data:
            message += f"Current Balance: {report_data['current_balance']}\n"
            
        if 'open_orders' in report_data:
            message += f"Open Orders: {report_data['open_orders']}\n"
            
        if 'additional_metrics' in report_data:
            message += f"\nAdditional Metrics: {report_data['additional_metrics']}"
        
        return self.send_notification(title, message, level=self.LEVEL_DAILY_REPORT)
    
    def send_efficiency_notification(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send an efficiency notification with system performance metrics.
        
        Args:
            metrics: Dictionary containing efficiency metrics
                - cpu_usage: CPU usage percentage
                - memory_usage: Memory usage percentage
                - api_calls: Number of API calls made
                - response_time: Average API response time
                - execution_time: Total execution time
                - additional_metrics: Any additional metrics
        
        Returns:
            Dictionary with results from each notifier
        """
        title = f"XRP Bot Efficiency Report: {datetime.now().strftime('%H:%M:%S')}"
        
        message = "=== SYSTEM EFFICIENCY ===\n\n"
        
        if 'cpu_usage' in metrics:
            message += f"CPU Usage: {metrics['cpu_usage']}%\n"
            
        if 'memory_usage' in metrics:
            message += f"Memory Usage: {metrics['memory_usage']}%\n"
            
        if 'api_calls' in metrics:
            message += f"API Calls: {metrics['api_calls']}\n"
            
        if 'response_time' in metrics:
            message += f"Avg Response Time: {metrics['response_time']}s\n"
            
        if 'execution_time' in metrics:
            message += f"Execution Time: {metrics['execution_time']}s\n"
            
        if 'additional_metrics' in metrics:
            message += f"\nAdditional Metrics: {metrics['additional_metrics']}"
        
        return self.send_notification(title, message, level=self.LEVEL_EFFICIENCY)
    
    def send_error_notification(self, error_type: str, error_message: str, 
                               severity: str = "medium") -> Dict[str, Any]:
        """
        Send an error notification.
        
        Args:
            error_type: Type of error
            error_message: Error message
            severity: Error severity (low, medium, high, critical)
        
        Returns:
            Dictionary with results from each notifier
        """
        severity = severity.lower()
        priority = 0
        
        if severity == "critical":
            priority = 2  # Emergency priority
        elif severity == "high":
            priority = 1  # High priority
        elif severity == "medium":
            priority = 0  # Normal priority
        elif severity == "low":
            priority = -1  # Low priority
        
        title = f"XRP Bot ERROR: {severity.upper()}"
        message = f"Error Type: {error_type}\n\n{error_message}"
        
        return self.send_notification(title, message, level=self.LEVEL_ERROR, priority=priority)
    
    def send_debug_notification(self, debug_info: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Send a debug notification.
        
        Args:
            debug_info: Debug information
            context: Context information
        
        Returns:
            Dictionary with results from each notifier
        """
        title = f"XRP Bot Debug: {datetime.now().strftime('%H:%M:%S')}"
        
        message = "=== DEBUG INFO ===\n\n"
        
        if context:
            message += f"Context: {context}\n\n"
            
        message += debug_info
        
        return self.send_notification(title, message, level=self.LEVEL_DEBUG, priority=-2)
    
    def send_status_notification(self, status: str, details: Optional[str] = None) -> Dict[str, Any]:
        """
        Send a status notification.
        
        Args:
            status: Status message
            details: Additional details
        
        Returns:
            Dictionary with results from each notifier
        """
        title = f"XRP Bot Status: {datetime.now().strftime('%H:%M:%S')}"
        
        message = f"Status: {status}\n"
        
        if details:
            message += f"\nDetails: {details}"
        
        return self.send_notification(title, message, level=self.LEVEL_STATUS)
    
    def is_pushover_enabled(self) -> bool:
        """
        Check if Pushover notifications are enabled.
        
        Returns:
            True if Pushover is enabled, False otherwise
        """
        return 'pushover' in self.notifiers


class BaseNotifier(ABC):
    """Base class for notification providers."""
    
    @abstractmethod
    def send(self, title: str, message: str, 
            priority: Optional[int] = None, 
            sound: Optional[str] = None,
            url: Optional[str] = None,
            attachment: Optional[str] = None) -> Dict[str, Any]:
        """
        Send a notification.
        
        Args:
            title: Notification title
            message: Notification message
            priority: Priority level
            sound: Sound to play
            url: URL to include in notification
            attachment: Path to attachment file
        
        Returns:
            Dictionary with notification result
        """
        pass


class PushoverNotifier(BaseNotifier):
    """Pushover notification provider."""
    
    def __init__(self, user_key: str, app_token: str, 
                device: str = "", sound: str = "pushover", priority: int = 0):
        """
        Initialize Pushover notifier.
        
        Args:
            user_key: Pushover user key
            app_token: Pushover application token
            device: Device name (optional)
            sound: Default sound (optional)
            priority: Default priority (optional)
        """
        self.user_key = user_key
        self.app_token = app_token
        self.device = device
        self.sound = sound
        self.priority = priority
        self.api_url = "https://api.pushover.net/1/messages.json"
        self.logger = logging.getLogger('notification_manager')
    
    def send(self, title: str, message: str, 
            priority: Optional[int] = None, 
            sound: Optional[str] = None,
            url: Optional[str] = None,
            attachment: Optional[str] = None) -> Dict[str, Any]:
        """
        Send a notification via Pushover.
        
        Args:
            title: Notification title
            message: Notification message
            priority: Priority level (-2 to 2, with 2 being emergency)
            sound: Sound to play
            url: URL to include in notification
            attachment: Path to attachment file
        
        Returns:
            Dictionary with notification result
        """
        # Use provided values or defaults
        if priority is None:
            priority = self.priority
            
        if sound is None:
            sound = self.sound
        
        # Prepare payload
        payload = {
            "token": self.app_token,
            "user": self.user_key,
            "title": title,
            "message": message,
            "priority": priority,
            "sound": sound
        }
        
        # Add device if specified
        if self.device:
            payload["device"] = self.device
            
        # Add URL if provided
        if url:
            payload["url"] = url
        
        # Prepare files for attachment
        files = {}
        if attachment and os.path.exists(attachment):
            files = {
                "attachment": (os.path.basename(attachment), open(attachment, "rb"))
            }
        
        try:
            # Send request
            if files:
                response = requests.post(self.api_url, data=payload, files=files)
            else:
                response = requests.post(self.api_url, data=payload)
            
            # Parse response
            response_data = response.json()
            
            # Check if request was successful
            if response.status_code == 200 and response_data.get("status") == 1:
                return {"success": True, "request_id": response_data.get("request")}
            else:
                error_message = response_data.get("errors", ["Unknown error"])[0]
                self.logger.error(f"Pushover API error: {error_message}")
                return {"success": False, "error": error_message}
                
        except Exception as e:
            self.logger.error(f"Failed to send Pushover notification: {e}")
            return {"success": False, "error": str(e)}
        finally:
            # Close file if opened
            if attachment and os.path.exists(attachment) and "attachment" in files:
                files["attachment"][1].close()


class ConsoleNotifier(BaseNotifier):
    """Console notification provider (for development and testing)."""
    
    def __init__(self):
        """Initialize console notifier."""
        self.logger = logging.getLogger('notification_manager')
    
    def send(self, title: str, message: str, 
            priority: Optional[int] = None, 
            sound: Optional[str] = None,
            url: Optional[str] = None,
            attachment: Optional[str] = None) -> Dict[str, Any]:
        """
        Send a notification to console.
        
        Args:
            title: Notification title
            message: Notification message
            priority: Priority level (ignored)
            sound: Sound to play (ignored)
            url: URL to include in notification (ignored)
            attachment: Path to attachment file (ignored)
        
        Returns:
            Dictionary with notification result
        """
        # Format notification
        notification = f"\n{'='*50}\n"
        notification += f"NOTIFICATION: {title}\n"
        notification += f"{'='*50}\n"
        notification += f"{message}\n"
        
        if url:
            notification += f"\nURL: {url}\n"
            
        if attachment:
            notification += f"\nAttachment: {attachment}\n"
            
        notification += f"{'='*50}\n"
        
        # Print to console
        print(notification)
        
        return {"success": True}
