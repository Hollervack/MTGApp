"""Configuration settings for the MTG Deck Constructor application"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import json


class Settings:
    """Class for managing application configurations"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or self._get_default_config_path()
        self._settings = self._load_default_settings()
        self._load_from_file()
    
    def _get_default_config_path(self) -> str:
        """Gets the default path for the configuration file"""
        # Search in the project directory
        project_root = Path(__file__).parent.parent.parent
        return str(project_root / 'config.json')
    
    def _load_default_settings(self) -> Dict[str, Any]:
        """Loads default configurations"""
        return {
            # Application settings
            'app': {
                'name': 'MTG Deck Constructor',
                'version': '1.0.0',
                'debug': False,
                'language': 'es'
            },
            
            # Interface configurations
            'ui': {
                'theme': 'default',
                'window_width': 1200,
                'window_height': 800,
                'window_resizable': True,
                'remember_window_size': True,
                'font_family': 'Arial',
                'font_size': 10
            },
            
            # Data configurations
            'data': {
                'cards_file': 'data/databaseMTG.csv',
                'decks_directory': 'data/decks',
                'cache_directory': 'data/cache',
                'images_directory': 'data/images',
                'backup_directory': 'data/backups',
                'auto_backup': True,
                'backup_interval_days': 7
            },
            
            # Image configurations
            'images': {
                'cache_enabled': True,
                'cache_size_mb': 500,
                'auto_download': True,
                'image_quality': 'normal',  # 'low', 'normal', 'high'
                'thumbnail_size': (200, 280),
                'full_size': (488, 680),
                'timeout_seconds': 30
            },
            
            # External API configurations
            'api': {
                'scryfall_base_url': 'https://api.scryfall.com',
                'rate_limit_delay': 0.1,  # seconds between requests
                'max_retries': 3,
                'timeout_seconds': 30,
                'user_agent': 'MTG Deck Constructor/1.0'
            },
            
            # Import/export configurations
            'import_export': {
                'supported_formats': ['txt', 'json', 'csv'],
                'default_export_format': 'txt',
                'include_metadata': True,
                'auto_detect_format': True
            },
            
            # Analysis configurations
            'analysis': {
                'enable_mana_curve': True,
                'enable_color_analysis': True,
                'enable_type_analysis': True,
                'enable_rarity_analysis': True,
                'enable_set_analysis': True,
                'cache_analysis_results': True
            },
            
            # Logging configurations
            'logging': {
                'level': 'INFO',  # DEBUG, INFO, WARNING, ERROR, CRITICAL
                'file_enabled': True,
                'file_path': 'logs/app.log',
                'max_file_size_mb': 10,
                'backup_count': 5,
                'console_enabled': True
            }
        }
    
    def _load_from_file(self):
        """Loads configurations from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    file_settings = json.load(f)
                
                # Merge file configurations with defaults
                self._merge_settings(self._settings, file_settings)
        except Exception as e:
            print(f"Error loading configurations from file: {e}")
    
    def _merge_settings(self, default: Dict[str, Any], override: Dict[str, Any]):
        """Merges configurations recursively"""
        for key, value in override.items():
            if key in default and isinstance(default[key], dict) and isinstance(value, dict):
                self._merge_settings(default[key], value)
            else:
                default[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Gets a configuration using dot notation"""
        keys = key.split('.')
        value = self._settings
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any):
        """Sets a configuration using dot notation"""
        keys = key.split('.')
        current = self._settings
        
        # Navigate to the second-to-last level
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        # Set the final value
        current[keys[-1]] = value
    
    def save(self) -> bool:
        """Saves current configurations to file"""
        try:
            # Create directory if it doesn't exist
            config_path = Path(self.config_file)
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving configurations: {e}")
            return False
    
    def reset_to_defaults(self):
        """Resets all configurations to default values"""
        self._settings = self._load_default_settings()
    
    def get_all(self) -> Dict[str, Any]:
        """Gets all configurations"""
        return self._settings.copy()
    
    def update(self, settings: Dict[str, Any]):
        """Updates multiple configurations"""
        self._merge_settings(self._settings, settings)
    
    # Quick access properties for common configurations
    @property
    def app_name(self) -> str:
        return self.get('app.name', 'MTG Deck Constructor')
    
    @property
    def app_version(self) -> str:
        return self.get('app.version', '1.0.0')
    
    @property
    def debug_mode(self) -> bool:
        return self.get('app.debug', False)
    
    @property
    def cards_file(self) -> str:
        return self.get('data.cards_file', 'data/databaseMTG.csv')
    
    @property
    def decks_directory(self) -> str:
        return self.get('data.decks_directory', 'data/decks')
    
    @property
    def cache_directory(self) -> str:
        return self.get('data.cache_directory', 'data/cache')
    
    @property
    def images_directory(self) -> str:
        return self.get('data.images_directory', 'data/images')
    
    @property
    def window_size(self) -> tuple:
        return (self.get('ui.window_width', 1200), self.get('ui.window_height', 800))
    
    @property
    def image_cache_enabled(self) -> bool:
        return self.get('images.cache_enabled', True)
    
    @property
    def auto_download_images(self) -> bool:
        return self.get('images.auto_download', True)
    
    @property
    def scryfall_api_url(self) -> str:
        return self.get('api.scryfall_base_url', 'https://api.scryfall.com')
    
    @property
    def api_rate_limit(self) -> float:
        return self.get('api.rate_limit_delay', 0.1)


# Global instance of configurations
_settings_instance: Optional[Settings] = None


def get_settings(config_file: Optional[str] = None) -> Settings:
    """Gets the global configuration instance"""
    global _settings_instance
    
    if _settings_instance is None or config_file is not None:
        _settings_instance = Settings(config_file)
    
    return _settings_instance


def reload_settings(config_file: Optional[str] = None):
    """Reloads configurations"""
    global _settings_instance
    _settings_instance = Settings(config_file)