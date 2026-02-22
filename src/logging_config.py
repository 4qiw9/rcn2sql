import logging
import os
from datetime import datetime


def setup_logging(log_file: str = None) -> logging.Logger:
    """
    Setup logging to console and file.

    Args:
        log_file: Optional path to log file. If None, generates name with timestamp.
                  If a relative path is provided, it is placed under ./log/.

    Returns:
        Configured logger instance.
    """
    log_dir = os.path.join(os.getcwd(), "log")
    os.makedirs(log_dir, exist_ok=True)

    if log_file is None:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_file = os.path.join(log_dir, f"{timestamp}.log")
    elif not os.path.isabs(log_file):
        log_file = os.path.join(log_dir, log_file)

    # Get or create root logger for rcn (all sub-loggers inherit)
    logger = logging.getLogger("rcn")

    # Clear any existing handlers to avoid duplicates
    logger.handlers = []
    logger.setLevel(logging.DEBUG)
    logger.propagate = False  # Don't propagate to root logger

    # Format
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console handler (INFO and above)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (DEBUG and above)
    file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

