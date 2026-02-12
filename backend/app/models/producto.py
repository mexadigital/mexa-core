from app import db
from datetime import datetime


class Producto(db.Model):
    """Producto model - Catalog of EPP and consumables"""
    __tablename__ = 'productos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False, unique=True, index=True)
    descripcion = db.Column(db.Text)
    categoria = db.Column(db.String(50))  # EPP, Consumible, Herramienta, etc.
    unidad_medida = db.Column(db.String(20), default='unidad')  # unidad, par, pieza, etc.
    stock_minimo = db.Column(db.Integer, default=10)
    activo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    vales = db.relationship('Vale', backref='producto', lazy='dynamic')
    
    def __init__(self, nombre, descripcion=None, categoria=None, unidad_medida='unidad', stock_minimo=10):
        self.nombre = nombre
        self.descripcion = descripcion
        self.categoria = categoria
        self.unidad_medida = unidad_medida
        self.stock_minimo = stock_minimo
    
    def to_dict(self):
        """Serialize product object"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'categoria': self.categoria,
            'unidad_medida': self.unidad_medida,
            'stock_minimo': self.stock_minimo,
            'activo': self.activo,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Producto {self.nombre}>'
