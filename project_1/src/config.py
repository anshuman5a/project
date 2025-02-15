import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv
from src.utils.logger import logger

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

class Config:
    """Application configuration with validation and type safety"""
    
    def __init__(self):
        # API Configuration
        self.API_HOST: str = self._get_env("API_HOST", "0.0.0.0")
        self.API_PORT: int = int(self._get_env("API_PORT", "8000"))
        
        # Security Configuration
        self.AIPROXY_TOKEN: str = self._get_env("AIPROXY_TOKEN")
        
        # File System Configuration
        self.PROJECT_ROOT: Path = Path(__file__).parent.parent
        self.DATA_DIR: Path = self.PROJECT_ROOT / "data"
        self.LOGS_DIR: Path = self.PROJECT_ROOT / "logs"
        self.TEMP_DIR: Path = self.PROJECT_ROOT / "temp"
        
        # Create necessary directories
        self._create_directories()
        
        # API Configuration
        self.CORS_ORIGINS: list = self._get_env(
            "CORS_ORIGINS", 
            "*"
        ).split(",")
        
        # Rate Limiting
        self.RATE_LIMIT_ENABLED: bool = self._get_env_bool("RATE_LIMIT_ENABLED", True)
        self.RATE_LIMIT_REQUESTS: int = int(self._get_env("RATE_LIMIT_REQUESTS", "100"))
        self.RATE_LIMIT_PERIOD: int = int(self._get_env("RATE_LIMIT_PERIOD", "3600"))
        
        # Validate configuration
        self._validate_config()
        
    def _get_env(self, key: str, default: Any = None) -> str:
        """Get environment variable with logging"""
        value = os.getenv(key, default)
        if value is None:
            raise ValueError(f"Required environment variable {key} is not set")
        return value
        
    def _get_env_bool(self, key: str, default: bool = False) -> bool:
        """Get boolean environment variable"""
        value = os.getenv(key, str(default)).lower()
        return value in ('true', '1', 'yes', 'on')
        
    def _create_directories(self) -> None:
        """Create necessary directories if they don't exist"""
        try:
            self.DATA_DIR.mkdir(parents=True, exist_ok=True)
            self.LOGS_DIR.mkdir(parents=True, exist_ok=True)
            self.TEMP_DIR.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to create directories: {str(e)}")
            raise
            
    def _validate_config(self) -> None:
        """Validate configuration values"""
        if not self.API_PORT or not (1024 <= self.API_PORT <= 65535):
            raise ValueError(f"Invalid API_PORT: {self.API_PORT}")
            
        if not self.AIPROXY_TOKEN:
            raise ValueError("AIPROXY_TOKEN is required")
            
        if self.RATE_LIMIT_ENABLED:
            if self.RATE_LIMIT_REQUESTS <= 0:
                raise ValueError("RATE_LIMIT_REQUESTS must be positive")
            if self.RATE_LIMIT_PERIOD <= 0:
                raise ValueError("RATE_LIMIT_PERIOD must be positive")
                
    def as_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary for easy access"""
        return {
            key: value for key, value in self.__dict__.items()
            if not key.startswith('_')
        }

# Create global config instance
config = Config()

# Export all config variables
API_HOST = config.API_HOST
API_PORT = config.API_PORT
AIPROXY_TOKEN = config.AIPROXY_TOKEN
DATA_DIR = config.DATA_DIR
CORS_ORIGINS = config.CORS_ORIGINS
RATE_LIMIT_ENABLED = config.RATE_LIMIT_ENABLED
RATE_LIMIT_REQUESTS = config.RATE_LIMIT_REQUESTS
RATE_LIMIT_PERIOD = config.RATE_LIMIT_PERIOD