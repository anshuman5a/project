"""File operation route handlers"""

from fastapi import APIRouter, HTTPException, Request, status
from datetime import datetime

from ..models.requests import FileRequest
from ..models.responses import FileResponse, ErrorResponse
from ...utils.security import SecurityCheck
from ...utils.file_ops import FileOps
from ...utils.logger import logger

router = APIRouter()
security = SecurityCheck()
file_ops = FileOps()

@router.get("/read", response_model=FileResponse)
async def read_file(request: Request, file_req: FileRequest):
    """Read content from a file"""
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
            return FileResponse(
                content=content,
                timestamp=datetime.utcnow()
            )
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
