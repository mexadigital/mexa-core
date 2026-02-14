"""
Configuration for Flask application with multi-tenant support
"""
import os
from pathlib import Path

class Config:
    """Base configuration"""
    
    # Database
    DB_DIR = Path(os.getenv("DB_DIR", "data"))
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{DB_DIR / 'app.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = os.getenv("SQL_DEBUG", "False").lower() == "true"
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour
    JWT_ALGORITHM = "HS256"
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-in-production")
    
    # Application
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    TESTING = False


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_ECHO = False


class TestConfig(Config):
    """Test configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestConfig,
    'default': DevelopmentConfig
}
