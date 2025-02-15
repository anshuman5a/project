"""Task execution route handlers"""

from fastapi import APIRouter, HTTPException, Request, status
from datetime import datetime

from ..models.requests import TaskRequest
from ..models.responses import TaskResponse, ErrorResponse
from ...tasks.parser import TaskParser
from ...tasks.executor import TaskExecutor
from ...utils.logger import logger

router = APIRouter()
parser = TaskParser()
executor = TaskExecutor()

@router.post("/run", response_model=TaskResponse)
async def run_task(request: Request, task_req: TaskRequest):
    """Execute a task based on the provided description"""
    try:
        # Parse task
        task_info = await parser.parse_task(task_req.task)
        logger.info(f"Parsed task info: {task_info}")
        
        # Execute task
        try:
            success = await executor.execute_task(task_info)
            
            if success:
                return TaskResponse(
                    status="success",
                    message="Task executed successfully",
                    task_info=task_info,
                    timestamp=datetime.utcnow()
                )
                
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
