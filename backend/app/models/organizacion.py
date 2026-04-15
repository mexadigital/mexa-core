from sqlalchemy import Column, Integer, String, DateTime, func

from app.db.base import Base


class Organizacion(Base):
    __tablename__ = "organizaciones"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, nullable=False, index=True)
    rfc = Column(String, unique=True, nullable=False, index=True)
    plan = Column(String, nullable=False, default="free")
    tipo = Column(String, nullable=False, default="control")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
