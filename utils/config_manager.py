"""
Configuration Manager for JARVIS
Handles all configuration settings and preferences
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path
from typing import Dict, List


from utils.logger import get_logger

class ConfigManager:
    """
    Advanced Configuration Manager
    Handles all JARVIS configuration settings
    """
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.config_dir = Path("config")
        self.config_file = self.config_dir / "jarvis_config.json"
        
        # Default configuration
        self.default_config = {
            'ai': {
                'api_key': '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',
                'model': 'google/gemini-2.5-flash-lite-preview-06-17',
                'temperature': 0.7,
                'max_tokens': 1000,
                'timeout': 30
            },
            'voice': {
                'enabled': True,
                'rate': 180,
                'volume': 0.9,
                'language': 'en-US',
                'wake_words': ['jarvis', 'जार्विस']
            },
            'system': {
                'monitoring_enabled': True,
                'auto_optimization': True,
                'security_monitoring': True,
                'update_interval': 5
            },
            'interface': {
                'theme': 'dark',
                'language': 'english',
                'gui_enabled': True,
                'console_colors': True
            },
            'learning': {
                'enabled': True,
                'save_conversations': True,
                'adapt_responses': True,
                'user_preferences': {}
            },
            'security': {
                'require_authentication': False,
                'log_commands': True,
                'restrict_system_commands': False,
                'encryption_enabled': True
            },
            'network': {
                'proxy_enabled': False,
                'proxy_host': '',
                'proxy_port': 8080,
                'timeout': 10
            },
            'hardware': {
                'gpu_acceleration': True,
                'cpu_optimization': True,
                'memory_management': True,
                'temperature_monitoring': True
            }
        }
        
        # Current configuration
        self.config = {}
        
        # Load configuration
        self._load_config()
        
        self.logger.info("⚙️ Configuration Manager initialized")
    
    def _load_config(self):
        """Load configuration from file"""
        try:
            # Create config directory if it doesn't exist
            self.config_dir.mkdir(exist_ok=True)
            
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                
                # Merge with default config
                self.config = self._merge_configs(self.default_config, file_config)
                self.logger.info("✅ Configuration loaded from file")
            else:
                # Use default configuration
                self.config = self.default_config.copy()
                self._save_config()
                self.logger.info("✅ Default configuration created")
                
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
            self.config = self.default_config.copy()
    
    def _merge_configs(self, default: Dict, user: Dict) -> Dict:
        """Merge user configuration with default configuration"""
        merged = default.copy()
        
        for key, value in user.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._merge_configs(merged[key], value)
            else:
                merged[key] = value
        
        return merged
    
    def _save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            self.logger.info("✅ Configuration saved")
            
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key"""
        try:
            keys = key.split('.')
            value = self.config
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            
            return value
            
        except Exception as e:
            self.logger.error(f"Error getting config value for key '{key}': {e}")
            return default
    
    def set(self, key: str, value: Any, save: bool = True):
        """Set configuration value by key"""
        try:
            keys = key.split('.')
            config = self.config
            
            # Navigate to the parent dictionary
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            
            # Set the value
            config[keys[-1]] = value
            
            if save:
                self._save_config()
            
            self.logger.info(f"Configuration updated: {key} = {value}")
            
        except Exception as e:
            self.logger.error(f"Error setting config value for key '{key}': {e}")
    
    def get_section(self, section: str) -> Dict:
        """Get entire configuration section"""
        return self.config.get(section, {}).copy()
    
    def set_section(self, section: str, values: Dict, save: bool = True):
        """Set entire configuration section"""
        try:
            self.config[section] = values
            
            if save:
                self._save_config()
            
            self.logger.info(f"Configuration section updated: {section}")
            
        except Exception as e:
            self.logger.error(f"Error setting config section '{section}': {e}")
    
    def update(self, updates: Dict, save: bool = True):
        """Update multiple configuration values"""
        try:
            for key, value in updates.items():
                self.set(key, value, save=False)
            
            if save:
                self._save_config()
            
            self.logger.info(f"Configuration updated with {len(updates)} changes")
            
        except Exception as e:
            self.logger.error(f"Error updating configuration: {e}")
    
    def reset_to_default(self, section: Optional[str] = None):
        """Reset configuration to default values"""
        try:
            if section:
                if section in self.default_config:
                    self.config[section] = self.default_config[section].copy()
                    self.logger.info(f"Configuration section '{section}' reset to default")
            else:
                self.config = self.default_config.copy()
                self.logger.info("Configuration reset to default")
            
            self._save_config()
            
        except Exception as e:
            self.logger.error(f"Error resetting configuration: {e}")
    
    def validate_config(self) -> Dict[str, List[str]]:
        """Validate configuration and return any issues"""
        issues = {
            'errors': [],
            'warnings': []
        }
        
        try:
            # Validate AI configuration
            ai_config = self.get_section('ai')
            if not ai_config.get('api_key'):
                issues['errors'].append("AI API key is missing")
            
            if not ai_config.get('model'):
                issues['errors'].append("AI model is not specified")
            
            # Validate voice configuration
            voice_config = self.get_section('voice')
            if voice_config.get('rate', 0) < 50 or voice_config.get('rate', 0) > 400:
                issues['warnings'].append("Voice rate should be between 50-400")
            
            if voice_config.get('volume', 0) < 0 or voice_config.get('volume', 0) > 1:
                issues['warnings'].append("Voice volume should be between 0-1")
            
            # Validate system configuration
            system_config = self.get_section('system')
            if system_config.get('update_interval', 0) < 1:
                issues['warnings'].append("System update interval should be at least 1 second")
            
            self.logger.info(f"Configuration validation complete: {len(issues['errors'])} errors, {len(issues['warnings'])} warnings")
            
        except Exception as e:
            self.logger.error(f"Error validating configuration: {e}")
            issues['errors'].append(f"Validation error: {str(e)}")
        
        return issues
    
    def export_config(self, file_path: str):
        """Export configuration to file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Configuration exported to: {file_path}")
            
        except Exception as e:
            self.logger.error(f"Error exporting configuration: {e}")
    
    def import_config(self, file_path: str):
        """Import configuration from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
            
            # Merge with current config
            self.config = self._merge_configs(self.config, imported_config)
            self._save_config()
            
            self.logger.info(f"Configuration imported from: {file_path}")
            
        except Exception as e:
            self.logger.error(f"Error importing configuration: {e}")
    
    def get_all_config(self) -> Dict:
        """Get complete configuration"""
        return self.config.copy()
    
    def get_config_info(self) -> Dict:
        """Get configuration information"""
        return {
            'config_file': str(self.config_file),
            'config_dir': str(self.config_dir),
            'sections': list(self.config.keys()),
            'total_settings': sum(len(section) if isinstance(section, dict) else 1 for section in self.config.values()),
            'last_modified': self.config_file.stat().st_mtime if self.config_file.exists() else None
        }