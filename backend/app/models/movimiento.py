from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from app.db.base import Base


class Movimiento(Base):
    __tablename__ = "movimientos"

    id = Column(Integer, primary_key=True, index=True)

    organizacion_id = Column(
        Integer,
        ForeignKey("organizaciones.id"),
        nullable=False,
        index=True
    )

    producto_id = Column(
        Integer,
        ForeignKey("productos.id"),
        nullable=False,
        index=True
    )

    ubicacion_id = Column(
        Integer,
        ForeignKey("ubicaciones.id"),
        nullable=True,
        index=True
    )

    tipo = Column(String, nullable=False)  # entrada / salida
    cantidad = Column(Integer, nullable=False)

    usuario = Column(String, nullable=True)
    recibe = Column(String, nullable=True)
    empleado = Column(String, nullable=True)
    nota = Column(String, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
