import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


class CustomLogger:
    _is_initialized = False

    logger: logging.Logger = None

    @classmethod
    def init(cls, log_dir: str, file_level=logging.INFO, console_level=logging.WARNING):
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)

        # Remove existing logger if already initialized
        if cls._is_initialized and cls.logger is not None:
            return

        # Set up logging
        cls.logger = logging.getLogger("custom_logger")
        cls.logger.setLevel(logging.DEBUG)  # Set to lowest level to let handlers control
        cls.logger.propagate = False  # Prevent propagation to root logger

        log_file = log_dir / f"custom_logger__{datetime.now().strftime('%H-%M-%S')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter("%(asctime)s | %(name)s | %(levelname)s | %(message)s"))
        file_handler.setLevel(file_level)
        cls.logger.addHandler(file_handler)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        console_handler.setLevel(console_level)
        cls.logger.addHandler(console_handler)

        # Log initial message to verify setup
        cls.logger.debug(f"Logger initialized with log file: {log_file}")

        cls._is_initialized = True

    @classmethod
    def log_event(cls, event_type: str, data: Dict[str, Any]):
        """Log a custom event with structured data"""
        try:
            cls.logger.info(f"Event: {event_type} {' '*(20-len(event_type))} | Data: {json.dumps(data)}")
        except Exception as e:
            cls.logger.info(f"Event: {event_type} {' '*(20-len(event_type))} | Data: {str(data)}")
