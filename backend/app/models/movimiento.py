from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from app.db.base import Base


class Movimiento(Base):
    __tablename__ = "movimientos"

    id = Column(Integer, primary_key=True, index=True)
    organizacion_id = Column(Integer, nullable=False)
    producto_id = Column(Integer, nullable=False)
    tipo = Column(String, nullable=False)
    cantidad = Column(Integer, nullable=False)
    usuario = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
