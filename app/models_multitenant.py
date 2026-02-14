"""
Multi-tenant database models for Mexa Core

This module defines the core models with multi-tenant support:
- Tenant: Multi-tenant organizations
- Usuario: Users scoped to tenants
- Producto: Products scoped to tenants  
- Vale: Vouchers/orders scoped to tenants
- AuditLog: Audit trail with tenant tracking
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey,
    Text, Numeric, UniqueConstraint, Index, CheckConstraint
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class Tenant(Base):
    """Multi-tenant organization model"""
    __tablename__ = 'tenants'
    
    id = Column(Integer, primary_key=True)
    slug = Column(String(50), unique=True, nullable=False, index=True)
    nombre = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    plan = Column(String(50), nullable=False, server_default='basic')
    activo = Column(Boolean, nullable=False, server_default='true')
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    usuarios = relationship('Usuario', back_populates='tenant', lazy='dynamic')
    productos = relationship('Producto', back_populates='tenant', lazy='dynamic')
    vales = relationship('Vale', back_populates='tenant', lazy='dynamic')
    audit_logs = relationship('AuditLog', back_populates='tenant', lazy='dynamic')
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'slug': self.slug,
            'nombre': self.nombre,
            'email': self.email,
            'plan': self.plan,
            'activo': self.activo,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class Usuario(Base):
    """User model with multi-tenant support"""
    __tablename__ = 'usuarios'
    
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=False, index=True)
    email = Column(String(255), nullable=False)
    nombre = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    activo = Column(Boolean, nullable=False, server_default='true')
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    tenant = relationship('Tenant', back_populates='usuarios')
    vales = relationship('Vale', back_populates='usuario', lazy='dynamic')
    
    # Table arguments - unique constraint and indexes
    __table_args__ = (
        UniqueConstraint('tenant_id', 'email', name='uq_usuarios_tenant_email'),
        Index('ix_usuarios_tenant_id', 'tenant_id'),
    )
    
    def to_dict(self, include_tenant=False):
        """Convert model to dictionary"""
        data = {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'email': self.email,
            'nombre': self.nombre,
            'activo': self.activo,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_tenant and self.tenant:
            data['tenant'] = self.tenant.to_dict()
        return data


class Producto(Base):
    """Product model with multi-tenant support"""
    __tablename__ = 'productos'
    
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=False, index=True)
    nombre = Column(String(255), nullable=False)
    descripcion = Column(Text)
    sku = Column(String(100))
    precio = Column(Numeric(10, 2), nullable=False, server_default='0')
    stock = Column(Integer, nullable=False, server_default='0')
    activo = Column(Boolean, nullable=False, server_default='true')
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    tenant = relationship('Tenant', back_populates='productos')
    
    # Table arguments - unique constraint, indexes and check constraint
    __table_args__ = (
        UniqueConstraint('tenant_id', 'nombre', name='uq_productos_tenant_nombre'),
        Index('ix_productos_tenant_id', 'tenant_id'),
        Index('ix_productos_tenant_sku', 'tenant_id', 'sku'),
        CheckConstraint('stock >= 0', name='ck_productos_stock_non_negative'),
    )
    
    def to_dict(self, include_tenant=False):
        """Convert model to dictionary"""
        data = {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'sku': self.sku,
            'precio': float(self.precio) if self.precio else 0.0,
            'stock': self.stock,
            'activo': self.activo,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_tenant and self.tenant:
            data['tenant'] = self.tenant.to_dict()
        return data


class Vale(Base):
    """Voucher/Order model with multi-tenant support"""
    __tablename__ = 'vales'
    
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=False, index=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    producto_id = Column(Integer, ForeignKey('productos.id'), nullable=False)
    request_id = Column(String(100), unique=True, nullable=False)  # Idempotency key
    cantidad = Column(Integer, nullable=False)
    monto_total = Column(Numeric(10, 2), nullable=False)
    estado = Column(String(50), nullable=False, server_default='pendiente')  # pendiente, completado, cancelado
    comentario = Column(Text)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    tenant = relationship('Tenant', back_populates='vales')
    usuario = relationship('Usuario', back_populates='vales')
    producto = relationship('Producto')
    
    # Table arguments - indexes and constraints
    __table_args__ = (
        Index('ix_vales_tenant_id', 'tenant_id'),
        Index('ix_vales_request_id', 'request_id'),
        Index('ix_vales_tenant_estado', 'tenant_id', 'estado'),
        CheckConstraint('cantidad > 0', name='ck_vales_cantidad_positive'),
    )
    
    def to_dict(self, include_relations=False):
        """Convert model to dictionary"""
        data = {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'usuario_id': self.usuario_id,
            'producto_id': self.producto_id,
            'request_id': self.request_id,
            'cantidad': self.cantidad,
            'monto_total': float(self.monto_total) if self.monto_total else 0.0,
            'estado': self.estado,
            'comentario': self.comentario,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_relations:
            if self.usuario:
                data['usuario'] = self.usuario.to_dict()
            if self.producto:
                data['producto'] = self.producto.to_dict()
            if self.tenant:
                data['tenant'] = self.tenant.to_dict()
        return data


class AuditLog(Base):
    """Audit log model with multi-tenant support"""
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=False, index=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=True)
    accion = Column(String(100), nullable=False)
    entidad_tipo = Column(String(100), nullable=False)  # Usuario, Producto, Vale, etc.
    entidad_id = Column(Integer, nullable=False)
    detalles = Column(Text)  # JSON string with details
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    
    # Relationships
    tenant = relationship('Tenant', back_populates='audit_logs')
    usuario = relationship('Usuario')
    
    # Table arguments - indexes
    __table_args__ = (
        Index('ix_audit_logs_tenant_id', 'tenant_id'),
        Index('ix_audit_logs_tenant_entidad', 'tenant_id', 'entidad_tipo', 'entidad_id'),
        Index('ix_audit_logs_created_at', 'created_at'),
    )
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'usuario_id': self.usuario_id,
            'accion': self.accion,
            'entidad_tipo': self.entidad_tipo,
            'entidad_id': self.entidad_id,
            'detalles': self.detalles,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
