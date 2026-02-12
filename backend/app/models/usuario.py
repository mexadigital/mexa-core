from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class Usuario(db.Model):
    """Usuario model for authentication"""
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    nombre_completo = db.Column(db.String(200))
    rol = db.Column(db.String(20), nullable=False, default='usuario')  # 'admin' or 'usuario'
    activo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    vales = db.relationship('Vale', backref='usuario', lazy='dynamic')
    
    def __init__(self, username, email, password, nombre_completo=None, rol='usuario'):
        self.username = username
        self.email = email
        self.set_password(password)
        self.nombre_completo = nombre_completo
        self.rol = rol
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Serialize user object"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'nombre_completo': self.nombre_completo,
            'rol': self.rol,
            'activo': self.activo,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Usuario {self.username}>'
