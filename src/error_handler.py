#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Error Handler for XRP Trading Bot v3.0
Provides centralized error handling, logging, and recovery mechanisms.
"""

import os
import sys
import json
import time
import logging
import traceback
from typing import Dict, Any, Optional, List, Callable, Union
from datetime import datetime, timedelta
from functools import wraps

class ErrorHandler:
    """
    Centralized error handling system for the XRP Trading Bot.
    Provides error tracking, logging, recovery mechanisms, and notification integration.
    """
    
    # Error severity levels
    SEVERITY_CRITICAL = "critical"  # System cannot continue, requires immediate attention
    SEVERITY_HIGH = "high"          # Significant issue affecting functionality, needs prompt attention
    SEVERITY_MEDIUM = "medium"      # Issue affecting some functionality, should be addressed soon
    SEVERITY_LOW = "low"            # Minor issue with minimal impact, can be addressed later
    SEVERITY_INFO = "info"          # Informational message about potential issues
    
    # Error categories
    CATEGORY_API = "api"            # API-related errors (Kraken, external services)
    CATEGORY_NETWORK = "network"    # Network connectivity issues
    CATEGORY_CONFIG = "config"      # Configuration errors
    CATEGORY_DATA = "data"          # Data processing or storage errors
    CATEGORY_SYSTEM = "system"      # System-level errors (file system, resources)
    CATEGORY_TRADING = "trading"    # Trading logic errors
    CATEGORY_MODULE = "module"      # Module-specific errors
    
    def __init__(self, config_path: Optional[str] = None, 
                config: Optional[Dict[str, Any]] = None,
                notification_manager=None):
        """
        Initialize the error handler.
        
        Args:
            config_path: Path to the error handler configuration file
            config: Configuration dictionary (overrides config_path if provided)
            notification_manager: NotificationManager instance for sending error notifications
        """
        self.logger = logging.getLogger('error_handler')
        self.config = {}
        self.notification_manager = notification_manager
        self.error_counts = {}  # Track error occurrences by type
        self.last_error_time = {}  # Track last occurrence time by error type
        self.recovery_attempts = {}  # Track recovery attempts by error type
        
        # Load configuration
        if config:
            self.config = config
        elif config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    self.config = json.load(f)
            except Exception as e:
                self.logger.error(f"Failed to load error handler config from {config_path}: {e}")
                self.config = {}
        
        # Initialize error log file
        self.error_log_path = self.config.get('error_log_path', 'data/error_log.json')
        os.makedirs(os.path.dirname(self.error_log_path), exist_ok=True)
        
        # Create error log file if it doesn't exist
        if not os.path.exists(self.error_log_path):
            with open(self.error_log_path, 'w') as f:
                json.dump([], f)
    
    def handle_error(self, error_type: str, error_message: str, 
                    exception: Optional[Exception] = None,
                    severity: str = SEVERITY_MEDIUM,
                    category: str = CATEGORY_SYSTEM,
                    context: Optional[Dict[str, Any]] = None,
                    notify: bool = True,
                    recovery_func: Optional[Callable] = None,
                    max_recovery_attempts: int = 3) -> Dict[str, Any]:
        """
        Handle an error by logging it, attempting recovery if possible, and optionally notifying.
        
        Args:
            error_type: Type of error
            error_message: Error message
            exception: Exception object if available
            severity: Error severity level
            category: Error category
            context: Additional context information
            notify: Whether to send notification
            recovery_func: Function to call for recovery attempt
            max_recovery_attempts: Maximum number of recovery attempts
            
        Returns:
            Dictionary with error handling result
        """
        # Generate error ID
        error_id = f"{int(time.time())}_{category}_{error_type}"
        
        # Get stack trace if exception is provided
        stack_trace = None
        if exception:
            stack_trace = ''.join(traceback.format_exception(
                type(exception), exception, exception.__traceback__))
        
        # Create error record
        error_record = {
            "id": error_id,
            "timestamp": datetime.now().isoformat(),
            "type": error_type,
            "message": error_message,
            "severity": severity,
            "category": category,
            "stack_trace": stack_trace,
            "context": context
        }
        
        # Log error
        self._log_error(error_record)
        
        # Update error statistics
        self._update_error_stats(error_type)
        
        # Attempt recovery if function provided
        recovery_result = None
        if recovery_func and self._should_attempt_recovery(error_type, max_recovery_attempts):
            try:
                self.logger.info(f"Attempting recovery for error {error_id}")
                recovery_result = recovery_func()
                error_record["recovery_attempted"] = True
                error_record["recovery_result"] = recovery_result
                self.recovery_attempts[error_type] = self.recovery_attempts.get(error_type, 0) + 1
            except Exception as recovery_exception:
                recovery_error = f"Recovery failed: {str(recovery_exception)}"
                error_record["recovery_attempted"] = True
                error_record["recovery_result"] = {"success": False, "error": recovery_error}
                self.logger.error(f"Recovery attempt failed for {error_id}: {recovery_error}")
        
        # Send notification if requested and notification manager is available
        notification_result = None
        if notify and self.notification_manager and self._should_notify(error_type, severity):
            try:
                details = f"Category: {category}\nSeverity: {severity}"
                if context:
                    details += f"\nContext: {json.dumps(context, indent=2)}"
                if stack_trace:
                    # Truncate stack trace if too long
                    max_trace_length = 500
                    if len(stack_trace) > max_trace_length:
                        stack_trace = stack_trace[:max_trace_length] + "...[truncated]"
                    details += f"\nStack Trace:\n{stack_trace}"
                
                notification_result = self.notification_manager.send_error_notification(
                    error_type=error_type,
                    error_message=error_message,
                    details=details
                )
                error_record["notification_sent"] = True
                error_record["notification_result"] = notification_result
            except Exception as notification_exception:
                self.logger.error(f"Failed to send notification for {error_id}: {notification_exception}")
                error_record["notification_sent"] = False
                error_record["notification_error"] = str(notification_exception)
        
        # Update error log with final record
        self._update_error_log(error_record)
        
        return {
            "error_id": error_id,
            "handled": True,
            "recovery_attempted": recovery_func is not None,
            "recovery_result": recovery_result,
            "notification_sent": notify and self.notification_manager is not None,
            "notification_result": notification_result,
            "severity": severity,
            "category": category
        }
    
    def _log_error(self, error_record: Dict[str, Any]):
        """
        Log error to the logger based on severity.
        
        Args:
            error_record: Error record dictionary
        """
        message = f"ERROR [{error_record['severity']}] {error_record['category']}: {error_record['type']} - {error_record['message']}"
        
        if error_record['severity'] == self.SEVERITY_CRITICAL:
            self.logger.critical(message)
        elif error_record['severity'] == self.SEVERITY_HIGH:
            self.logger.error(message)
        elif error_record['severity'] == self.SEVERITY_MEDIUM:
            self.logger.error(message)
        elif error_record['severity'] == self.SEVERITY_LOW:
            self.logger.warning(message)
        else:  # INFO
            self.logger.info(message)
    
    def _update_error_stats(self, error_type: str):
        """
        Update error statistics.
        
        Args:
            error_type: Type of error
        """
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        self.last_error_time[error_type] = datetime.now()
    
    def _should_attempt_recovery(self, error_type: str, max_attempts: int) -> bool:
        """
        Determine if recovery should be attempted based on previous attempts.
        
        Args:
            error_type: Type of error
            max_attempts: Maximum number of recovery attempts
            
        Returns:
            True if recovery should be attempted, False otherwise
        """
        # Check if max attempts reached
        current_attempts = self.recovery_attempts.get(error_type, 0)
        if current_attempts >= max_attempts:
            self.logger.warning(f"Max recovery attempts ({max_attempts}) reached for {error_type}")
            return False
        
        # Check if enough time has passed since last attempt
        if error_type in self.last_error_time:
            last_time = self.last_error_time[error_type]
            cooldown_minutes = self.config.get('recovery_cooldown_minutes', {}).get(error_type, 5)
            cooldown_delta = timedelta(minutes=cooldown_minutes)
            
            if datetime.now() - last_time < cooldown_delta:
                self.logger.info(f"Recovery cooldown period not elapsed for {error_type}")
                return False
        
        return True
    
    def _should_notify(self, error_type: str, severity: str) -> bool:
        """
        Determine if notification should be sent based on error type and severity.
        
        Args:
            error_type: Type of error
            severity: Error severity
            
        Returns:
            True if notification should be sent, False otherwise
        """
        # Always notify for critical errors
        if severity == self.SEVERITY_CRITICAL:
            return True
        
        # Check notification settings for this error type
        notify_settings = self.config.get('notification_settings', {})
        
        # Check if notification is enabled for this severity
        severity_enabled = notify_settings.get('severity', {}).get(severity, True)
        if not severity_enabled:
            return False
        
        # Check if notification is enabled for this error type
        error_type_enabled = notify_settings.get('error_types', {}).get(error_type, True)
        if not error_type_enabled:
            return False
        
        # Check if we've sent too many notifications for this error type recently
        if error_type in self.error_counts:
            max_notifications = notify_settings.get('max_notifications_per_hour', {}).get(error_type, 5)
            if self.error_counts[error_type] > max_notifications:
                # Check if it's been an hour since first notification
                if error_type in self.last_error_time:
                    hour_ago = datetime.now() - timedelta(hours=1)
                    if self.last_error_time[error_type] > hour_ago:
                        self.logger.info(f"Suppressing notification for {error_type}: too many in last hour")
                        return False
                    else:
                        # Reset counter if it's been more than an hour
                        self.error_counts[error_type] = 1
        
        return True
    
    def _update_error_log(self, error_record: Dict[str, Any]):
        """
        Update the error log file with a new error record.
        
        Args:
            error_record: Error record dictionary
        """
        try:
            # Read existing log
            error_log = []
            if os.path.exists(self.error_log_path):
                with open(self.error_log_path, 'r') as f:
                    error_log = json.load(f)
            
            # Add new record
            error_log.append(error_record)
            
            # Limit log size if configured
            max_log_size = self.config.get('max_log_size', 1000)
            if len(error_log) > max_log_size:
                error_log = error_log[-max_log_size:]
            
            # Write updated log
            with open(self.error_log_path, 'w') as f:
                json.dump(error_log, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to update error log: {e}")
    
    def get_error_summary(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get a summary of errors in the specified time period.
        
        Args:
            hours: Number of hours to include in summary
            
        Returns:
            Dictionary with error summary
        """
        try:
            # Read error log
            error_log = []
            if os.path.exists(self.error_log_path):
                with open(self.error_log_path, 'r') as f:
                    error_log = json.load(f)
            
            # Filter by time period
            cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()
            recent_errors = [e for e in error_log if e.get('timestamp', '') >= cutoff_time]
            
            # Count by category and severity
            category_counts = {}
            severity_counts = {}
            error_type_counts = {}
            
            for error in recent_errors:
                category = error.get('category', 'unknown')
                severity = error.get('severity', 'unknown')
                error_type = error.get('type', 'unknown')
                
                category_counts[category] = category_counts.get(category, 0) + 1
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
                error_type_counts[error_type] = error_type_counts.get(error_type, 0) + 1
            
            return {
                "total_errors": len(recent_errors),
                "time_period_hours": hours,
                "by_category": category_counts,
                "by_severity": severity_counts,
                "by_type": error_type_counts,
                "most_recent": recent_errors[-5:] if recent_errors else []
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate error summary: {e}")
            return {"error": str(e)}
    
    def error_decorator(self, error_type: str, severity: str = SEVERITY_MEDIUM, 
                       category: str = CATEGORY_SYSTEM, notify: bool = True,
                       recovery_func: Optional[Callable] = None,
                       max_recovery_attempts: int = 3):
        """
        Decorator for handling errors in functions.
        
        Args:
            error_type: Type of error
            severity: Error severity level
            category: Error category
            notify: Whether to send notification
            recovery_func: Function to call for recovery attempt
            max_recovery_attempts: Maximum number of recovery attempts
            
        Returns:
            Decorated function
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    # Get function name and arguments for context
                    func_name = func.__name__
                    # Safely convert args to string representation
                    args_str = str(args) if args else ""
                    # Only include non-sensitive kwargs
                    safe_kwargs = {k: v for k, v in kwargs.items() 
                                 if k not in ['api_key', 'api_secret', 'password', 'token']}
                    
                    context = {
                        "function": func_name,
                        "args": args_str,
                        "kwargs": str(safe_kwargs)
                    }
                    
                    # Handle the error
                    error_message = f"Error in {func_name}: {str(e)}"
                    result = self.handle_error(
                        error_type=error_type,
                        error_message=error_message,
                        exception=e,
                        severity=severity,
                        category=category,
                        context=context,
                        notify=notify,
                        recovery_func=recovery_func,
                        max_recovery_attempts=max_recovery_attempts
                    )
                    
                    # Re-raise if configured to do so
                    if self.config.get('reraise_exceptions', False):
                        raise
                    
                    # Return None or a default value
                    return None
            return wrapper
        return decorator


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Example configuration
    config = {
        "error_log_path": "data/error_log.json",
        "max_log_size": 1000,
        "reraise_exceptions": False,
        "recovery_cooldown_minutes": {
            "api_timeout": 5,
            "network_error": 10,
            "data_processing_error": 15
        },
        "notification_settings": {
            "severity": {
                "critical": True,
                "high": True,
                "medium": True,
                "low": False,
                "info": False
            },
            "error_types": {
                "api_timeout": True,
                "network_error": True,
                "data_processing_error": True
            },
            "max_notifications_per_hour": {
                "api_timeout": 3,
                "network_error": 3,
                "data_processing_error": 5
            }
        }
    }
    
    # Create mock notification manager
    class MockNotificationManager:
        def send_error_notification(self, error_type, error_message, details=None):
            print(f"MOCK NOTIFICATION: {error_type} - {error_message}")
            if details:
                print(f"Details: {details}")
            return {"success": True}
    
    # Create error handler
    error_handler = ErrorHandler(config=config, notification_manager=MockNotificationManager())
    
    # Example recovery function
    def example_recovery():
        print("Attempting recovery...")
        return {"success": True, "message": "Recovery successful"}
    
    # Example error handling
    try:
        # Simulate an error
        result = 10 / 0
    except Exception as e:
        error_handler.handle_error(
            error_type="division_by_zero",
            error_message="Attempted to divide by zero",
            exception=e,
            severity=ErrorHandler.SEVERITY_HIGH,
            category=ErrorHandler.CATEGORY_SYSTEM,
            context={"operation": "division", "numerator": 10, "denominator": 0},
            recovery_func=example_recovery
        )
    
    # Example using decorator
    @error_handler.error_decorator(
        error_type="api_error",
        severity=ErrorHandler.SEVERITY_MEDIUM,
        category=ErrorHandler.CATEGORY_API
    )
    def api_call(endpoint, params):
        # Simulate API error
        if endpoint == "broken":
            raise ConnectionError("API connection failed")
        return {"success": True, "data": "example data"}
    
    # Test decorated function
    api_call("broken", {"param": "value"})
    
    # Get error summary
    summary = error_handler.get_error_summary(hours=24)
    print(f"Error summary: {json.dumps(summary, indent=2)}")
