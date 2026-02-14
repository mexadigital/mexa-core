"""
Flask application entry point for MEXA Core
"""
from flask import Flask, jsonify, request
import os
import logging
from datetime import datetime

# Configure logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
app.config['DATABASE_HOST'] = os.getenv('DATABASE_HOST', 'db')
app.config['DATABASE_PORT'] = os.getenv('DATABASE_PORT', '5432')
app.config['DATABASE_NAME'] = os.getenv('DATABASE_NAME', 'mexa_db')
app.config['DATABASE_USER'] = os.getenv('DATABASE_USER', 'mexa_user')
app.config['DATABASE_PASSWORD'] = os.getenv('DATABASE_PASSWORD', 'mexa_pass')


@app.route('/')
def index():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'service': 'MEXA Core',
        'timestamp': datetime.utcnow().isoformat()
    })


@app.route('/health')
def health():
    """Detailed health check"""
    return jsonify({
        'status': 'healthy',
        'service': 'MEXA Core',
        'timestamp': datetime.utcnow().isoformat(),
        'database': {
            'host': app.config['DATABASE_HOST'],
            'port': app.config['DATABASE_PORT'],
            'database': app.config['DATABASE_NAME']
        }
    })


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested resource was not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f'Internal server error: {error}')
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An internal server error occurred'
    }), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
