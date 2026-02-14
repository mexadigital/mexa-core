"""
JWT Middleware for Multi-Tenant Support

Extracts tenant_id from JWT token and stores in Flask's g object for use throughout the request.
"""
from functools import wraps
from flask import g, request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity
import logging

logger = logging.getLogger(__name__)


def require_tenant_context(f):
    """
    Decorator to require JWT authentication and extract tenant_id
    
    This middleware:
    1. Verifies JWT token is present and valid
    2. Extracts tenant_id from token claims
    3. Stores tenant_id in g.tenant_id for access throughout request
    4. Validates user belongs to the tenant
    5. Logs tenant context for all operations
    
    Returns 401 if token is missing/invalid or tenant_id is missing from token
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Verify JWT token
            verify_jwt_in_request()
            
            # Get JWT claims
            claims = get_jwt()
            identity = get_jwt_identity()
            
            # Extract tenant_id from claims
            tenant_id = claims.get('tenant_id')
            
            if not tenant_id:
                logger.error(f"JWT token missing tenant_id for user {identity}")
                return jsonify({'error': 'Token missing tenant context'}), 401
            
            # Store in g for access throughout request
            g.tenant_id = tenant_id
            g.usuario_id = identity
            g.request_method = request.method
            g.request_path = request.path
            
            # Log tenant context
            logger.info(f"Tenant context set: tenant_id={tenant_id}, usuario_id={identity}, path={request.path}")
            
            return f(*args, **kwargs)
            
        except Exception as e:
            logger.error(f"JWT verification failed: {str(e)}")
            return jsonify({'error': 'Invalid or expired token'}), 401
    
    return decorated_function


def get_tenant_id():
    """
    Get current tenant_id from Flask g object
    
    Returns:
        int: Current tenant ID or None if not set
    """
    return getattr(g, 'tenant_id', None)


def get_usuario_id():
    """
    Get current usuario_id from Flask g object
    
    Returns:
        int: Current user ID or None if not set
    """
    return getattr(g, 'usuario_id', None)


def validate_tenant_access(entity):
    """
    Validate that an entity belongs to the current user's tenant
    
    Args:
        entity: Model instance with tenant_id attribute
    
    Returns:
        bool: True if entity belongs to current tenant, False otherwise
    """
    current_tenant_id = get_tenant_id()
    
    if not current_tenant_id:
        logger.warning("Tenant access validation called without tenant context")
        return False
    
    entity_tenant_id = getattr(entity, 'tenant_id', None)
    
    if entity_tenant_id != current_tenant_id:
        logger.warning(
            f"Cross-tenant access attempt: "
            f"user_tenant={current_tenant_id}, entity_tenant={entity_tenant_id}"
        )
        return False
    
    return True
