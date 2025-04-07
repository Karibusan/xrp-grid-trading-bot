#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Survivability Module for XRP Trading Bot
Version: 1.0.0
Description: Module that implements resilience mechanisms to ensure
the trading bot can continue to function effectively even when
certain information sources or functionalities are compromised.
"""

import numpy as np
import pandas as pd
import time
import json
import os
import logging
import shutil
import socket
import requests
from datetime import datetime, timedelta
import krakenex
from pykrakenapi import KrakenAPI

class SurvivabilityManager:
    """
    A module that implements resilience mechanisms to ensure
    the trading bot can continue to function effectively even when
    certain information sources or functionalities are compromised.
    """
    
    def __init__(self, config_path=None, api_key=None, api_secret=None):
        """
        Initialize the Survivability Manager module.
        
        Args:
            config_path (str): Path to configuration file
            api_key (str): Kraken API key
            api_secret (str): Kraken API secret
        """
        # Default configuration
        self.default_config = {
            "enabled": True,
            "trading_pair": "XRPGBP",
            "health_check_interval_minutes": 15,
            "backup_interval_hours": 24,
            "backup_retention_days": 7,
            "emergency_shutdown_threshold": 0.15,
            "fallback_apis": ["kraken", "binance", "coinbase"],
            "log_file": "survivability_log.txt",
            "data_file": "survivability_data.json",
            "backup_dir": "backups"
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
            
        # Create backup directory
        self.backup_dir = self.config["backup_dir"]
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
            
        self.system_status = {
            "timestamp": datetime.now().isoformat(),
            "status": "initializing",
            "components": {},
            "last_backup": None,
            "emergency_mode": False
        }
        
        self.last_health_check = None
        self.last_backup = None
        
        self._log_info("Survivability Manager initialized")
    
    def _log_info(self, message):
        """Log informational message"""
        logging.info(message)
        
    def _log_error(self, message):
        """Log error message"""
        logging.error(message)
        
    def _log_warning(self, message):
        """Log warning message"""
        logging.warning(message)
    
    def check_system_health(self):
        """
        Perform a comprehensive system health check
        
        Returns:
            bool: System health status
        """
        try:
            # Update last health check time
            self.last_health_check = datetime.now()
            
            # Reset components status
            self.system_status["components"] = {}
            
            # Check internet connectivity
            internet_status = self._check_internet_connectivity()
            self.system_status["components"]["internet"] = {
                "status": "online" if internet_status else "offline",
                "details": "Connected to the internet" if internet_status else "No internet connection"
            }
            
            # Check API connectivity
            api_status = self._check_api_connectivity()
            self.system_status["components"]["api"] = {
                "status": "online" if api_status else "offline",
                "details": "Connected to Kraken API" if api_status else "Cannot connect to Kraken API"
            }
            
            # Check disk space
            disk_status, disk_details = self._check_disk_space()
            self.system_status["components"]["disk"] = {
                "status": "ok" if disk_status else "low",
                "details": disk_details
            }
            
            # Check data integrity
            data_status, data_details = self._check_data_integrity()
            self.system_status["components"]["data"] = {
                "status": "ok" if data_status else "corrupted",
                "details": data_details
            }
            
            # Determine overall system status
            if all(comp["status"] in ["online", "ok"] for comp in self.system_status["components"].values()):
                self.system_status["status"] = "healthy"
            elif any(comp["status"] in ["offline", "corrupted"] for comp in self.system_status["components"].values()):
                self.system_status["status"] = "critical"
            else:
                self.system_status["status"] = "degraded"
            
            # Update timestamp
            self.system_status["timestamp"] = datetime.now().isoformat()
            
            # Save system status
            try:
                with open(self.config["data_file"], 'w') as f:
                    json.dump(self.system_status, f, indent=2)
            except Exception as e:
                self._log_error(f"Error saving system status: {str(e)}")
            
            self._log_info(f"System health check completed: {self.system_status['status']}")
            return self.system_status["status"] == "healthy"
            
        except Exception as e:
            self._log_error(f"Error checking system health: {str(e)}")
            self.system_status["status"] = "unknown"
            return False
    
    def _check_internet_connectivity(self):
        """
        Check internet connectivity
        
        Returns:
            bool: Internet connectivity status
        """
        try:
            # Try to connect to a reliable server
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except OSError:
            return False
    
    def _check_api_connectivity(self):
        """
        Check API connectivity
        
        Returns:
            bool: API connectivity status
        """
        if not self.kraken:
            return False
            
        try:
            # Try to get server time
            self.kraken.get_server_time()
            return True
        except Exception:
            return False
    
    def _check_disk_space(self):
        """
        Check available disk space
        
        Returns:
            tuple: (status, details)
        """
        try:
            # Get disk usage statistics
            total, used, free = shutil.disk_usage("/")
            
            # Convert to GB
            total_gb = total / (1024 ** 3)
            free_gb = free / (1024 ** 3)
            used_percent = (used / total) * 100
            
            # Check if disk space is low
            if free_gb < 1.0 or used_percent > 95:
                return False, f"Low disk space: {free_gb:.2f} GB free ({used_percent:.1f}% used)"
            else:
                return True, f"Sufficient disk space: {free_gb:.2f} GB free ({used_percent:.1f}% used)"
        except Exception as e:
            return False, f"Error checking disk space: {str(e)}"
    
    def _check_data_integrity(self):
        """
        Check data integrity
        
        Returns:
            tuple: (status, details)
        """
        try:
            # Check if data directory exists
            if not os.path.exists(self.data_dir):
                return False, "Data directory does not exist"
                
            # Check if backup directory exists
            if not os.path.exists(self.backup_dir):
                return False, "Backup directory does not exist"
                
            # Check if log file is writable
            try:
                with open(self.config["log_file"], 'a') as f:
                    f.write("")
            except Exception:
                return False, "Log file is not writable"
            
            return True, "Data integrity check passed"
        except Exception as e:
            return False, f"Error checking data integrity: {str(e)}"
    
    def create_system_backup(self):
        """
        Create a backup of system data
        
        Returns:
            bool: Success status
        """
        try:
            # Update last backup time
            self.last_backup = datetime.now()
            self.system_status["last_backup"] = self.last_backup.isoformat()
            
            # Create backup directory with timestamp
            timestamp = self.last_backup.strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(self.backup_dir, f"backup_{timestamp}")
            os.makedirs(backup_path, exist_ok=True)
            
            # Backup configuration
            config_backup_path = os.path.join(backup_path, "config")
            os.makedirs(config_backup_path, exist_ok=True)
            
            # Find all JSON files in data directory
            data_files = [f for f in os.listdir(self.data_dir) if f.endswith('.json')]
            
            # Copy data files to backup
            for file in data_files:
                src = os.path.join(self.data_dir, file)
                dst = os.path.join(config_backup_path, file)
                shutil.copy2(src, dst)
            
            # Backup logs
            log_backup_path = os.path.join(backup_path, "logs")
            os.makedirs(log_backup_path, exist_ok=True)
            
            # Copy log file to backup
            if os.path.exists(self.config["log_file"]):
                shutil.copy2(self.config["log_file"], os.path.join(log_backup_path, "survivability_log.txt"))
            
            # Create backup info file
            backup_info = {
                "timestamp": timestamp,
                "created_at": self.last_backup.isoformat(),
                "system_status": self.system_status,
                "files_backed_up": data_files + ["survivability_log.txt"]
            }
            
            with open(os.path.join(backup_path, "backup_info.json"), 'w') as f:
                json.dump(backup_info, f, indent=2)
            
            self._log_info(f"System backup created at {backup_path}")
            
            # Clean up old backups
            self._cleanup_old_backups()
            
            return True
            
        except Exception as e:
            self._log_error(f"Error creating system backup: {str(e)}")
            return False
    
    def _cleanup_old_backups(self):
        """
        Clean up old backups based on retention policy
        
        Returns:
            bool: Success status
        """
        try:
            # Get all backup directories
            backup_dirs = [d for d in os.listdir(self.backup_dir) if d.startswith("backup_")]
            
            # Sort by timestamp (newest first)
            backup_dirs.sort(reverse=True)
            
            # Keep only the specified number of backups
            retention_days = self.config["backup_retention_days"]
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            for backup_dir in backup_dirs:
                try:
                    # Extract timestamp from directory name
                    timestamp_str = backup_dir.replace("backup_", "")
                    timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                    
                    # Check if backup is older than retention period
                    if timestamp < cutoff_date:
                        backup_path = os.path.join(self.backup_dir, backup_dir)
                        shutil.rmtree(backup_path)
                        self._log_info(f"Removed old backup: {backup_dir}")
                except Exception as e:
                    self._log_warning(f"Error processing backup directory {backup_dir}: {str(e)}")
            
            return True
            
        except Exception as e:
            self._log_error(f"Error cleaning up old backups: {str(e)}")
            return False
    
    def restore_from_backup(self, backup_timestamp=None):
        """
        Restore system from backup
        
        Args:
            backup_timestamp (str): Timestamp of backup to restore (format: YYYYMMDD_HHMMSS)
                                   If None, restore from latest backup
        
        Returns:
            bool: Success status
        """
        try:
            # Get all backup directories
            backup_dirs = [d for d in os.listdir(self.backup_dir) if d.startswith("backup_")]
            
            if not backup_dirs:
                self._log_error("No backups found")
                return False
            
            # Sort by timestamp (newest first)
            backup_dirs.sort(reverse=True)
            
            # Select backup to restore
            if backup_timestamp:
                backup_dir = f"backup_{backup_timestamp}"
                if backup_dir not in backup_dirs:
                    self._log_error(f"Backup {backup_timestamp} not found")
                    return False
            else:
                backup_dir = backup_dirs[0]  # Latest backup
            
            backup_path = os.path.join(self.backup_dir, backup_dir)
            
            # Check if backup exists
            if not os.path.exists(backup_path):
                self._log_error(f"Backup directory {backup_path} not found")
                return False
            
            # Create backup of current state before restoring
            self.create_system_backup()
            
            # Restore configuration
            config_backup_path = os.path.join(backup_path, "config")
            if os.path.exists(config_backup_path):
                # Copy all JSON files from backup to data directory
                for file in os.listdir(config_backup_path):
                    if file.endswith('.json'):
                        src = os.path.join(config_backup_path, file)
                        dst = os.path.join(self.data_dir, file)
                        shutil.copy2(src, dst)
            
            self._log_info(f"System restored from backup {backup_dir}")
            return True
            
        except Exception as e:
            self._log_error(f"Error restoring from backup: {str(e)}")
            return False
    
    def get_fallback_price(self):
        """
        Get price from fallback APIs when primary API is unavailable
        
        Returns:
            float: Price or None if all APIs fail
        """
        if not self.system_status["components"].get("api", {}).get("status") == "offline":
            # Primary API is online, no need for fallback
            return None
            
        try:
            pair = self.config["trading_pair"]
            
            # Try fallback APIs
            for api in self.config["fallback_apis"]:
                if api == "kraken" and self.kraken:
                    # Already tried primary API
                    continue
                    
                try:
                    if api == "binance":
                        # Convert pair format (e.g., XRPGBP -> XRPGBP)
                        binance_pair = pair.replace("/", "")
                        url = f"https://api.binance.com/api/v3/ticker/price?symbol={binance_pair}"
                        response = requests.get(url, timeout=5)
                        data = response.json()
                        price = float(data["price"])
                        self._log_info(f"Got price from Binance: {price}")
                        return price
                        
                    elif api == "coinbase":
                        # Convert pair format (e.g., XRPGBP -> XRP-GBP)
                        base = pair[:3]
                        quote = pair[3:]
                        coinbase_pair = f"{base}-{quote}"
                        url = f"https://api.coinbase.com/v2/prices/{coinbase_pair}/spot"
                        response = requests.get(url, timeout=5)
                        data = response.json()
                        price = float(data["data"]["amount"])
                        self._log_info(f"Got price from Coinbase: {price}")
                        return price
                        
                except Exception as e:
                    self._log_warning(f"Error getting price from {api}: {str(e)}")
                    continue
            
            self._log_error("All fallback APIs failed")
            return None
            
        except Exception as e:
            self._log_error(f"Error getting fallback price: {str(e)}")
            return None
    
    def check_emergency_conditions(self, current_price=None, portfolio_value=None):
        """
        Check for emergency conditions that require immediate action
        
        Args:
            current_price (float): Current price of trading pair
            portfolio_value (float): Current portfolio value
            
        Returns:
            bool: Emergency mode status
        """
        try:
            # Check system health
            if self.system_status["status"] == "critical":
                self._log_warning("Emergency mode activated: Critical system status")
                self.system_status["emergency_mode"] = True
                return True
            
            # Check for market crash
            if current_price is not None and portfolio_value is not None:
                # Calculate portfolio change
                if "last_portfolio_value" in self.system_status:
                    last_value = self.system_status["last_portfolio_value"]
                    change = (portfolio_value - last_value) / last_value
                    
                    # Check if change exceeds emergency threshold
                    if change < -self.config["emergency_shutdown_threshold"]:
                        self._log_warning(f"Emergency mode activated: Portfolio value dropped by {-change*100:.2f}%")
                        self.system_status["emergency_mode"] = True
                        return True
                
                # Update last portfolio value
                self.system_status["last_portfolio_value"] = portfolio_value
            
            # No emergency conditions detected
            self.system_status["emergency_mode"] = False
            return False
            
        except Exception as e:
            self._log_error(f"Error checking emergency conditions: {str(e)}")
            return False
    
    def get_emergency_actions(self):
        """
        Get recommended actions for emergency mode
        
        Returns:
            dict: Emergency actions
        """
        if not self.system_status["emergency_mode"]:
            return {"emergency_mode": False}
            
        try:
            # Determine cause of emergency
            cause = "unknown"
            
            if self.system_status["components"].get("internet", {}).get("status") == "offline":
                cause = "internet_connectivity"
            elif self.system_status["components"].get("api", {}).get("status") == "offline":
                cause = "api_connectivity"
            elif self.system_status["components"].get("data", {}).get("status") == "corrupted":
                cause = "data_corruption"
            elif "last_portfolio_value" in self.system_status:
                cause = "market_crash"
            
            # Generate actions based on cause
            actions = {
                "emergency_mode": True,
                "cause": cause,
                "timestamp": datetime.now().isoformat(),
                "actions": []
            }
            
            if cause == "internet_connectivity":
                actions["actions"] = [
                    "Pause all trading activities",
                    "Wait for internet connectivity to be restored",
                    "Once restored, perform a full system health check"
                ]
            elif cause == "api_connectivity":
                actions["actions"] = [
                    "Switch to fallback APIs for price data",
                    "Reduce trading frequency",
                    "Monitor API status and resume normal operations when available"
                ]
            elif cause == "data_corruption":
                actions["actions"] = [
                    "Pause all trading activities",
                    "Restore from latest backup",
                    "Perform a full system health check before resuming"
                ]
            elif cause == "market_crash":
                actions["actions"] = [
                    "Pause opening new positions",
                    "Set tighter stop-loss levels for existing positions",
                    "Increase grid spacing to reduce trading frequency",
                    "Wait for market stabilization before resuming normal operations"
                ]
            else:
                actions["actions"] = [
                    "Pause all trading activities",
                    "Perform a full system health check",
                    "Restore from latest backup if necessary",
                    "Resume operations only after manual verification"
                ]
            
            return actions
            
        except Exception as e:
            self._log_error(f"Error getting emergency actions: {str(e)}")
            return {"emergency_mode": True, "error": str(e)}
    
    def run_maintenance(self):
        """
        Run routine maintenance tasks
        
        Returns:
            dict: Maintenance results
        """
        try:
            maintenance_results = {
                "timestamp": datetime.now().isoformat(),
                "tasks": {}
            }
            
            # Check if backup is needed
            backup_needed = False
            if self.last_backup is None:
                backup_needed = True
            else:
                time_since_backup = (datetime.now() - self.last_backup).total_seconds() / 3600
                if time_since_backup >= self.config["backup_interval_hours"]:
                    backup_needed = True
            
            # Create backup if needed
            if backup_needed:
                backup_success = self.create_system_backup()
                maintenance_results["tasks"]["backup"] = {
                    "status": "completed" if backup_success else "failed",
                    "details": "Backup created successfully" if backup_success else "Failed to create backup"
                }
            else:
                maintenance_results["tasks"]["backup"] = {
                    "status": "skipped",
                    "details": f"Last backup was {(datetime.now() - self.last_backup).total_seconds() / 3600:.1f} hours ago"
                }
            
            # Clean up logs
            try:
                # Check log file size
                log_size = os.path.getsize(self.config["log_file"]) / (1024 * 1024)  # Size in MB
                
                if log_size > 10:  # If log file is larger than 10 MB
                    # Create a backup of the log file
                    log_backup = f"{self.config['log_file']}.{datetime.now().strftime('%Y%m%d')}"
                    shutil.copy2(self.config["log_file"], log_backup)
                    
                    # Truncate the log file
                    with open(self.config["log_file"], 'w') as f:
                        f.write(f"Log file truncated at {datetime.now().isoformat()}\n")
                    
                    maintenance_results["tasks"]["log_cleanup"] = {
                        "status": "completed",
                        "details": f"Log file truncated (was {log_size:.2f} MB), backup created at {log_backup}"
                    }
                else:
                    maintenance_results["tasks"]["log_cleanup"] = {
                        "status": "skipped",
                        "details": f"Log file size is {log_size:.2f} MB, below threshold"
                    }
            except Exception as e:
                maintenance_results["tasks"]["log_cleanup"] = {
                    "status": "failed",
                    "details": f"Error cleaning up logs: {str(e)}"
                }
            
            self._log_info("Maintenance tasks completed")
            return maintenance_results
            
        except Exception as e:
            self._log_error(f"Error running maintenance: {str(e)}")
            return {"error": str(e)}
    
    def run_survivability_check(self, current_price=None, portfolio_value=None):
        """
        Run a complete survivability check
        
        Args:
            current_price (float): Current price of trading pair
            portfolio_value (float): Current portfolio value
            
        Returns:
            dict: Survivability check results
        """
        if not self.config["enabled"]:
            self._log_info("Survivability Manager is disabled")
            return {"enabled": False}
            
        self._log_info("Starting survivability check")
        
        # Check if it's time to run health check
        current_time = datetime.now()
        run_health_check = True
        
        if self.last_health_check:
            time_diff = (current_time - self.last_health_check).total_seconds() / 60
            if time_diff < self.config["health_check_interval_minutes"]:
                self._log_info(f"Skipping health check, last check was {time_diff:.1f} minutes ago")
                run_health_check = False
        
        # Run health check if needed
        if run_health_check:
            self.check_system_health()
        
        # Check for emergency conditions
        emergency_mode = self.check_emergency_conditions(current_price, portfolio_value)
        
        # Get emergency actions if in emergency mode
        emergency_actions = self.get_emergency_actions() if emergency_mode else None
        
        # Run maintenance tasks
        maintenance_results = self.run_maintenance()
        
        # Get fallback price if API is offline
        fallback_price = self.get_fallback_price()
        
        self._log_info("Survivability check completed")
        
        return {
            "timestamp": current_time.isoformat(),
            "system_status": self.system_status,
            "emergency_mode": emergency_mode,
            "emergency_actions": emergency_actions,
            "maintenance_results": maintenance_results,
            "fallback_price": fallback_price,
            "next_health_check_in_minutes": self.config["health_check_interval_minutes"] if run_health_check else 
                self.config["health_check_interval_minutes"] - (current_time - self.last_health_check).total_seconds() / 60
        }

# Example usage
if __name__ == "__main__":
    # Create data directory if it doesn't exist
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        
    # Create backup directory if it doesn't exist
    backup_dir = "backups"
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        
    # Configuration
    config = {
        "enabled": True,
        "trading_pair": "XRPGBP",
        "health_check_interval_minutes": 15,
        "backup_interval_hours": 24,
        "backup_retention_days": 7,
        "emergency_shutdown_threshold": 0.15,
        "fallback_apis": ["kraken", "binance", "coinbase"],
        "log_file": f"{data_dir}/survivability_log.txt",
        "data_file": f"{data_dir}/survivability_data.json",
        "backup_dir": backup_dir
    }
    
    # Save config
    with open(f"{data_dir}/survivability_config.json", 'w') as f:
        json.dump(config, f, indent=2)
        
    print("Survivability Manager module created.")
    print("To use this module with your XRP Trading Bot:")
    print("1. Place this file in the same directory as your main bot script")
    print("2. Import the module in your main script:")
    print("   from survivability_module import SurvivabilityManager")
    print("3. Initialize the manager with your API keys:")
    print("   manager = SurvivabilityManager(config_path='data/survivability_config.json', api_key=YOUR_API_KEY, api_secret=YOUR_API_SECRET)")
    print("4. Run the survivability check periodically:")
    print("   results = manager.run_survivability_check(current_price=0.3955, portfolio_value=1000.0)")
    print("5. Take appropriate actions based on the results, especially in emergency mode")
