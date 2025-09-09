"""
CLI Configuration Management
CONSTITUTIONAL COMPLIANCE: Uses existing LD-3.4 framework, no modifications
"""

import os
import json
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class CLIConfig:
    """Configuration for TransRapport CLI"""
    database_path: str = "data/transrapport.db"
    constitutional_source: str = "LD-3.4-constitution"
    analysis_method: str = "LD-3.4"
    confidence_threshold: float = 0.7
    export_directory: str = "exports"
    temp_directory: str = "temp"
    log_level: str = "INFO"
    
    # Analysis configuration
    enable_ato: bool = True
    enable_sem: bool = True
    enable_clu: bool = True
    enable_mema: bool = True
    enable_rapport: bool = True
    
    # Export configuration
    default_transcript_formats: list = None
    default_marker_formats: list = None
    
    def __post_init__(self):
        if self.default_transcript_formats is None:
            self.default_transcript_formats = ["annotated_txt", "json", "csv"]
        
        if self.default_marker_formats is None:
            self.default_marker_formats = ["json", "csv", "analytics"]


def load_config(config_path: Optional[str] = None) -> CLIConfig:
    """
    Load CLI configuration from file or defaults
    
    Args:
        config_path: Optional path to configuration file
        
    Returns:
        CLIConfig instance
    """
    config = CLIConfig()
    
    # Try to load from file
    if config_path and Path(config_path).exists():
        try:
            with open(config_path, 'r') as f:
                data = json.load(f)
            
            # Update config with loaded data
            for key, value in data.items():
                if hasattr(config, key):
                    setattr(config, key, value)
                    
        except Exception as e:
            print(f"Warning: Failed to load config from {config_path}: {e}")
    
    # Load from environment variables
    config = _load_from_env(config)
    
    # Ensure directories exist
    Path(config.database_path).parent.mkdir(parents=True, exist_ok=True)
    Path(config.export_directory).mkdir(parents=True, exist_ok=True)
    Path(config.temp_directory).mkdir(parents=True, exist_ok=True)
    
    return config


def _load_from_env(config: CLIConfig) -> CLIConfig:
    """Load configuration from environment variables"""
    
    env_mappings = {
        'TRANSRAPPORT_DATABASE_PATH': 'database_path',
        'TRANSRAPPORT_EXPORT_DIR': 'export_directory',
        'TRANSRAPPORT_TEMP_DIR': 'temp_directory',
        'TRANSRAPPORT_LOG_LEVEL': 'log_level',
        'TRANSRAPPORT_CONFIDENCE_THRESHOLD': 'confidence_threshold',
    }
    
    for env_var, attr_name in env_mappings.items():
        env_value = os.getenv(env_var)
        if env_value:
            if attr_name == 'confidence_threshold':
                try:
                    setattr(config, attr_name, float(env_value))
                except ValueError:
                    pass
            else:
                setattr(config, attr_name, env_value)
    
    return config


def save_config(config: CLIConfig, config_path: str) -> bool:
    """
    Save configuration to file
    
    Args:
        config: Configuration to save
        config_path: Path to save configuration file
        
    Returns:
        True if successful
    """
    try:
        config_dict = asdict(config)
        
        Path(config_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(config_dict, f, indent=2)
        
        return True
        
    except Exception as e:
        print(f"Error saving config to {config_path}: {e}")
        return False