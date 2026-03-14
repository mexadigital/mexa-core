from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func

from app.db.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    organizacion_id = Column(Integer, ForeignKey("organizaciones.id"), nullable=False)
    nombre = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    activo = Column(String, default="si")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
