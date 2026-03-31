from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint

from app.db.base import Base


class Inventario(Base):
    __tablename__ = "inventario"

    id = Column(Integer, primary_key=True, index=True)

    organizacion_id = Column(Integer, nullable=False, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    ubicacion_id = Column(Integer, ForeignKey("ubicaciones.id"), nullable=False)

    cantidad = Column(Integer, default=0, nullable=False)

    __table_args__ = (
        UniqueConstraint("producto_id", "ubicacion_id", name="uq_producto_ubicacion"),
    )
