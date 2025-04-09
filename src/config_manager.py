#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuration Manager for XRP Trading Bot v3.0
Provides centralized configuration loading, validation, and management.
"""

import os
import sys
import json
import logging
import jsonschema
from typing import Dict, Any, Optional, List, Union
from datetime import datetime

class ConfigManager:
    """
    Centralized configuration management for the XRP Trading Bot.
    Handles loading, validation, and access to configuration settings.
    """
    
    def __init__(self, config_dir: str = "config", 
                main_config_file: str = "config.json",
                error_handler=None):
        """
        Initialize the configuration manager.
        
        Args:
            config_dir: Directory containing configuration files
            main_config_file: Main configuration file name
            error_handler: ErrorHandler instance for handling configuration errors
        """
        self.config_dir = config_dir
        self.main_config_file = main_config_file
        self.error_handler = error_handler
        self.logger = logging.getLogger('config_manager')
        
        # Initialize configuration storage
        self.config = {}
        self.module_configs = {}
        self.config_schemas = {}
        
        # Load configuration schemas
        self._load_schemas()
        
        # Load main configuration
        self._load_main_config()
    
    def _load_schemas(self):
        """Load JSON schemas for configuration validation."""
        schema_dir = os.path.join(self.config_dir, "schemas")
        if not os.path.exists(schema_dir):
            self.logger.warning(f"Schema directory not found: {schema_dir}")
            return
            
        try:
            for filename in os.listdir(schema_dir):
                if filename.endswith(".schema.json"):
                    schema_path = os.path.join(schema_dir, filename)
                    schema_name = filename.replace(".schema.json", "")
                    
                    with open(schema_path, 'r') as f:
                        self.config_schemas[schema_name] = json.load(f)
                        
                    self.logger.debug(f"Loaded schema: {schema_name}")
        except Exception as e:
            self.logger.error(f"Error loading schemas: {e}")
            if self.error_handler:
                self.error_handler.handle_error(
                    error_type="config_schema_load_error",
                    error_message=f"Failed to load configuration schemas: {e}",
                    exception=e,
                    severity="high",
                    category="config"
                )
    
    def _load_main_config(self):
        """Load main configuration file."""
        config_path = os.path.join(self.config_dir, self.main_config_file)
        
        if not os.path.exists(config_path):
            error_msg = f"Main configuration file not found: {config_path}"
            self.logger.error(error_msg)
            if self.error_handler:
                self.error_handler.handle_error(
                    error_type="config_file_not_found",
                    error_message=error_msg,
                    severity="critical",
                    category="config"
                )
            return
            
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
                
            # Validate main configuration
            self._validate_config("main", self.config)
            
            self.logger.info(f"Loaded main configuration from {config_path}")
            
            # Load module configurations
            self._load_module_configs()
            
        except Exception as e:
            error_msg = f"Failed to load main configuration: {e}"
            self.logger.error(error_msg)
            if self.error_handler:
                self.error_handler.handle_error(
                    error_type="config_load_error",
                    error_message=error_msg,
                    exception=e,
                    severity="critical",
                    category="config"
                )
    
    def _load_module_configs(self):
        """Load module-specific configuration files."""
        modules = self.config.get("modules", {})
        
        for module_name, module_config in modules.items():
            if not module_config.get("enabled", False):
                continue
                
            config_file = module_config.get("config_file")
            if not config_file:
                continue
                
            # Handle both absolute and relative paths
            if not os.path.isabs(config_file):
                config_file = os.path.join(self.config_dir, config_file)
                
            if not os.path.exists(config_file):
                self.logger.warning(f"Module configuration file not found: {config_file}")
                continue
                
            try:
                with open(config_file, 'r') as f:
                    module_conf = json.load(f)
                    
                # Validate module configuration
                self._validate_config(module_name, module_conf)
                
                self.module_configs[module_name] = module_conf
                self.logger.debug(f"Loaded configuration for module: {module_name}")
                
            except Exception as e:
                error_msg = f"Failed to load configuration for module {module_name}: {e}"
                self.logger.error(error_msg)
                if self.error_handler:
                    self.error_handler.handle_error(
                        error_type="module_config_load_error",
                        error_message=error_msg,
                        exception=e,
                        severity="high",
                        category="config",
                        context={"module": module_name}
                    )
    
    def _validate_config(self, config_name: str, config_data: Dict[str, Any]) -> bool:
        """
        Validate configuration against schema.
        
        Args:
            config_name: Name of configuration (for schema lookup)
            config_data: Configuration data to validate
            
        Returns:
            True if validation successful, False otherwise
        """
        if config_name not in self.config_schemas:
            self.logger.warning(f"No schema found for {config_name}, skipping validation")
            return True
            
        schema = self.config_schemas[config_name]
        
        try:
            jsonschema.validate(instance=config_data, schema=schema)
            self.logger.debug(f"Configuration {config_name} validated successfully")
            return True
        except jsonschema.exceptions.ValidationError as e:
            error_msg = f"Configuration validation failed for {config_name}: {e}"
            self.logger.error(error_msg)
            if self.error_handler:
                self.error_handler.handle_error(
                    error_type="config_validation_error",
                    error_message=error_msg,
                    exception=e,
                    severity="high",
                    category="config",
                    context={"config_name": config_name}
                )
            return False
    
    def get_config(self, key: Optional[str] = None, default: Any = None) -> Any:
        """
        Get configuration value from main configuration.
        
        Args:
            key: Configuration key (dot notation supported for nested access)
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        if key is None:
            return self.config
            
        # Handle nested keys with dot notation
        if '.' in key:
            parts = key.split('.')
            current = self.config
            
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return default
                    
            return current
        else:
            return self.config.get(key, default)
    
    def get_module_config(self, module_name: str, key: Optional[str] = None, default: Any = None) -> Any:
        """
        Get configuration value from module configuration.
        
        Args:
            module_name: Module name
            key: Configuration key (dot notation supported for nested access)
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        if module_name not in self.module_configs:
            return default
            
        if key is None:
            return self.module_configs[module_name]
            
        # Handle nested keys with dot notation
        if '.' in key:
            parts = key.split('.')
            current = self.module_configs[module_name]
            
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return default
                    
            return current
        else:
            return self.module_configs[module_name].get(key, default)
    
    def is_module_enabled(self, module_name: str) -> bool:
        """
        Check if a module is enabled.
        
        Args:
            module_name: Module name
            
        Returns:
            True if module is enabled, False otherwise
        """
        modules = self.config.get("modules", {})
        module_config = modules.get(module_name, {})
        return module_config.get("enabled", False)
    
    def save_config(self, config_data: Dict[str, Any], config_file: Optional[str] = None) -> bool:
        """
        Save configuration to file.
        
        Args:
            config_data: Configuration data to save
            config_file: Configuration file path (uses main config file if None)
            
        Returns:
            True if save successful, False otherwise
        """
        if config_file is None:
            config_file = os.path.join(self.config_dir, self.main_config_file)
            
        try:
            # Create backup of existing file
            if os.path.exists(config_file):
                backup_file = f"{config_file}.{datetime.now().strftime('%Y%m%d%H%M%S')}.bak"
                with open(config_file, 'r') as src, open(backup_file, 'w') as dst:
                    dst.write(src.read())
                self.logger.debug(f"Created backup of {config_file} at {backup_file}")
                
            # Write new configuration
            with open(config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
                
            self.logger.info(f"Saved configuration to {config_file}")
            return True
            
        except Exception as e:
            error_msg = f"Failed to save configuration to {config_file}: {e}"
            self.logger.error(error_msg)
            if self.error_handler:
                self.error_handler.handle_error(
                    error_type="config_save_error",
                    error_message=error_msg,
                    exception=e,
                    severity="high",
                    category="config"
                )
            return False
    
    def save_module_config(self, module_name: str, config_data: Dict[str, Any]) -> bool:
        """
        Save module configuration to file.
        
        Args:
            module_name: Module name
            config_data: Configuration data to save
            
        Returns:
            True if save successful, False otherwise
        """
        modules = self.config.get("modules", {})
        module_config = modules.get(module_name, {})
        config_file = module_config.get("config_file")
        
        if not config_file:
            error_msg = f"No configuration file specified for module {module_name}"
            self.logger.error(error_msg)
            if self.error_handler:
                self.error_handler.handle_error(
                    error_type="module_config_save_error",
                    error_message=error_msg,
                    severity="medium",
                    category="config",
                    context={"module": module_name}
                )
            return False
            
        # Handle both absolute and relative paths
        if not os.path.isabs(config_file):
            config_file = os.path.join(self.config_dir, config_file)
            
        return self.save_config(config_data, config_file)
    
    def update_config(self, updates: Dict[str, Any], save: bool = True) -> bool:
        """
        Update main configuration with new values.
        
        Args:
            updates: Dictionary of updates to apply
            save: Whether to save updated configuration to file
            
        Returns:
            True if update successful, False otherwise
        """
        # Helper function for recursive dictionary update
        def update_dict(target, source):
            for key, value in source.items():
                if isinstance(value, dict) and key in target and isinstance(target[key], dict):
                    update_dict(target[key], value)
                else:
                    target[key] = value
        
        try:
            # Apply updates
            update_dict(self.config, updates)
            
            # Validate updated configuration
            if not self._validate_config("main", self.config):
                return False
                
            # Save if requested
            if save:
                return self.save_config(self.config)
                
            return True
            
        except Exception as e:
            error_msg = f"Failed to update configuration: {e}"
            self.logger.error(error_msg)
            if self.error_handler:
                self.error_handler.handle_error(
                    error_type="config_update_error",
                    error_message=error_msg,
                    exception=e,
                    severity="medium",
                    category="config"
                )
            return False
    
    def update_module_config(self, module_name: str, updates: Dict[str, Any], save: bool = True) -> bool:
        """
        Update module configuration with new values.
        
        Args:
            module_name: Module name
            updates: Dictionary of updates to apply
            save: Whether to save updated configuration to file
            
        Returns:
            True if update successful, False otherwise
        """
        if module_name not in self.module_configs:
            error_msg = f"No configuration found for module {module_name}"
            self.logger.error(error_msg)
            if self.error_handler:
                self.error_handler.handle_error(
                    error_type="module_config_update_error",
                    error_message=error_msg,
                    severity="medium",
                    category="config",
                    context={"module": module_name}
                )
            return False
            
        # Helper function for recursive dictionary update
        def update_dict(target, source):
            for key, value in source.items():
                if isinstance(value, dict) and key in target and isinstance(target[key], dict):
                    update_dict(target[key], value)
                else:
                    target[key] = value
        
        try:
            # Apply updates
            update_dict(self.module_configs[module_name], updates)
            
            # Validate updated configuration
            if not self._validate_config(module_name, self.module_configs[module_name]):
                return False
                
            # Save if requested
            if save:
                return self.save_module_config(module_name, self.module_configs[module_name])
                
            return True
            
        except Exception as e:
            error_msg = f"Failed to update configuration for module {module_name}: {e}"
            self.logger.error(error_msg)
            if self.error_handler:
                self.error_handler.handle_error(
                    error_type="module_config_update_error",
                    error_message=error_msg,
                    exception=e,
                    severity="medium",
                    category="config",
                    context={"module": module_name}
                )
            return False
    
    def reload_config(self) -> bool:
        """
        Reload configuration from files.
        
        Returns:
            True if reload successful, False otherwise
        """
        try:
            # Clear current configurations
            self.config = {}
            self.module_configs = {}
            
            # Reload main configuration
            self._load_main_config()
            
            return True
            
        except Exception as e:
            error_msg = f"Failed to reload configuration: {e}"
            self.logger.error(error_msg)
            if self.error_handler:
                self.error_handler.handle_error(
                    error_type="config_reload_error",
                    error_message=error_msg,
                    exception=e,
                    severity="high",
                    category="config"
                )
            return False
    
    def create_default_config(self, config_template: Dict[str, Any], 
                            config_file: Optional[str] = None) -> bool:
        """
        Create default configuration file if it doesn't exist.
        
        Args:
            config_template: Template for default configuration
            config_file: Configuration file path (uses main config file if None)
            
        Returns:
            True if creation successful, False otherwise
        """
        if config_file is None:
            config_file = os.path.join(self.config_dir, self.main_config_file)
            
        # Don't overwrite existing file
        if os.path.exists(config_file):
            self.logger.info(f"Configuration file already exists: {config_file}")
            return True
            
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
            
        try:
            with open(config_file, 'w') as f:
                json.dump(config_template, f, indent=2)
                
            self.logger.info(f"Created default configuration at {config_file}")
            return True
            
        except Exception as e:
            error_msg = f"Failed to create default configuration at {config_file}: {e}"
            self.logger.error(error_msg)
            if self.error_handler:
                self.error_handler.handle_error(
                    error_type="config_create_error",
                    error_message=error_msg,
                    exception=e,
                    severity="high",
                    category="config"
                )
            return False


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create config manager
    config_manager = ConfigManager(config_dir="config")
    
    # Example: Get configuration values
    api_key = config_manager.get_config("api_key", "")
    trading_pair = config_manager.get_config("trading_pair", "XRPGBP")
    
    print(f"API Key: {'*' * len(api_key) if api_key else 'Not set'}")
    print(f"Trading Pair: {trading_pair}")
    
    # Example: Check if module is enabled
    signal_collapse_enabled = config_manager.is_module_enabled("signal_collapse")
    print(f"Signal Collapse module enabled: {signal_collapse_enabled}")
    
    # Example: Get module configuration
    if signal_collapse_enabled:
        threshold = config_manager.get_module_config("signal_collapse", "threshold", 0.8)
        print(f"Signal Collapse threshold: {threshold}")
    
    # Example: Update configuration
    config_manager.update_config({"price_check_interval_minutes": 3}, save=True)
    
    # Example: Create default configuration
    default_config = {
        "trading_pair": "XRPGBP",
        "grid_range_percentage": 4.0,
        "grid_levels": 16,
        "total_allocation": 100.0,
        "price_check_interval_minutes": 5,
        "api_key": "",
        "api_secret": "",
        "modules": {
            "signal_collapse": {
                "enabled": True,
                "config_file": "signal_collapse_config.json"
            }
        }
    }
    
    config_manager.create_default_config(default_config, "config/default_config.json")
