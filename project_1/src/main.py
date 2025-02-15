"""Main application entry point"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from datetime import datetime

from .api.routes import task_routes, file_routes
from .api.middleware.security import setup_security
from .core.config import API_HOST, API_PORT
from .utils.logger import logger

# Initialize FastAPI app with metadata
app = FastAPI(
    title="Task Execution API",
    description="API for executing various tasks and file operations",
    version="1.0.0"
)

# Setup security middleware
setup_security(app)

# Include routers
app.include_router(task_routes.router)
app.include_router(file_routes.router)

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