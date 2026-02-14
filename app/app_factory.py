"""
Flask application factory with multi-tenant support and database initialization
"""
from flask import Flask, g
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from app.config import config

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()


def create_app(config_name='default'):
    """
    Application factory pattern
    
    Args:
        config_name: Configuration to use (default, development, production, testing)
    
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Ensure data directory exists
    config[config_name].DB_DIR.mkdir(parents=True, exist_ok=True)
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    
    # Register blueprints
    from app.routes_multitenant import auth_bp, vales_bp, productos_bp, usuarios_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(vales_bp, url_prefix='/api/vales')
    app.register_blueprint(productos_bp, url_prefix='/api/productos')
    app.register_blueprint(usuarios_bp, url_prefix='/api/usuarios')
    
    # Create database tables
    with app.app_context():
        from app.models_multitenant import Base, Tenant, Usuario, Producto, Vale, AuditLog
        db.create_all()
        
        # Initialize default tenant if not exists
        if not Tenant.query.filter_by(id=1).first():
            default_tenant = Tenant(
                id=1,
                slug='default',
                nombre='Default Tenant',
                email='admin@mexa.local',
                plan='pro',
                activo=True
            )
            db.session.add(default_tenant)
            db.session.commit()
    
    # Logging middleware
    @app.before_request
    def log_request():
        """Log all requests with tenant context"""
        tenant_id = getattr(g, 'tenant_id', None)
        app.logger.info(f"Request: {g.get('request_method', 'UNKNOWN')} {g.get('request_path', 'UNKNOWN')} | Tenant: {tenant_id}")
    
    # Health check endpoint
    @app.route('/health')
    def health():
        return {'status': 'healthy'}, 200
    
    return app
