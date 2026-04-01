from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, DateTime
from app.db.base import Base


class Traspaso(Base):
    __tablename__ = "traspasos"

    id = Column(Integer, primary_key=True, index=True)
    organizacion_id = Column(Integer, ForeignKey("organizaciones.id"), nullable=False, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False, index=True)
    ubicacion_origen_id = Column(Integer, ForeignKey("ubicaciones.id"), nullable=False, index=True)
    ubicacion_destino_id = Column(Integer, ForeignKey("ubicaciones.id"), nullable=False, index=True)
    cantidad = Column(Integer, nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    fecha = Column(DateTime, default=datetime.utcnow, nullable=False)
