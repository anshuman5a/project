import logging
import logging.handlers
import os
from pathlib import Path

# Create logs directory
log_dir = Path(__file__).parent.parent.parent / 'logs'
log_dir.mkdir(exist_ok=True)

# Configure logging with rotation
handler = logging.handlers.RotatingFileHandler(
    filename=log_dir / 'app.log',
    maxBytes=5*1024*1024,  # 5MB
    backupCount=3,
    encoding='utf-8'
)

# Configure console handler
console_handler = logging.StreamHandler()

# Configure formatting
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    handlers=[handler, console_handler]
)

# Get logger for this module
logger = logging.getLogger(__name__)

# Prevent propagation of logs to avoid duplicate entries
logger.propagate = False