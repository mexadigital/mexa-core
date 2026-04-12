from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Requisicion(Base):
    __tablename__ = "requisiciones"

    id = Column(Integer, primary_key=True, index=True)
    organizacion_id = Column(Integer, ForeignKey("organizaciones.id"), nullable=False, index=True)

    folio = Column(String, unique=True, index=True, nullable=False)
    solicitante = Column(String, nullable=False)
    estado = Column(String, default="pendiente", nullable=False)
    nota = Column(Text, nullable=True)

    # Aquí guardas datos flexibles:
    # frente, planta, disciplina, prioridad, etc.
    extra_data = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    detalles = relationship(
        "RequisicionDetalle",
        back_populates="requisicion",
        cascade="all, delete-orphan",
    )
