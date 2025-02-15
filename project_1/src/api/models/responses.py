"""Response models for API endpoints"""

from typing import Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

class TaskResponse(BaseModel):
    """Model for task execution response"""
    status: str
    message: str
    task_info: Dict[str, Any]
    timestamp: datetime
    
class FileResponse(BaseModel):
    """Model for file read response"""
    content: str
    timestamp: datetime
    
class ErrorResponse(BaseModel):
    """Model for error response"""
    detail: str
    timestamp: datetime
