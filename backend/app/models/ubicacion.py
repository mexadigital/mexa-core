
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from app.db.base import Base


class Ubicacion(Base):
    __tablename__ = "ubicaciones"

    id = Column(Integer, primary_key=True, index=True)
    organizacion_id = Column(Integer, ForeignKey("organizaciones.id"), nullable=False, index=True)
    nombre = Column(String, nullable=False)
    tipo = Column(String, nullable=False)
    activo = Column(Boolean, default=True, nullable=False)
