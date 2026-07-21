import logging
import os
from datetime import datetime
from config import Config

def setup_logger() -> logging.Logger:
    """
    Configures and returns a logger instance that logs to both console and a file.
    
    Returns:
        logging.Logger: Configured logger.
    """
    logger = logging.getLogger("AttendanceBot")
    logger.setLevel(logging.INFO)

    # Prevent adding handlers multiple times if logger is instantiated again
    if logger.hasHandlers():
        return logger

    # Log format
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler
    date_str = datetime.now().strftime("%Y-%m-%d")
    log_file_path = os.path.join(Config.LOG_DIR, f"attendance_bot_{date_str}.log")
    
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

# Global logger instance
logger = setup_logger()
