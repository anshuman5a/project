"""Request models for API endpoints"""

from pydantic import BaseModel, constr

class TaskRequest(BaseModel):
    """Model for task execution request"""
    task: constr(min_length=1, max_length=1000)
    
class FileRequest(BaseModel):
    """Model for file read request"""
    path: constr(min_length=1, max_length=255)
