"""
Configuration management for the revenue forecasting system.
"""

import os
import yaml
import json
from typing import Dict, Any, Optional
from pathlib import Path


class Config:
    """
    Configuration manager for the revenue forecasting system.

    Handles loading and managing configuration from files or dictionaries.
    """

    DEFAULT_CONFIG = {
        'data': {
            'date_column': 'date',
            'revenue_column': 'revenue',
            'missing_data_strategy': 'interpolate',  # 'interpolate', 'forward_fill', 'drop', 'mean'
            'outlier_detection': True,
            'outlier_threshold': 3.0,  # standard deviations
        },
        'models': {
            'auto_select': True,
            'validation_split': 0.2,
            'cross_validation_folds': 5,
            'ensemble_weights': 'auto',  # 'auto' or dict of weights
        },
        'forecasting': {
            'default_periods': 12,
            'confidence_level': 0.95,
            'seasonality': 'auto',  # 'auto', 'daily', 'weekly', 'monthly', 'quarterly', 'yearly'
            'trend': 'auto',  # 'auto', 'linear', 'exponential', 'logistic'
        },
        'business_model': {
            'type': None,  # 'saas', 'ecommerce', 'marketplace', 'freemium', 'enterprise', 'usage_based', 'hybrid'
            'metrics': [],
        },
        'scenarios': {
            'monte_carlo_simulations': 10000,
            'confidence_intervals': [0.10, 0.25, 0.50, 0.75, 0.90],
        },
        'output': {
            'format': 'excel',  # 'excel', 'csv', 'json', 'pdf'
            'include_visuals': True,
            'include_commentary': True,
            'decimal_places': 2,
        },
        'performance': {
            'parallel_processing': True,
            'n_jobs': -1,  # -1 for all CPUs
            'cache_enabled': True,
            'cache_dir': '.cache',
        },
        'logging': {
            'level': 'INFO',
            'file': 'revenue_builder.log',
            'console': True,
        }
    }

    def __init__(self, config_path: Optional[str] = None, config_dict: Optional[Dict] = None):
        """
        Initialize configuration.

        Args:
            config_path: Path to configuration file (YAML or JSON)
            config_dict: Configuration dictionary
        """
        self.config = self.DEFAULT_CONFIG.copy()

        if config_path:
            self.load_from_file(config_path)

        if config_dict:
            self.update(config_dict)

    def load_from_file(self, path: str):
        """Load configuration from a file."""
        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")

        with open(path, 'r') as f:
            if path.suffix in ['.yaml', '.yml']:
                loaded_config = yaml.safe_load(f)
            elif path.suffix == '.json':
                loaded_config = json.load(f)
            else:
                raise ValueError(f"Unsupported configuration file format: {path.suffix}")

        self.update(loaded_config)

    def update(self, config_dict: Dict):
        """Update configuration with new values."""
        self._deep_update(self.config, config_dict)

    def _deep_update(self, base_dict: Dict, update_dict: Dict):
        """Recursively update nested dictionaries."""
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.

        Args:
            key_path: Dot-separated path to config value (e.g., 'data.date_column')
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        value = self.config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def set(self, key_path: str, value: Any):
        """
        Set a configuration value using dot notation.

        Args:
            key_path: Dot-separated path to config value
            value: Value to set
        """
        keys = key_path.split('.')
        config = self.config

        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]

        config[keys[-1]] = value

    def save(self, path: str):
        """Save configuration to a file."""
        path = Path(path)

        with open(path, 'w') as f:
            if path.suffix in ['.yaml', '.yml']:
                yaml.dump(self.config, f, default_flow_style=False)
            elif path.suffix == '.json':
                json.dump(self.config, f, indent=2)
            else:
                raise ValueError(f"Unsupported file format: {path.suffix}")

    def to_dict(self) -> Dict:
        """Return configuration as a dictionary."""
        return self.config.copy()

    def __repr__(self) -> str:
        return f"Config({self.config})"
