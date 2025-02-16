# run.py (in root directory)
import uvicorn
import logging
from src.config import (
    API_HOST, 
    API_PORT
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        config = {
            "app": "src.main:app",
            "host": API_HOST,
            "port": API_PORT,
            "reload": True,
            "log_level": "info",
            "workers": 4  # Number of worker processes
        }
        
        logger.info(f"Starting server on {API_HOST}:{API_PORT}")
        uvicorn.run(**config)
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        raise