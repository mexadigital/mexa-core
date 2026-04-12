from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class RequisicionDetalle(Base):
    __tablename__ = "requisicion_detalle"

    id = Column(Integer, primary_key=True, index=True)
    requisicion_id = Column(Integer, ForeignKey("requisiciones.id"), nullable=False, index=True)

    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=True, index=True)
    producto_nombre = Column(String, nullable=False)

    cantidad_solicitada = Column(Integer, nullable=False)
    cantidad_surtida = Column(Integer, default=0, nullable=False)

    estado = Column(String, default="pendiente", nullable=False)
    nota = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    requisicion = relationship("Requisicion", back_populates="detalles")
