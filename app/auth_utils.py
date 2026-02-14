"""
Authentication utilities for multi-tenant application
"""
from passlib.hash import bcrypt
from flask_jwt_extended import create_access_token
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt
    
    Args:
        password: Plain text password
    
    Returns:
        Hashed password string
    """
    return bcrypt.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify a password against its hash
    
    Args:
        password: Plain text password to verify
        password_hash: Stored password hash
    
    Returns:
        True if password matches, False otherwise
    """
    try:
        return bcrypt.verify(password, password_hash)
    except Exception as e:
        logger.error(f"Password verification error: {str(e)}")
        return False


def generate_token(usuario_id: int, tenant_id: int, email: str) -> str:
    """
    Generate JWT access token with tenant context
    
    Args:
        usuario_id: User ID
        tenant_id: Tenant ID
        email: User email
    
    Returns:
        JWT access token string
    """
    additional_claims = {
        'tenant_id': tenant_id,
        'email': email
    }
    
    access_token = create_access_token(
        identity=usuario_id,
        additional_claims=additional_claims
    )
    
    logger.info(f"Generated token for usuario_id={usuario_id}, tenant_id={tenant_id}")
    
    return access_token
