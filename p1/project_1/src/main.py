# src/main.py

from fastapi import FastAPI, HTTPException, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel, constr
from typing import Optional, Dict, Any
from datetime import datetime

from src.tasks.parser import TaskParser
from src.tasks.executor import TaskExecutor
from src.utils.security import SecurityCheck
from src.utils.file_ops import FileOps
from src.utils.logger import logger
from .config import (
    API_PORT, 
    API_HOST, 
    CORS_ORIGINS,
    RATE_LIMIT_ENABLED,
    RATE_LIMIT_REQUESTS,
    RATE_LIMIT_PERIOD
)

# Initialize FastAPI app with metadata
app = FastAPI(
    title="Task Execution API",
    description="API for executing various tasks and file operations",
    version="1.0.0"
)

# Initialize components
parser = TaskParser()
executor = TaskExecutor()
security = SecurityCheck()
file_ops = FileOps()

# Rate limiting
if RATE_LIMIT_ENABLED:
    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Request Models
class TaskRequest(BaseModel):
    task: constr(min_length=1, max_length=1000)
    
class FileRequest(BaseModel):
    path: constr(min_length=1, max_length=255)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure as needed
)

@app.post("/run", response_model=Dict[str, Any])
@limiter.limit(f"{RATE_LIMIT_REQUESTS}/{RATE_LIMIT_PERIOD}s") if RATE_LIMIT_ENABLED else lambda x: x
async def run_task(request: Request, task_req: TaskRequest):
    """
    Execute a task based on the provided description
    
    Args:
        request: FastAPI request object
        task_req: Task request containing the task description
        
    Returns:
        Dict containing task execution status and info
        
    Raises:
        HTTPException: For various error conditions
    """
    try:
        # Parse task
        task_info = await parser.parse_task(task_req.task)
        logger.info(f"Parsed task info: {task_info}")
        
        # Execute task
        try:
            success = await executor.execute_task(task_info)
            
            if success:
                return {
                    "status": "success",
                    "message": "Task executed successfully",
                    "task_info": task_info,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Task execution error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Task execution failed: {str(e)}"
            )
            
    except ValueError as e:
        logger.error(f"Bad request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/read", response_model=Dict[str, str])
@limiter.limit(f"{RATE_LIMIT_REQUESTS}/{RATE_LIMIT_PERIOD}s") if RATE_LIMIT_ENABLED else lambda x: x
async def read_file(request: Request, file_req: FileRequest):
    """
    Read content from a file
    
    Args:
        request: FastAPI request object
        file_req: File request containing the file path
        
    Returns:
        Dict containing file content
        
    Raises:
        HTTPException: For various error conditions
    """
    try:
        # Normalize path
        path = file_req.path.strip("'\"").lstrip('/')
        
        # Security check
        if not security.is_path_allowed(path):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
            
        try:
            content = await file_ops.read_file(path)
            return {
                "content": content,
                "timestamp": datetime.utcnow().isoformat()
            }
        except FileNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reading file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reading file: {str(e)}"
        )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

# Error handler for all unhandled exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An unexpected error occurred",
            "timestamp": datetime.utcnow().isoformat()
        }
    )

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting server on {API_HOST}:{API_PORT}")
    uvicorn.run(
        app,
        host=API_HOST,
        port=API_PORT,
        reload=True,
        log_level="info"
    )