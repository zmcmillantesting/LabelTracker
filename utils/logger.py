# utils/logger.py
import logging
import os, sys
from datetime import datetime

def resource_path(relative_path: str) -> str:
    """Return an absolute path suitable for bundled apps.

    If running as a PyInstaller bundle (frozen), use the directory
    containing the executable so logs are created next to the exe.
    Otherwise use the current working directory (project root).
    """
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.abspath('.')
    # If an absolute path was passed, return it unchanged
    if os.path.isabs(relative_path):
        return relative_path
    return os.path.join(base_path, relative_path)


def setup_logging(log_dir: str = None, log_level=logging.INFO):
    """Setup application logging.

    By default logs are written to a `logs/` folder next to the running
    executable (when frozen) or next to the project during development.
    """
    if log_dir is None:
        log_dir = resource_path('logs')

    # Create logs directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)
    
    # Create a unique log file name with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"app_{timestamp}.log")
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()  # Also log to console
        ]
    )
    
    # Get logger for this module
    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized. Log file: {log_file}")
    
    return logger