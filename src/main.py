#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main entry point for XRP Trading Bot
Version: 3.0.2
"""

import os
import sys
import json
import logging
import time
from datetime import datetime

# Add src directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.enhanced_trading_system import EnhancedTradingSystem
from src.notification_manager import NotificationManager
from src.error_handler import ErrorHandler
from src.api_client import APIClient
from src.config_manager import ConfigManager

def setup_logging():
    """Setup logging configuration"""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    log_file = os.path.join(log_dir, f"xrp_bot_{datetime.now().strftime('%Y%m%d')}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger("xrp_bot")

def main():
    """Main entry point for the XRP Trading Bot"""
    logger = setup_logging()
    logger.info("Starting XRP Trading Bot v3.0.2")
    
    try:
        # Initialize configuration manager
        config_manager = ConfigManager("config/config.json")
        
        # Initialize error handler
        error_handler = ErrorHandler("config/error_handler_config.json")
        
        # Initialize notification manager
        notification_manager = NotificationManager("config/notification_config.json", error_handler)
        
        # Send startup notification
        notification_manager.send_status_notification(
            "XRP Trading Bot Started",
            "Version 3.0.2 initialized successfully"
        )
        
        # Initialize API client
        api_client = APIClient("config/api_client_config.json", error_handler)
        
        # Initialize trading system
        trading_system = EnhancedTradingSystem(
            config_manager=config_manager,
            api_client=api_client,
            notification_manager=notification_manager,
            error_handler=error_handler
        )
        
        # Start trading
        trading_system.start()
        
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        if 'notification_manager' in locals():
            notification_manager.send_error_notification(
                "Fatal Error",
                f"Bot crashed with error: {str(e)}",
                "critical"
            )
        sys.exit(1)

if __name__ == "__main__":
    main()
