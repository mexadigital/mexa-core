from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.base import Base


class Organizacion(Base):
    __tablename__ = "organizaciones"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False, index=True)
    rfc = Column(String, nullable=True, index=True)
    plan = Column(String, nullable=False, default="free")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
