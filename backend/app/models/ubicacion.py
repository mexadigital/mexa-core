from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, func

from app.db.base import Base


class Ubicacion(Base):
    __tablename__ = "ubicaciones"

    id = Column(Integer, primary_key=True, index=True)
    organizacion_id = Column(Integer, ForeignKey("organizaciones.id"), nullable=False)

    nombre = Column(String, nullable=False)
    tipo = Column(String, nullable=False, default="sucursal")
    activo = Column(Boolean, nullable=False, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
