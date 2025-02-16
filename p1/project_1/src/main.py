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

@app.post("/run")
@limiter.limit(f"{RATE_LIMIT_REQUESTS}/{RATE_LIMIT_PERIOD}s") if RATE_LIMIT_ENABLED else lambda x: x
async def run_task(
    request: Request,
    task_req: Optional[TaskRequest] = None,
    task: str = Query(None, description="Task description if sent as query parameter")
):
    try:
        # Get task either from JSON body or query parameter
        task_description = task_req.task if task_req else task
        if not task_description:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Task description is required either in request body or as query parameter"
            )

        # Parse and validate the task
        parsed_task = parser.parse(task_description)
        if not parsed_task:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid task format"
            )

        # Security check
        security.validate_task(parsed_task)

        # Execute the task
        result = await executor.execute(parsed_task)
        
        return {
            "status": "success",
            "task": parsed_task,
            "result": result
        }

    except Exception as e:
        logger.error(f"Task execution failed: {str(e)}")
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Task execution failed: {str(e)}"
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
