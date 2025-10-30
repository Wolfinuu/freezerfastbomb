"""
Configuration Manager Module
Handles all system configuration settings with JSON persistence
"""

import json
import os
from zoneinfo import ZoneInfo
from datetime import datetime
from typing import Dict, Any

class ConfigManager:
    """Manages system configuration with file persistence"""
    
    def __init__(self, config_file: str = "freezer_config.json"):
        """
        Initialize the configuration manager
        
        Args:
            config_file: Path to the JSON configuration file
        """
        self.config_file = config_file
        self.config = self._load_or_create_default()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        Get default configuration settings
        
        Returns:
            Dictionary with default configuration values
        """
        return {
            # Freezer Information
            "freezer_info": {
                "model_name": "FAST BOMBAS Freezer Modelo X",
                "location": "Instalação Principal de Armazenamento",
                "operator_name": "Equipe de Operações",
                "operator_contact": "operador@fastbombas.com"
            },
            
            # Temperature Thresholds (Celsius)
            "temperature_thresholds": {
                "evaporator": {
                    "min": -25.0,
                    "max": -15.0,
                    "critical_high": -10.0,
                    "critical_low": -30.0
                },
                "condenser": {
                    "min": 20.0,
                    "max": 40.0,
                    "critical_high": 50.0,
                    "critical_low": 15.0
                },
                "ambient": {
                    "min": 18.0,
                    "max": 30.0,
                    "critical_high": 35.0,
                    "critical_low": 10.0
                }
            },
            
            # Data Collection Settings
            "data_collection": {
                "reading_interval_seconds": 5,
                "chart_refresh_interval_seconds": 5,
                "max_data_points_display": 30,
                "max_historical_records": 10000
            },
            
            # Alert Settings
            "alert_settings": {
                "enable_email_alerts": True,
                "alert_cooldown_seconds": 300,  # Wait 5 minutes between repeat alerts
                "consecutive_readings_trigger": 2  # Alert after 2 consecutive critical readings
            },
            
            # Email Configuration
            "email_config": {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "sender_email": "",  # User must configure
                "recipient_emails": [],  # List of recipient emails
                "use_tls": True
            },
            
            # Data Logging
            "data_logging": {
                "enable_csv_logging": True,
                "csv_file_path": "data/temperature_logs.csv",
                "retention_days": 30,
                "auto_export_enabled": False,
                "export_interval_hours": 24
            },
            
            # Simulation Settings (for testing)
            "simulation": {
                "normal_temp_evaporator_min": -20.0,
                "normal_temp_evaporator_max": -15.0,
                "failure_probability": 0.05,  # 5% chance of failure per reading
                "failure_duration_seconds": 60,
                "temp_variation_range": 0.5  # +/- 0.5°C variation
            },
            
            # UI Settings
            "ui_settings": {
                "dashboard_title": "FAST BOMBAS - Sistema de Controle Térmico de Freezer",
                "temperature_unit": "Celsius",  # Celsius or Fahrenheit
                "show_advanced_metrics": True,
                "theme_color": "blue"
            },
            
            # System Metadata
            "system_metadata": {
                "config_version": "1.0",
                "last_modified": datetime.now(ZoneInfo("America/Sao_Paulo")).isoformat(),
                "created_date": datetime.now(ZoneInfo("America/Sao_Paulo")).isoformat()
            }
        }
    
    def _load_or_create_default(self) -> Dict[str, Any]:
        """
        Load configuration from file or create default if not exists
        
        Returns:
            Configuration dictionary
        """
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Merge with defaults to ensure new keys are added
                    default_config = self._get_default_config()
                    merged_config = self._deep_merge(default_config, config)
                    return merged_config
            except Exception as e:
                print(f"Error loading config file: {e}")
                print("Using default configuration")
                return self._get_default_config()
        else:
            # Create default configuration
            default_config = self._get_default_config()
            self.save_config(default_config)
            return default_config
    
    def _deep_merge(self, default: Dict, user: Dict) -> Dict:
        """
        Deep merge user config with default config
        Ensures new default keys are added while preserving user values
        
        Args:
            default: Default configuration dictionary
            user: User configuration dictionary
            
        Returns:
            Merged configuration dictionary
        """
        result = default.copy()
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result
    
    def save_config(self, config: Dict[str, Any] = None) -> bool:
        """
        Save configuration to file
        
        Args:
            config: Configuration dictionary to save (uses self.config if None)
            
        Returns:
            True if successful, False otherwise
        """
        if config is None:
            config = self.config
        
        try:
            # Update last modified timestamp
            config["system_metadata"]["last_modified"] = datetime.now(ZoneInfo("America/Sao_Paulo")).isoformat()
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_file) if os.path.dirname(self.config_file) else ".", exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            
            self.config = config
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def get(self, *keys) -> Any:
        """
        Get configuration value using dot notation
        
        Args:
            *keys: Keys to traverse (e.g., get('temperature_thresholds', 'evaporator', 'max'))
            
        Returns:
            Configuration value or None if not found
        """
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        return value
    
    def set(self, *keys_and_value) -> bool:
        """
        Set configuration value using dot notation
        
        Args:
            *keys_and_value: Keys and final value (e.g., set('email_config', 'smtp_port', 587))
            
        Returns:
            True if successful, False otherwise
        """
        if len(keys_and_value) < 2:
            return False
        
        keys = keys_and_value[:-1]
        value = keys_and_value[-1]
        
        # Navigate to the parent dictionary
        current = self.config
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Set the value
        current[keys[-1]] = value
        return self.save_config()
    
    def reset_to_default(self) -> bool:
        """
        Reset configuration to default values
        
        Returns:
            True if successful, False otherwise
        """
        self.config = self._get_default_config()
        return self.save_config()
    
    def export_config(self, export_path: str) -> bool:
        """
        Export configuration to a different file
        
        Args:
            export_path: Path to export the configuration
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error exporting config: {e}")
            return False
    
    def import_config(self, import_path: str) -> bool:
        """
        Import configuration from a file
        
        Args:
            import_path: Path to import the configuration from
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
            
            # Merge with defaults to ensure completeness
            default_config = self._get_default_config()
            merged_config = self._deep_merge(default_config, imported_config)
            
            return self.save_config(merged_config)
        except Exception as e:
            print(f"Error importing config: {e}")
            return False
