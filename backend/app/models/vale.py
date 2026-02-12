from app import db
from datetime import datetime


class Vale(db.Model):
    """Vale model - Daily consumption records"""
    __tablename__ = 'vales'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign Keys
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False, index=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False, index=True)
    
    # Core fields as per requirements
    disciplina = db.Column(db.String(50), nullable=False, index=True)  # Civil, Mecánica, Eléctrica
    satelite = db.Column(db.String(20), nullable=False, index=True)    # #1, #2, #3
    cantidad_salida = db.Column(db.Integer, nullable=False)
    stock_actual = db.Column(db.Integer, nullable=False)
    observaciones = db.Column(db.Text)
    
    # Metadata
    fecha = db.Column(db.Date, nullable=False, default=datetime.utcnow, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, usuario_id, producto_id, disciplina, satelite, 
                 cantidad_salida, stock_actual, observaciones=None, fecha=None):
        self.usuario_id = usuario_id
        self.producto_id = producto_id
        self.disciplina = disciplina
        self.satelite = satelite
        self.cantidad_salida = cantidad_salida
        self.stock_actual = stock_actual
        self.observaciones = observaciones
        if fecha:
            self.fecha = fecha
    
    def to_dict(self):
        """Serialize vale object"""
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'usuario': self.usuario.username if self.usuario else None,
            'producto_id': self.producto_id,
            'producto': self.producto.nombre if self.producto else None,
            'disciplina': self.disciplina,
            'satelite': self.satelite,
            'cantidad_salida': self.cantidad_salida,
            'stock_actual': self.stock_actual,
            'observaciones': self.observaciones,
            'fecha': self.fecha.isoformat() if self.fecha else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Vale {self.id} - {self.producto.nombre if self.producto else "N/A"} - {self.disciplina}>'
