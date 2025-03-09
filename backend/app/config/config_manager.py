from typing import Dict, Any, Optional
from pathlib import Path
import yaml
import os
from dataclasses import dataclass
from datetime import timedelta

@dataclass
class AssetConfig:
    """Technical analysis configuration parameters"""
    SHORT_WINDOW: int = 12
    LONG_WINDOW: int = 26
    SIGNAL_WINDOW: int = 9
    BOLLINGER_WINDOW: int = 20
    STD_DEV: float = 2.0
    STOCH_WINDOW: int = 14
    SMOOTH_WINDOW: int = 3
    ADX_WINDOW: int = 14
    CCI_WINDOW: int = 20
    RSI_WINDOW: int = 14

@dataclass
class CorrelationConfig:
    """Correlation analysis configuration parameters"""
    MIN_WINDOW_SIZE: int = 5
    MAX_WINDOW_SIZE: int = 500
    DEFAULT_WINDOW_SIZE: int = 30
    MIN_CORRELATION: float = -1.0
    MAX_CORRELATION: float = 1.0
    ROLLING_WINDOWS: list = None
    
    def __post_init__(self):
        self.ROLLING_WINDOWS = [30, 60, 90, 180, 360] if self.ROLLING_WINDOWS is None else self.ROLLING_WINDOWS

@dataclass
class APIConfig:
    """API configuration parameters"""
    HOST: str = "localhost"
    PORT: int = 5000
    DEBUG: bool = True
    CORS_ORIGINS: list = None
    REQUEST_TIMEOUT: int = 30
    
    def __post_init__(self):
        self.CORS_ORIGINS = ["http://localhost:5173"] if self.CORS_ORIGINS is None else self.CORS_ORIGINS

class ConfigManager:
    """Configuration management class for the application"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.env = os.getenv('FLASK_ENV', 'development')
        self.config_path = config_path or self._get_default_config_path()
        self.config: Dict[str, Any] = {}
        self.asset_config = AssetConfig()
        self.correlation_config = CorrelationConfig()
        self.api_config = APIConfig()
        self._load_config()
        self._validate_config()

    def _get_default_config_path(self) -> Path:
        """Get the default configuration file path based on environment"""
        config_dir = Path(__file__).parent
        return config_dir / f"config.{self.env}.yaml"

    def _load_config(self) -> None:
        """Load configuration from YAML file and environment variables"""
        # Load from YAML
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        
        # Override with environment variables
        self._load_env_vars()
        
        # Update dataclass configs
        self._update_configs()

    def _load_env_vars(self) -> None:
        """Load configuration from environment variables"""
        env_mappings = {
            'FLASK_HOST': ('api', 'host'),
            'FLASK_PORT': ('api', 'port'),
            'FLASK_DEBUG': ('api', 'debug'),
            'CORS_ORIGINS': ('api', 'cors_origins'),
            'DEFAULT_WINDOW_SIZE': ('correlation', 'default_window_size'),
            'DATA_DIR': ('data', 'directory'),
        }
        
        for env_var, config_path in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                self._set_nested_dict(self.config, config_path, value)

    def _set_nested_dict(self, d: dict, path: tuple, value: Any) -> None:
        """Set a value in a nested dictionary using a path tuple"""
        for key in path[:-1]:
            d = d.setdefault(key, {})
        d[path[-1]] = value

    def _update_configs(self) -> None:
        """Update dataclass configurations from loaded config"""
        if 'asset' in self.config:
            for key, value in self.config['asset'].items():
                if hasattr(self.asset_config, key):
                    setattr(self.asset_config, key, value)
        
        if 'correlation' in self.config:
            for key, value in self.config['correlation'].items():
                if hasattr(self.correlation_config, key):
                    setattr(self.correlation_config, key, value)
        
        if 'api' in self.config:
            for key, value in self.config['api'].items():
                if hasattr(self.api_config, key):
                    setattr(self.api_config, key, value)

    def _validate_config(self) -> None:
        """Validate configuration values"""
        # Validate correlation config
        if not (self.correlation_config.MIN_WINDOW_SIZE <= 
                self.correlation_config.DEFAULT_WINDOW_SIZE <= 
                self.correlation_config.MAX_WINDOW_SIZE):
            raise ValueError("Invalid window size configuration")
        
        if not (self.correlation_config.MIN_CORRELATION <= 
                self.correlation_config.MAX_CORRELATION):
            raise ValueError("Invalid correlation range configuration")
        
        # Validate API config
        if not isinstance(self.api_config.PORT, int) or not (0 <= self.api_config.PORT <= 65535):
            raise ValueError("Invalid port number")
        
        if not isinstance(self.api_config.CORS_ORIGINS, list):
            raise ValueError("CORS_ORIGINS must be a list")

    def get_flask_config(self) -> Dict[str, Any]:
        """Get Flask application configuration"""
        return {
            'HOST': self.api_config.HOST,
            'PORT': self.api_config.PORT,
            'DEBUG': self.api_config.DEBUG,
            'CORS_ORIGINS': self.api_config.CORS_ORIGINS,
            'REQUEST_TIMEOUT': self.api_config.REQUEST_TIMEOUT
        }

    def get_correlation_config(self) -> Dict[str, Any]:
        """Get correlation analysis configuration"""
        return {
            'DEFAULT_WINDOW_SIZE': self.correlation_config.DEFAULT_WINDOW_SIZE,
            'MIN_WINDOW_SIZE': self.correlation_config.MIN_WINDOW_SIZE,
            'MAX_WINDOW_SIZE': self.correlation_config.MAX_WINDOW_SIZE,
            'ROLLING_WINDOWS': self.correlation_config.ROLLING_WINDOWS
        }

    def get_asset_config(self) -> Dict[str, Any]:
        """Get asset analysis configuration"""
        return {
            'SHORT_WINDOW': self.asset_config.SHORT_WINDOW,
            'LONG_WINDOW': self.asset_config.LONG_WINDOW,
            'SIGNAL_WINDOW': self.asset_config.SIGNAL_WINDOW,
            'BOLLINGER_WINDOW': self.asset_config.BOLLINGER_WINDOW,
            'STD_DEV': self.asset_config.STD_DEV,
            'STOCH_WINDOW': self.asset_config.STOCH_WINDOW,
            'SMOOTH_WINDOW': self.asset_config.SMOOTH_WINDOW,
            'ADX_WINDOW': self.asset_config.ADX_WINDOW,
            'CCI_WINDOW': self.asset_config.CCI_WINDOW,
            'RSI_WINDOW': self.asset_config.RSI_WINDOW
        } 