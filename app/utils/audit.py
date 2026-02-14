"""
Audit utility functions for logging critical actions to both database and logs.
Provides centralized audit logging with automatic context capture.
"""
import logging
import uuid
from flask import g, request
from app.database import SessionLocal
from app.models.audit_log import AuditLog

logger = logging.getLogger(__name__)


def log_audit(action, resource_type, resource_id=None, old_values=None, new_values=None, user_id=None):
    """
    Log an audit entry to both the database and application logs.
    
    Automatically captures request context (request_id, endpoint, method, ip_address)
    from Flask's g object. Safe error handling ensures audit failures don't break
    the main application flow.
    
    Args:
        action (str): The action being performed (e.g., 'create', 'update', 'delete', 
                     'login_success', 'login_failed', 'adjust_stock')
        resource_type (str): Type of resource being acted upon (e.g., 'vale', 'producto', 
                            'usuario', 'epp', 'consumable')
        resource_id (int, optional): ID of the resource being acted upon
        old_values (dict, optional): Dictionary of old values before the change
        new_values (dict, optional): Dictionary of new values after the change
        user_id (int, optional): ID of the user performing the action (auto-captured if available)
    
    Returns:
        AuditLog: The created audit log entry, or None if an error occurred
    
    Example:
        >>> log_audit('create', 'epp', epp.id, new_values={'name': 'Safety Helmet', 'description': 'Hard hat'})
        >>> log_audit('update', 'consumable', consumable.id, 
        ...           old_values={'quantity': 10}, new_values={'quantity': 15})
        >>> log_audit('delete', 'epp', epp.id, old_values={'name': 'Old Item'})
    """
    try:
        # Capture context from Flask g object
        # If request_id not available, generate a new UUID to ensure unique identification
        request_id = g.request_id if hasattr(g, 'request_id') else str(uuid.uuid4())
        ip_address = g.ip_address if hasattr(g, 'ip_address') else None
        
        # If ip_address not in g, try to get from request
        if not ip_address and request:
            if request.headers.get('X-Forwarded-For'):
                ip_address = request.headers.get('X-Forwarded-For').split(',')[0].strip()
            else:
                ip_address = request.remote_addr or 'unknown'
        
        # Capture endpoint and method
        endpoint = request.path if request else None
        method = request.method if request else None
        
        # Use provided user_id or try to get from g
        if user_id is None and hasattr(g, 'user_id'):
            user_id = g.user_id
        
        # Create audit log entry
        db = SessionLocal()
        try:
            audit_entry = AuditLog(
                request_id=request_id,
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                old_values=old_values,
                new_values=new_values,
                endpoint=endpoint,
                method=method,
                ip_address=ip_address
            )
            
            db.add(audit_entry)
            db.commit()
            db.refresh(audit_entry)
            
            # Also log to application logs
            logger.info(
                f'Audit: {action} {resource_type}',
                extra={
                    'request_id': request_id,
                    'user_id': user_id,
                    'action': action,
                    'resource_type': resource_type,
                    'resource_id': resource_id,
                    'endpoint': endpoint,
                    'method': method,
                    'ip_address': ip_address,
                    'audit_id': audit_entry.id
                }
            )
            
            return audit_entry
            
        finally:
            db.close()
            
    except Exception as e:
        # Log the error but don't raise it - audit failures shouldn't break the app
        logger.error(
            f'Failed to create audit log: {str(e)}',
            extra={
                'action': action,
                'resource_type': resource_type,
                'resource_id': resource_id,
                'error': str(e)
            },
            exc_info=True
        )
        return None


def get_audit_logs(resource_type=None, resource_id=None, user_id=None, action=None, 
                   limit=100, offset=0):
    """
    Query audit logs with optional filters.
    
    Args:
        resource_type (str, optional): Filter by resource type
        resource_id (int, optional): Filter by resource ID
        user_id (int, optional): Filter by user ID
        action (str, optional): Filter by action type
        limit (int): Maximum number of records to return (default: 100)
        offset (int): Number of records to skip (default: 0)
    
    Returns:
        list: List of AuditLog entries matching the filters
    """
    db = SessionLocal()
    try:
        query = db.query(AuditLog)
        
        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)
        if resource_id is not None:
            query = query.filter(AuditLog.resource_id == resource_id)
        if user_id is not None:
            query = query.filter(AuditLog.user_id == user_id)
        if action:
            query = query.filter(AuditLog.action == action)
        
        query = query.order_by(AuditLog.created_at.desc())
        query = query.limit(limit).offset(offset)
        
        return query.all()
        
    finally:
        db.close()
