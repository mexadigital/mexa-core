from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from app.db.base import Base


class InventarioUbicacion(Base):
    __tablename__ = "inventario_ubicacion"

    __table_args__ = (
        UniqueConstraint(
            "organizacion_id",
            "producto_id",
            "ubicacion_id",
            name="uq_inventario_ubicacion"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    organizacion_id = Column(Integer, ForeignKey("organizaciones.id"), nullable=False, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False, index=True)
    ubicacion_id = Column(Integer, ForeignKey("ubicaciones.id"), nullable=False, index=True)
    cantidad = Column(Integer, nullable=False, default=0)
