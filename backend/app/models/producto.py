from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.sql import func

from app.db.base import Base


class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False, index=True)
    codigo = Column(String(100), nullable=True, unique=True, index=True)
    tipo = Column(String(50), nullable=False, default="consumible")
    cantidad = Column(Integer, nullable=False, default=0)
    ubicacion = Column(String(200), nullable=True)

    precio = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
