"""
Audit log model for tracking all critical actions in the system.
Records user actions, resource changes, and maintains compliance trail.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
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
    
    # User information
    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    
    # Action information
    action = Column(String(50), nullable=False, index=True)  # create, update, delete, login_failed, etc.
    resource_type = Column(String(50), nullable=False, index=True)  # vale, producto, usuario, etc.
    resource_id = Column(Integer, nullable=True, index=True)
    
    # Change tracking
    old_values = Column(JSON, nullable=True)  # State before change
    new_values = Column(JSON, nullable=True)  # State after change
    
    # Request context
    endpoint = Column(String(255), nullable=True)  # /api/vales, /api/productos, etc.
    method = Column(String(10), nullable=True)  # POST, PUT, DELETE, GET
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6 address
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = relationship('User', foreign_keys=[user_id], backref='audit_logs')
    
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
