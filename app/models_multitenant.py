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
from sqlalchemy import UniqueConstraint, Index, CheckConstraint
from sqlalchemy.sql import func


def init_models(db):
    """
    Initialize models with database instance
    
    Args:
        db: Flask-SQLAlchemy database instance
    
    Returns:
        Tuple of (Tenant, Usuario, Producto, Vale, AuditLog) model classes
    """
    
    class Tenant(db.Model):
        """Multi-tenant organization model"""
        __tablename__ = 'tenants'
        
        id = db.Column(db.Integer, primary_key=True)
        slug = db.Column(db.String(50), unique=True, nullable=False)
        nombre = db.Column(db.String(255), nullable=False)
        email = db.Column(db.String(255), nullable=False)
        plan = db.Column(db.String(50), nullable=False, server_default='basic')
        activo = db.Column(db.Boolean, nullable=False, server_default='true')
        created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
        updated_at = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
        
        # Relationships
        usuarios = db.relationship('Usuario', back_populates='tenant', lazy='dynamic')
        productos = db.relationship('Producto', back_populates='tenant', lazy='dynamic')
        vales = db.relationship('Vale', back_populates='tenant', lazy='dynamic')
        audit_logs = db.relationship('AuditLog', back_populates='tenant', lazy='dynamic')
        
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
    
    
    class Usuario(db.Model):
        """User model with multi-tenant support"""
        __tablename__ = 'usuarios'
        
        id = db.Column(db.Integer, primary_key=True)
        tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
        email = db.Column(db.String(255), nullable=False)
        nombre = db.Column(db.String(255), nullable=False)
        password_hash = db.Column(db.String(255), nullable=False)
        activo = db.Column(db.Boolean, nullable=False, server_default='true')
        created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
        updated_at = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
        
        # Relationships
        tenant = db.relationship('Tenant', back_populates='usuarios')
        vales = db.relationship('Vale', back_populates='usuario', lazy='dynamic')
        
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
    
    
    class Producto(db.Model):
        """Product model with multi-tenant support"""
        __tablename__ = 'productos'
        
        id = db.Column(db.Integer, primary_key=True)
        tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
        nombre = db.Column(db.String(255), nullable=False)
        descripcion = db.Column(db.Text)
        sku = db.Column(db.String(100))
        precio = db.Column(db.Numeric(10, 2), nullable=False, server_default='0')
        stock = db.Column(db.Integer, nullable=False, server_default='0')
        activo = db.Column(db.Boolean, nullable=False, server_default='true')
        created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
        updated_at = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
        
        # Relationships
        tenant = db.relationship('Tenant', back_populates='productos')
        
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
    
    
    class Vale(db.Model):
        """Voucher/Order model with multi-tenant support"""
        __tablename__ = 'vales'
        
        id = db.Column(db.Integer, primary_key=True)
        tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
        usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
        producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
        request_id = db.Column(db.String(100), unique=True, nullable=False)  # Idempotency key
        cantidad = db.Column(db.Integer, nullable=False)
        monto_total = db.Column(db.Numeric(10, 2), nullable=False)
        estado = db.Column(db.String(50), nullable=False, server_default='pendiente')  # pendiente, completado, cancelado
        comentario = db.Column(db.Text)
        created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
        updated_at = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
        
        # Relationships
        tenant = db.relationship('Tenant', back_populates='vales')
        usuario = db.relationship('Usuario', back_populates='vales')
        producto = db.relationship('Producto')
        
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
    
    
    class AuditLog(db.Model):
        """Audit log model with multi-tenant support"""
        __tablename__ = 'audit_logs'
        
        id = db.Column(db.Integer, primary_key=True)
        tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
        usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
        accion = db.Column(db.String(100), nullable=False)
        entidad_tipo = db.Column(db.String(100), nullable=False)  # Usuario, Producto, Vale, etc.
        entidad_id = db.Column(db.Integer, nullable=False)
        detalles = db.Column(db.Text)  # JSON string with details
        ip_address = db.Column(db.String(50))
        user_agent = db.Column(db.String(500))
        created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
        
        # Relationships
        tenant = db.relationship('Tenant', back_populates='audit_logs')
        usuario = db.relationship('Usuario')
        
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
    
    return Tenant, Usuario, Producto, Vale, AuditLog
