"""
Audit logging utilities for multi-tenant application
"""
from flask import request
from app.models_multitenant import AuditLog
from app.middleware import get_tenant_id, get_usuario_id
import json
import logging

logger = logging.getLogger(__name__)


def log_audit(accion: str, entidad_tipo: str, entidad_id: int, detalles: dict = None, db_session=None):
    """
    Create an audit log entry
    
    Args:
        accion: Action performed (CREATE, UPDATE, DELETE, READ)
        entidad_tipo: Type of entity (Usuario, Producto, Vale, etc.)
        entidad_id: ID of the entity
        detalles: Additional details as dictionary (will be JSON encoded)
        db_session: SQLAlchemy session (required)
    
    Returns:
        AuditLog instance or None if error
    """
    if not db_session:
        logger.error("db_session is required for audit logging")
        return None
    
    try:
        tenant_id = get_tenant_id()
        usuario_id = get_usuario_id()
        
        if not tenant_id:
            logger.warning(f"Audit log created without tenant context: {accion} {entidad_tipo} {entidad_id}")
            # Use default tenant for system operations
            tenant_id = 1
        
        # Get request context
        ip_address = request.remote_addr if request else None
        user_agent = request.headers.get('User-Agent', '')[:500] if request else None
        
        # Create audit log
        audit_entry = AuditLog(
            tenant_id=tenant_id,
            usuario_id=usuario_id,
            accion=accion,
            entidad_tipo=entidad_tipo,
            entidad_id=entidad_id,
            detalles=json.dumps(detalles) if detalles else None,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db_session.add(audit_entry)
        logger.info(
            f"Audit log: tenant={tenant_id}, usuario={usuario_id}, "
            f"action={accion}, entity={entidad_tipo}:{entidad_id}"
        )
        
        return audit_entry
        
    except Exception as e:
        logger.error(f"Failed to create audit log: {str(e)}")
        return None
