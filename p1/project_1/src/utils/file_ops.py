# src/utils/file_ops.py

from pathlib import Path
from typing import List, Union, Optional
import aiofiles
import os
from .logger import logger

class FileOps:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        
    async def read_file(self, path: Union[str, Path]) -> str:
        """
        Read content from a file asynchronously
        
        Args:
            path: Path to the file to read
            
        Returns:
            str: Content of the file
            
        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If file cannot be accessed
        """
        try:
            path = Path(path)
            if not path.exists():
                raise FileNotFoundError(f"File not found: {path}")
            if not path.is_file():
                raise ValueError(f"Path is not a file: {path}")
                
            async with aiofiles.open(path, 'r', encoding='utf-8') as f:
                return await f.read()
        except Exception as e:
            logger.error(f"Error reading file {path}: {str(e)}")
            raise
            
    async def write_file(self, path: Union[str, Path], content: str) -> None:
        """
        Write content to a file asynchronously
        
        Args:
            path: Path to write the file to
            content: Content to write
            
        Raises:
            PermissionError: If file cannot be written
            OSError: If directory creation fails
        """
        try:
            path = Path(path)
            if not path.is_absolute():
                path = self.project_root / path
            
            # Ensure directory exists
            path.parent.mkdir(parents=True, exist_ok=True)
            
            async with aiofiles.open(path, 'w', encoding='utf-8') as f:
                await f.write(content)
                
            logger.info(f"Successfully wrote to file: {path}")
        except Exception as e:
            logger.error(f"Error writing to file {path}: {str(e)}")
            raise
            
    async def list_files(self, directory: Union[str, Path], pattern: str = "*", recursive: bool = False) -> List[Path]:
        """
        List files in a directory matching a pattern
        
        Args:
            directory: Directory to search in
            pattern: Glob pattern to match files
            recursive: Whether to search recursively
            
        Returns:
            List of Path objects for matching files
            
        Raises:
            NotADirectoryError: If directory doesn't exist or is not a directory
        """
        try:
            directory = Path(directory)
            if not directory.exists():
                raise NotADirectoryError(f"Directory not found: {directory}")
            if not directory.is_dir():
                raise NotADirectoryError(f"Path is not a directory: {directory}")
            
            if recursive:
                return list(directory.rglob(pattern))
            return list(directory.glob(pattern))
        except Exception as e:
            logger.error(f"Error listing files in {directory}: {str(e)}")
            raise