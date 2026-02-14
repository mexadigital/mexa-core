"""
Logging configuration for Mexa application.
Provides structured JSON logging with multiple handlers for different log levels.
"""
import logging
import os
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter that includes standard fields."""
    
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        log_record['timestamp'] = self.formatTime(record, self.datefmt)
        log_record['level'] = record.levelname
        log_record['logger'] = record.name
        log_record['module'] = record.module
        log_record['function'] = record.funcName
        log_record['line'] = record.lineno


def setup_logging(app):
    """
    Configure application logging with JSON formatter and multiple handlers.
    
    Args:
        app: Flask application instance
    """
    # Get log level from environment, default to INFO in production, DEBUG in development
    log_level_str = os.getenv('LOG_LEVEL', 'DEBUG' if app.config.get('DEBUG') else 'INFO')
    log_level = getattr(logging, log_level_str.upper(), logging.INFO)
    
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    # Create custom JSON formatter
    json_formatter = CustomJsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s'
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove any existing handlers
    root_logger.handlers.clear()
    
    # STDOUT handler - INFO level for development/Docker
    stdout_handler = logging.StreamHandler()
    stdout_handler.setLevel(logging.INFO)
    stdout_handler.setFormatter(json_formatter)
    root_logger.addHandler(stdout_handler)
    
    # Main log file handler - DEBUG+ (rotating file, 10MB max, 10 backups)
    main_log_file = os.path.join(logs_dir, 'mexa.log')
    main_file_handler = RotatingFileHandler(
        main_log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10
    )
    main_file_handler.setLevel(logging.DEBUG)
    main_file_handler.setFormatter(json_formatter)
    root_logger.addHandler(main_file_handler)
    
    # Error log file handler - ERROR+ (rotating file, 10MB max, 10 backups)
    error_log_file = os.path.join(logs_dir, 'mexa-error.log')
    error_file_handler = RotatingFileHandler(
        error_log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10
    )
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(json_formatter)
    root_logger.addHandler(error_file_handler)
    
    # Log configuration complete
    app.logger.info(
        'Logging configuration complete',
        extra={
            'log_level': log_level_str,
            'logs_dir': logs_dir,
            'handlers': ['stdout', 'main_file', 'error_file']
        }
    )
