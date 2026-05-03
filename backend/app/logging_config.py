"""
Logging configuration for CampaignCraft backend
Writes logs to files with automatic rotation
"""

import logging
import logging.handlers
import os
from pathlib import Path

# Create logs directory
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Log file paths
BACKEND_LOG = LOG_DIR / "backend.log"
API_LOG = LOG_DIR / "api.log"
AGENT_LOG = LOG_DIR / "agents.log"
ERROR_LOG = LOG_DIR / "errors.log"

def setup_logging():
    """Configure logging for the application"""
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Backend general log
    backend_handler = logging.handlers.RotatingFileHandler(
        BACKEND_LOG,
        maxBytes=5*1024*1024,  # 5MB
        backupCount=5
    )
    backend_handler.setLevel(logging.DEBUG)
    backend_handler.setFormatter(formatter)
    root_logger.addHandler(backend_handler)
    
    # API log
    api_logger = logging.getLogger('uvicorn.access')
    api_file_handler = logging.handlers.RotatingFileHandler(
        API_LOG,
        maxBytes=5*1024*1024,
        backupCount=5
    )
    api_file_handler.setFormatter(formatter)
    api_logger.addHandler(api_file_handler)
    
    # Agent log
    agent_logger = logging.getLogger('app.agents')
    agent_handler = logging.handlers.RotatingFileHandler(
        AGENT_LOG,
        maxBytes=5*1024*1024,
        backupCount=5
    )
    agent_handler.setFormatter(formatter)
    agent_logger.addHandler(agent_handler)
    
    # Error log
    error_handler = logging.handlers.RotatingFileHandler(
        ERROR_LOG,
        maxBytes=5*1024*1024,
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)
    
    # Console handler (brief)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    return root_logger

if __name__ == "__main__":
    setup_logging()
    print(f"Logs will be written to: {LOG_DIR}")
