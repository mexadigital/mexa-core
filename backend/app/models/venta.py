from datetime import datetime
from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime
from app.db.base import Base


class Venta(Base):
    __tablename__ = "ventas"

    id = Column(Integer, primary_key=True, index=True)
    organizacion_id = Column(Integer, nullable=False, index=True)

    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False, index=True)
    ubicacion_id = Column(Integer, ForeignKey("ubicaciones.id"), nullable=False, index=True)

    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Float, nullable=False)
    total = Column(Float, nullable=False)

    usuario_id = Column(Integer, nullable=False, index=True)
    fecha = Column(DateTime, default=datetime.utcnow, nullable=False)
