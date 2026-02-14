"""
Application entry point.
Creates and runs the Flask application.
"""
from app import create_app
import os

if __name__ == '__main__':
    # Get configuration from environment
    debug = os.getenv('FLASK_ENV', 'production') == 'development'
    
    app = create_app({'DEBUG': debug})
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=debug
    )
