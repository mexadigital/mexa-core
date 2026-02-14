"""
Audit log model for tracking all critical actions in the system.
Records user actions, resource changes, and maintains compliance trail.
"""
from sqlalchemy import Column, Integer, String, DateTime, Index, Text
from sqlalchemy.types import JSON as GenericJSON
from sqlalchemy.sql import func
from datetime import datetime, timezone
import uuid
from app.database import Base


class AuditLog(Base):
    """
    Audit log table for tracking all critical system actions.
    
    Stores comprehensive information about user actions, resource changes,
    and maintains a complete audit trail for compliance and debugging.
    """
    __tablename__ = 'audit_logs'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Request tracking
    request_id = Column(String(36), unique=True, nullable=False, index=True)
    
    # User information - nullable integer, no foreign key constraint for flexibility
    user_id = Column(Integer, nullable=True, index=True)
    
    # Action information
    action = Column(String(50), nullable=False, index=True)  # create, update, delete, login_failed, etc.
    resource_type = Column(String(50), nullable=False, index=True)  # vale, producto, usuario, etc.
    resource_id = Column(Integer, nullable=True, index=True)
    
    # Change tracking - Use GenericJSON for compatibility with SQLite
    old_values = Column(GenericJSON, nullable=True)  # State before change
    new_values = Column(GenericJSON, nullable=True)  # State after change
    
    # Request context
    endpoint = Column(String(255), nullable=True)  # /api/vales, /api/productos, etc.
    method = Column(String(10), nullable=True)  # POST, PUT, DELETE, GET
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6 address
    
    # Timestamp - using timezone-aware datetime
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    
    # Composite indexes for common queries
    __table_args__ = (
        Index('idx_audit_user_action', 'user_id', 'action'),
        Index('idx_audit_resource', 'resource_type', 'resource_id'),
        Index('idx_audit_created_at', 'created_at'),
    )
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, resource_type={self.resource_type}, resource_id={self.resource_id})>"
    
    def to_dict(self):
        """Convert audit log to dictionary representation."""
        return {
            'id': self.id,
            'request_id': self.request_id,
            'user_id': self.user_id,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'old_values': self.old_values,
            'new_values': self.new_values,
            'endpoint': self.endpoint,
            'method': self.method,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
