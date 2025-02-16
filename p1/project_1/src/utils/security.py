from pathlib import Path
from typing import List, Union, Set
import os
from .logger import logger

class SecurityCheck:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        
        # Dangerous operations that should be blocked
        self.forbidden_operations: Set[str] = {
            'rm', 'rmdir', 'delete', 'remove',
            'format', 'mkfs',
            'sudo', 'su',
            'chmod', 'chown'
        }
        
        # Allowed paths (relative to project root)
        self.allowed_paths: List[Path] = [
            self.project_root / "data",
            self.project_root / "logs",
            self.project_root / "temp"
        ]
        
        # Create allowed directories
        for path in self.allowed_paths:
            path.mkdir(parents=True, exist_ok=True)
            
        # File extensions that are allowed
        self.allowed_extensions: Set[str] = {
            '.txt', '.json', '.csv', '.md', '.py',
            '.jpg', '.jpeg', '.png', '.gif'
        }

    def validate_operation(self, operation: str) -> bool:
        """
        Validate if an operation is safe to execute
        
        Args:
            operation: The operation string to validate
            
        Returns:
            bool: True if operation is safe, False otherwise
        """
        try:
            operation = operation.lower().strip()
            
            # Check for forbidden operations
            if any(forbidden in operation for forbidden in self.forbidden_operations):
                logger.warning(f"Blocked forbidden operation: {operation}")
                return False
                
            # Additional security checks can be added here
            return True
            
        except Exception as e:
            logger.error(f"Error validating operation: {str(e)}")
            return False

    def is_path_allowed(self, path: Union[str, Path]) -> bool:
        """
        Check if a path is allowed for access
        
        Args:
            path: Path to validate
            
        Returns:
            bool: True if path is allowed, False otherwise
        """
        try:
            path = Path(path).resolve()
            
            # Check if path exists
            if not path.exists():
                logger.warning(f"Path does not exist: {path}")
                return False
                
            # Check if path is within allowed directories
            if not any(str(path).startswith(str(allowed)) for allowed in self.allowed_paths):
                logger.warning(f"Path not in allowed directories: {path}")
                return False
                
            # Check file extension if it's a file
            if path.is_file() and path.suffix.lower() not in self.allowed_extensions:
                logger.warning(f"File extension not allowed: {path}")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error checking path: {str(e)}")
            return False
            
    def sanitize_path(self, path: Union[str, Path]) -> Path:
        """
        Sanitize and validate a path
        
        Args:
            path: Path to sanitize
            
        Returns:
            Path: Sanitized path object
            
        Raises:
            ValueError: If path is invalid or not allowed
        """
        try:
            path = Path(path).resolve()
            
            if not self.is_path_allowed(path):
                raise ValueError(f"Path not allowed: {path}")
                
            return path
            
        except Exception as e:
            logger.error(f"Error sanitizing path: {str(e)}")
            raise ValueError(f"Invalid path: {str(e)}")