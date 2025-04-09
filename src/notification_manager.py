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
            self.LEVEL_DEBUG: 0
        }
        self.last_notification_time = {
            self.LEVEL_TRADE: None,
            self.LEVEL_DAILY_REPORT: None,
            self.LEVEL_EFFICIENCY: None,
            self.LEVEL_ERROR: None,
            self.LEVEL_DEBUG: None
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
            level: Notification level (trade, daily_report, efficiency, error, debug)
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
            level = self.LEVEL_DEBUG
            
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
    
    def send_daily_report(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a daily report notification.
        
        Args:
            report_data: Dictionary containing report data
                - trades_count: Number of trades executed
                - buy_volume: Total buy volume
                - sell_volume: Total sell volume
                - profit: Total profit
                - current_balance: Current balance
                - price_change: Price change percentage
                - additional_info: Any additional information
        
        Returns:
            Dictionary with results from each notifier
        """
        title = f"XRP Bot Daily Report: {datetime.now().strftime('%Y-%m-%d')}"
        
        message = "=== DAILY TRADING REPORT ===\n\n"
        
        if 'trades_count' in report_data:
            message += f"Trades Executed: {report_data['trades_count']}\n"
            
        if 'buy_volume' in report_data and 'sell_volume' in report_data:
            message += f"Buy Volume: {report_data['buy_volume']:.8f} XRP\n"
            message += f"Sell Volume: {report_data['sell_volume']:.8f} XRP\n"
            message += f"Net Volume: {report_data['buy_volume'] - report_data['sell_volume']:.8f} XRP\n"
            
        if 'profit' in report_data:
            message += f"Total Profit: {report_data['profit']:.4f}\n"
            
        if 'current_balance' in report_data:
            message += f"Current Balance: {report_data['current_balance']:.4f}\n"
            
        if 'price_change' in report_data:
            message += f"24h Price Change: {report_data['price_change']:.2f}%\n"
            
        if 'additional_info' in report_data:
            message += f"\nAdditional Information:\n{report_data['additional_info']}\n"
            
        return self.send_notification(title, message, level=self.LEVEL_DAILY_REPORT)
    
    def send_efficiency_notification(self, metrics: Dict[str, Union[float, int, str]]) -> Dict[str, Any]:
        """
        Send an efficiency notification.
        
        Args:
            metrics: Dictionary containing efficiency metrics
                - cpu_usage: CPU usage percentage
                - memory_usage: Memory usage percentage
                - api_calls: Number of API calls made
                - response_time: Average API response time
                - execution_time: Execution time for trading cycle
                - additional_metrics: Any additional metrics
        
        Returns:
            Dictionary with results from each notifier
        """
        title = "XRP Bot Efficiency Metrics"
        
        message = "=== SYSTEM EFFICIENCY ===\n\n"
        
        if 'cpu_usage' in metrics:
            message += f"CPU Usage: {metrics['cpu_usage']:.1f}%\n"
            
        if 'memory_usage' in metrics:
            message += f"Memory Usage: {metrics['memory_usage']:.1f}%\n"
            
        if 'api_calls' in metrics:
            message += f"API Calls: {metrics['api_calls']}\n"
            
        if 'response_time' in metrics:
            message += f"Avg Response Time: {metrics['response_time']:.2f}ms\n"
            
        if 'execution_time' in metrics:
            message += f"Trading Cycle Time: {metrics['execution_time']:.2f}s\n"
            
        if 'additional_metrics' in metrics:
            message += f"\nAdditional Metrics:\n{metrics['additional_metrics']}\n"
            
        return self.send_notification(title, message, level=self.LEVEL_EFFICIENCY)
    
    def send_error_notification(self, error_type: str, error_message: str, 
                               details: Optional[str] = None) -> Dict[str, Any]:
        """
        Send an error notification.
        
        Args:
            error_type: Type of error
            error_message: Error message
            details: Additional error details
        
        Returns:
            Dictionary with results from each notifier
        """
        title = f"XRP Bot Error: {error_type}"
        
        message = f"Error: {error_message}\n"
        if details:
            message += f"Details: {details}"
        
        return self.send_notification(title, message, level=self.LEVEL_ERROR)
    
    def send_debug_notification(self, debug_type: str, debug_message: str,
                              details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Send a debug notification.
        
        Args:
            debug_type: Type of debug information
            debug_message: Debug message
            details: Additional debug details
        
        Returns:
            Dictionary with results from each notifier
        """
        title = f"XRP Bot Debug: {debug_type}"
        
        message = f"{debug_message}\n"
        if details:
            for key, value in details.items():
                message += f"{key}: {value}\n"
                
        return self.send_notification(title, message, level=self.LEVEL_DEBUG)


class BaseNotifier(ABC):
    """Abstract base class for notification providers."""
    
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
            url: URL to include
            attachment: Path to attachment file
        
        Returns:
            Dictionary with notification result
        """
        pass


class PushoverNotifier(BaseNotifier):
    """Pushover notification provider."""
    
    def __init__(self, user_key: str, app_token: str, 
                device: str = "", sound: str = "pushover", 
                priority: int = 0):
        """
        Initialize Pushover notifier.
        
        Args:
            user_key: Pushover user key
            app_token: Pushover application token
            device: Device name (optional)
            sound: Notification sound (optional)
            priority: Default priority (optional)
        """
        self.user_key = user_key
        self.app_token = app_token
        self.device = device
        self.sound = sound
        self.priority = priority
        self.api_url = "https://api.pushover.net/1/messages.json"
        self.logger = logging.getLogger('pushover_notifier')
        
        # Validate configuration
        if not user_key or not app_token:
            self.logger.warning("Pushover user key or app token not provided")
    
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
            url: URL to include
            attachment: Path to attachment file
        
        Returns:
            Dictionary with notification result
        """
        if not self.user_key or not self.app_token:
            return {"success": False, "error": "Pushover credentials not configured"}
        
        # Prepare payload
        payload = {
            "token": self.app_token,
            "user": self.user_key,
            "title": title,
            "message": message,
            "priority": priority if priority is not None else self.priority,
            "sound": sound if sound is not None else self.sound,
            "timestamp": int(datetime.now().timestamp())
        }
        
        # Add device if specified
        if self.device:
            payload["device"] = self.device
            
        # Add URL if specified
        if url:
            payload["url"] = url
            
        files = {}
        # Add attachment if specified
        if attachment and os.path.exists(attachment):
            with open(attachment, "rb") as f:
                files["attachment"] = (os.path.basename(attachment), f, "application/octet-stream")
        
        try:
            # Send request
            if files:
                response = requests.post(self.api_url, data=payload, files=files)
            else:
                response = requests.post(self.api_url, data=payload)
            
            # Parse response
            if response.status_code == 200:
                return {"success": True, "response": response.json()}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
                
        except Exception as e:
            self.logger.error(f"Failed to send Pushover notification: {e}")
            return {"success": False, "error": str(e)}


class ConsoleNotifier(BaseNotifier):
    """Console notification provider (for debugging and fallback)."""
    
    def __init__(self):
        """Initialize console notifier."""
        self.logger = logging.getLogger('console_notifier')
    
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
            url: URL to include (ignored)
            attachment: Path to attachment file (ignored)
        
        Returns:
            Dictionary with notification result
        """
        print(f"\n=== NOTIFICATION: {title} ===")
        print(message)
        if url:
            print(f"URL: {url}")
        if attachment:
            print(f"Attachment: {attachment}")
        print("=" * (18 + len(title)))
        
        return {"success": True}


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Example configuration
    config = {
        "pushover": {
            "enabled": True,
            "user_key": "YOUR_USER_KEY",
            "app_token": "YOUR_APP_TOKEN",
            "device": "",
            "sound": "pushover",
            "priority": 0
        },
        "notification_levels": {
            "trade": True,
            "daily_report": True,
            "efficiency": True,
            "error": True,
            "debug": False
        },
        "level_settings": {
            "trade": {
                "priority": 0,
                "sound": "cashregister"
            },
            "daily_report": {
                "priority": -1,
                "sound": "classical"
            },
            "efficiency": {
                "priority": -1,
                "sound": "mechanical"
            },
            "error": {
                "priority": 1,
                "sound": "siren"
            },
            "debug": {
                "priority": -2,
                "sound": "none"
            }
        },
        "throttling": {
            "enabled": True,
            "max_notifications_per_hour": {
                "trade": 20,
                "daily_report": 2,
                "efficiency": 4,
                "error": 10,
                "debug": 5
            },
            "min_time_between_notifications_seconds": {
                "trade": 30,
                "daily_report": 3600,
                "efficiency": 900,
                "error": 60,
                "debug": 300
            }
        }
    }
    
    # Create notification manager
    notification_manager = NotificationManager(config=config)
    
    # Send test notifications for each level
    notification_manager.send_trade_notification(
        trade_type="buy",
        volume=100.0,
        price=0.5123,
        total=51.23
    )
    
    notification_manager.send_daily_report({
        "trades_count": 15,
        "buy_volume": 500.0,
        "sell_volume": 450.0,
        "profit": 25.75,
        "current_balance": 1250.45,
        "price_change": 2.35
    })
    
    notification_manager.send_efficiency_notification({
        "cpu_usage": 15.2,
        "memory_usage": 28.7,
        "api_calls": 120,
        "response_time": 245.8,
        "execution_time": 3.45
    })
    
    notification_manager.send_error_notification(
        error_type="API Error",
        error_message="Failed to connect to Kraken API",
        details="Timeout after 30 seconds"
    )
    
    notification_manager.send_debug_notification(
        debug_type="Order Placement",
        debug_message="Order placement details",
        details={
            "order_id": "ABCDEF-12345",
            "type": "buy",
            "volume": 100.0,
            "price": 0.5123
        }
    )
