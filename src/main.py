#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main entry point for XRP Trading Bot v3.0
"""

import os
import sys
import json
import time
import logging
import argparse
from datetime import datetime

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from src.notification_manager import NotificationManager
from src.error_handler import ErrorHandler
from src.api_client import KrakenClient
from src.config_manager import ConfigManager
from src.enhanced_trading_system import EnhancedTradingSystem

def setup_logging(log_dir="logs", debug=False):
    """
    Configure logging for the application.
    
    Args:
        log_dir: Directory to store log files
        debug: Whether to enable debug logging
    """
    # Create log directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)
    
    # Set log level
    log_level = logging.DEBUG if debug else logging.INFO
    
    # Create log file name with timestamp
    log_file = os.path.join(log_dir, f"xrp_bot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    # Create a logger for this module
    logger = logging.getLogger('main')
    logger.info(f"Logging initialized. Log file: {log_file}")
    
    return logger

def parse_arguments():
    """
    Parse command line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description='XRP Trading Bot v3.0')
    parser.add_argument('--config', help='Path to main configuration file', default='config/config.json')
    parser.add_argument('--debug', help='Enable debug logging', action='store_true')
    parser.add_argument('--test', help='Run in test mode (no real orders)', action='store_true')
    parser.add_argument('--reset', help='Reset bot state before starting', action='store_true')
    
    return parser.parse_args()

def main():
    """
    Main entry point for the application.
    """
    # Parse command line arguments
    args = parse_arguments()
    
    # Setup logging
    logger = setup_logging(debug=args.debug)
    logger.info("Starting XRP Trading Bot v3.0")
    
    try:
        # Initialize configuration manager
        config_manager = ConfigManager(
            config_dir=os.path.dirname(args.config),
            main_config_file=os.path.basename(args.config)
        )
        logger.info("Configuration manager initialized")
        
        # Check if configuration is valid
        if not config_manager.get_config():
            logger.error("Invalid or missing configuration. Exiting.")
            return 1
        
        # Initialize error handler
        error_handler_config_file = config_manager.get_config("error_handler.config_file")
        error_handler_config_path = os.path.join(os.path.dirname(args.config), error_handler_config_file)
        error_handler = ErrorHandler(config_path=error_handler_config_path)
        logger.info("Error handler initialized")
        
        # Update config manager with error handler
        config_manager.error_handler = error_handler
        
        # Initialize notification manager
        notification_config_file = config_manager.get_config("notification.config_file")
        notification_config_path = os.path.join(os.path.dirname(args.config), notification_config_file)
        notification_manager = NotificationManager(config_path=notification_config_path)
        logger.info("Notification manager initialized")
        
        # Initialize API client
        api_client_config_file = config_manager.get_config("api_client.config_file")
        api_client_config_path = os.path.join(os.path.dirname(args.config), api_client_config_file)
        api_client = KrakenClient(
            api_key=config_manager.get_config("api_key", ""),
            api_secret=config_manager.get_config("api_secret", ""),
            config_path=api_client_config_path,
            error_handler=error_handler
        )
        logger.info("API client initialized")
        
        # Initialize trading system
        trading_system = EnhancedTradingSystem(
            config_manager=config_manager,
            api_client=api_client,
            notification_manager=notification_manager,
            error_handler=error_handler
        )
        logger.info("Trading system initialized")
        
        # Send startup notification
        if notification_manager:
            notification_manager.send_notification(
                title="XRP Trading Bot v3.0 Started",
                message=f"Bot started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                level="status"
            )
        
        # Start trading system
        trading_system.start()
        logger.info("Trading system started")
        
        # Keep main thread alive
        try:
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received, shutting down...")
            trading_system.stop()
            
            # Send shutdown notification
            if notification_manager:
                notification_manager.send_notification(
                    title="XRP Trading Bot Stopped",
                    message=f"Bot stopped at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    level="status"
                )
        
        logger.info("XRP Trading Bot shutdown complete")
        return 0
        
    except Exception as e:
        logger.critical(f"Unhandled exception in main: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
