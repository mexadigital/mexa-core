from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class ValeResguardo(Base):
    __tablename__ = "vales_resguardo"

    id = Column(Integer, primary_key=True, index=True)

    organizacion_id = Column(Integer, ForeignKey("organizaciones.id"), nullable=False)

    folio_sistema = Column(String, index=True, nullable=False)  # A0001
    numero_vale_fisico = Column(String, nullable=True)

    empleado_recibe = Column(String, index=True, nullable=False)
    numero_empleado = Column(String, index=True, nullable=True)
    puesto = Column(String, nullable=True)
    area_frente = Column(String, nullable=True)

    ubicacion_origen = Column(String, nullable=True)
    ubicacion_fisica_vale = Column(String, nullable=True)  # Carpeta A / A0001-A0050
    estado_archivo_fisico = Column(String, default="pendiente_archivar")

    foto_url = Column(Text, nullable=True)

    estado_vale = Column(String, default="abierto")  # abierto, parcial, cerrado, cancelado
    nota = Column(Text, nullable=True)

    usuario_creador = Column(String, nullable=True)

    fecha_entrega = Column(DateTime(timezone=True), server_default=func.now())
    fecha_cierre = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    detalles = relationship(
        "ValeResguardoDetalle",
        back_populates="vale",
        cascade="all, delete-orphan"
    )


class ValeResguardoDetalle(Base):
    __tablename__ = "vales_resguardo_detalle"

    id = Column(Integer, primary_key=True, index=True)

    vale_id = Column(Integer, ForeignKey("vales_resguardo.id"), nullable=False)

    herramienta_nombre = Column(String, nullable=False)
    item_code = Column(String, nullable=True)
    medida_size = Column(String, nullable=True)
    unidad = Column(String, nullable=True)

    marca = Column(String, nullable=True)
    modelo = Column(String, nullable=True)
    serie = Column(String, nullable=True)

    cantidad_entregada = Column(Integer, default=1)
    cantidad_devuelta = Column(Integer, default=0)

    estado = Column(String, default="pendiente")  # pendiente, parcial, devuelto, dañado, perdido
    observacion = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    vale = relationship("ValeResguardo", back_populates="detalles")
