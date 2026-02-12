from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from app.config import config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
mail = Mail()

def create_app(config_name='default'):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)
    CORS(app)
    
    # Register blueprints
    from app.routes import auth, vales, dashboard, reportes, productos
    
    app.register_blueprint(auth.bp, url_prefix='/api/auth')
    app.register_blueprint(vales.bp, url_prefix='/api/vales')
    app.register_blueprint(dashboard.bp, url_prefix='/api/dashboard')
    app.register_blueprint(reportes.bp, url_prefix='/api/reportes')
    app.register_blueprint(productos.bp, url_prefix='/api/productos')
    
    # Health check endpoint
    @app.route('/health')
    def health():
        return {'status': 'healthy'}, 200
    
    return app
