"""
Logging configuration module for the Binance Futures trading bot.
"""
import os
import logging
from logging.handlers import RotatingFileHandler

def setup_logging() -> logging.Logger:
    """
    Set up the logging configuration.
    Creates a 'logs' directory at the root of the project and configures
    a rotating file logger named 'trading_bot'.
    """
    # Find the root trading_bot directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logs_dir = os.path.join(base_dir, "logs")
    
    # Create logs folder if it doesn't exist
    os.makedirs(logs_dir, exist_ok=True)
    
    log_file = os.path.join(logs_dir, "trading.log")
    
    logger = logging.getLogger("trading_bot")
    logger.setLevel(logging.INFO)
    
    # Avoid duplicate handlers if setup is called multiple times
    if not logger.handlers:
        # Format: timestamp - level - source - message
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        # Set up a rotating file handler (5 MB size limit, 3 backup files)
        file_handler = RotatingFileHandler(
            log_file, 
            maxBytes=5 * 1024 * 1024, 
            backupCount=3,
            encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        
        logger.addHandler(file_handler)
        
        # Suppress excessive logging from third-party libraries
        logging.getLogger("binance").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("requests").setLevel(logging.WARNING)
        
    return logger

# Expose a default logger instance
logger = setup_logging()
