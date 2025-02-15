"""Base class for task handlers"""

from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseTaskHandler(ABC):
    """Abstract base class for task handlers"""
    
    @abstractmethod
    async def execute(self, params: Dict[str, Any]) -> bool:
        """
        Execute the task with given parameters
        
        Args:
            params: Task parameters
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            ValueError: If parameters are invalid
            RuntimeError: If execution fails
        """
        pass
        
    def validate_params(self, params: Dict[str, Any], required_keys: list) -> None:
        """
        Validate that all required parameters are present
        
        Args:
            params: Parameters to validate
            required_keys: List of required parameter keys
            
        Raises:
            ValueError: If any required parameter is missing
        """
        if not isinstance(params, dict):
            raise ValueError("Parameters must be a dictionary")
            
        missing_keys = [key for key in required_keys if key not in params]
        if missing_keys:
            raise ValueError(f"Missing required parameters: {', '.join(missing_keys)}")
