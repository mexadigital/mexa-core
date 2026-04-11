from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey

from app.db.database import Base


class Movimiento(Base):
    __tablename__ = "movimientos"

    id = Column(Integer, primary_key=True, index=True)

    organizacion_id = Column(Integer, nullable=False, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False, index=True)

    tipo = Column(String, nullable=False)  # entrada | salida
    cantidad = Column(Integer, nullable=False)

    # Usuario autenticado que registró el movimiento
    usuario = Column(String, nullable=False)

    # Datos tipo vale / entrega
    recibe = Column(String, nullable=True)
    empleado = Column(String, nullable=True)
    nota = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
