from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.db.base import Base


class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    organizacion_id = Column(Integer, ForeignKey("organizaciones.id"), nullable=False)
    nombre = Column(String, nullable=False)
    codigo = Column(String, nullable=False, index=True)
    tipo = Column(String, nullable=False)
    cantidad = Column(Integer, default=0)
    ubicacion = Column(String, nullable=True)
    precio = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
