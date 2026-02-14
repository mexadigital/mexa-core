"""
Request ID middleware for tracking requests throughout their lifecycle.
Generates unique request IDs, logs request entry/exit, and handles errors.
"""
import logging
import time
import uuid
import traceback
from flask import g, request, jsonify
from functools import wraps

logger = logging.getLogger(__name__)


def init_request_id_middleware(app):
    """
    Initialize request ID middleware for the Flask application.
    
    Args:
        app: Flask application instance
    """
    
    @app.before_request
    def before_request_handler():
        """Generate or extract request ID and log request entry."""
        # Generate or extract request ID from header
        request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
        g.request_id = request_id
        g.start_time = time.time()
        
        # Get client IP address
        if request.headers.get('X-Forwarded-For'):
            g.ip_address = request.headers.get('X-Forwarded-For').split(',')[0].strip()
        else:
            g.ip_address = request.remote_addr or 'unknown'
        
        # Log request entry
        logger.info(
            'Request started',
            extra={
                'request_id': request_id,
                'method': request.method,
                'path': request.path,
                'ip_address': g.ip_address,
                'user_agent': request.headers.get('User-Agent', 'unknown')
            }
        )
    
    @app.after_request
    def after_request_handler(response):
        """Log request exit and add request ID to response headers."""
        if hasattr(g, 'request_id'):
            # Calculate request duration
            duration = None
            if hasattr(g, 'start_time'):
                duration = time.time() - g.start_time
            
            # Log request exit
            logger.info(
                'Request completed',
                extra={
                    'request_id': g.request_id,
                    'method': request.method,
                    'path': request.path,
                    'status_code': response.status_code,
                    'duration': duration,
                    'ip_address': g.ip_address if hasattr(g, 'ip_address') else 'unknown'
                }
            )
            
            # Add request ID to response headers
            response.headers['X-Request-ID'] = g.request_id
        
        return response
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        """Handle exceptions with full stack traces and context."""
        request_id = g.request_id if hasattr(g, 'request_id') else 'unknown'
        ip_address = g.ip_address if hasattr(g, 'ip_address') else 'unknown'
        
        # Log error with full stack trace
        logger.error(
            f'Unhandled exception: {str(error)}',
            extra={
                'request_id': request_id,
                'method': request.method,
                'path': request.path,
                'ip_address': ip_address,
                'error_type': type(error).__name__,
                'stack_trace': traceback.format_exc()
            },
            exc_info=True
        )
        
        # Return JSON error response
        response = jsonify({
            'error': 'Internal server error',
            'message': str(error),
            'request_id': request_id
        })
        response.status_code = 500
        response.headers['X-Request-ID'] = request_id
        return response
    
    @app.errorhandler(404)
    def handle_not_found(error):
        """Handle 404 errors."""
        request_id = g.request_id if hasattr(g, 'request_id') else 'unknown'
        
        logger.warning(
            'Resource not found',
            extra={
                'request_id': request_id,
                'method': request.method,
                'path': request.path,
                'ip_address': g.ip_address if hasattr(g, 'ip_address') else 'unknown'
            }
        )
        
        response = jsonify({
            'error': 'Not found',
            'message': 'The requested resource was not found',
            'request_id': request_id
        })
        response.status_code = 404
        response.headers['X-Request-ID'] = request_id
        return response
