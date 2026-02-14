"""
Flask application initialization.
Sets up logging, middleware, and registers blueprints.
"""
from flask import Flask
from app.logging_config import setup_logging
from app.middleware import init_request_id_middleware
from app.database import Base, engine


def create_app(config=None):
    """
    Create and configure the Flask application.
    
    Args:
        config (dict, optional): Configuration dictionary
    
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    if config:
        app.config.update(config)
    
    # Setup logging first
    setup_logging(app)
    
    # Initialize middleware
    init_request_id_middleware(app)
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    # Register blueprints
    from app.routes.epp import epp_bp
    from app.routes.consumables import consumables_bp
    
    app.register_blueprint(epp_bp, url_prefix="/api")
    app.register_blueprint(consumables_bp, url_prefix="/api")
    
    return app

