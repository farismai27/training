"""
Logging configuration for production monitoring
"""

import logging
import json
import sys
from datetime import datetime
from pathlib import Path


class JSONFormatter(logging.Formatter):
    """Format logs as JSON for easier parsing in production."""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }

        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        # Add extra fields if present
        if hasattr(record, 'extra_data'):
            log_data.update(record.extra_data)

        return json.dumps(log_data)


def setup_logging(
    name: str = "mcp_server",
    log_file: str = None,
    level: int = logging.INFO,
    json_format: bool = False
) -> logging.Logger:
    """
    Set up structured logging for the application.

    Args:
        name: Logger name
        log_file: Path to log file (if None, logs to stdout only)
        level: Logging level
        json_format: Use JSON formatting for production

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Remove existing handlers
    logger.handlers = []

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    if json_format:
        console_handler.setFormatter(JSONFormatter())
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        # Ensure logs directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)

        if json_format:
            file_handler.setFormatter(JSONFormatter())
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)

    return logger


# Create default logger
default_logger = setup_logging()


def log_error(logger: logging.Logger, error: Exception, context: dict = None):
    """
    Log an error with additional context.

    Args:
        logger: Logger instance
        error: Exception to log
        context: Additional context data
    """
    extra_data = {
        'error_type': type(error).__name__,
        'error_message': str(error)
    }

    if context:
        extra_data.update(context)

    logger.error(
        f"Error occurred: {error}",
        exc_info=True,
        extra={'extra_data': extra_data}
    )


def log_performance(logger: logging.Logger, operation: str, duration: float, **kwargs):
    """
    Log performance metrics.

    Args:
        logger: Logger instance
        operation: Name of the operation
        duration: Duration in seconds
        **kwargs: Additional metrics
    """
    extra_data = {
        'operation': operation,
        'duration_seconds': duration,
        **kwargs
    }

    logger.info(
        f"Performance: {operation} took {duration:.3f}s",
        extra={'extra_data': extra_data}
    )
