from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import String, Integer, DateTime, ForeignKey, Enum as SAEnum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

# IMPORTAMOS TU BASE REAL
from app.db import Base


# =========================
# ENUMS
# =========================

class TipoFrente(str, Enum):
    GENERAL = "GENERAL"
    SATELITE = "SATELITE"


class EstadoHerramienta(str, Enum):
    EN_FRENTE = "EN_FRENTE"
    EN_RESGUARDO = "EN_RESGUARDO"
    MANTENIMIENTO = "MANTENIMIENTO"
    BAJA = "BAJA"


class TipoMovimientoHerramienta(str, Enum):
    TRASPASO_FRENTE = "TRASPASO_FRENTE"
    SALIDA_RESGUARDO = "SALIDA_RESGUARDO"
    DEVOLUCION_A_FRENTE = "DEVOLUCION_A_FRENTE"
    TRASPASO_RESGUARDO = "TRASPASO_RESGUARDO"
    MANTENIMIENTO = "MANTENIMIENTO"
    BAJA = "BAJA"


# =========================
# MODELOS
# =========================

class Frente(Base):
    __tablename__ = "frentes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    tipo: Mapped[TipoFrente] = mapped_column(SAEnum(TipoFrente), nullable=False)
    activo: Mapped[int] = mapped_column(Integer, default=1, nullable=False)


class Trabajador(Base):
    __tablename__ = "trabajadores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    numero_empleado: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(160), nullable=False)
    activo: Mapped[int] = mapped_column(Integer, default=1, nullable=False)


class Producto(Base):
    __tablename__ = "productos_serial"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)


class Herramienta(Base):
    __tablename__ = "herramientas"

    __table_args__ = (
        UniqueConstraint("numero_serie", name="uq_herramienta_numero_serie"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    producto_id: Mapped[int] = mapped_column(ForeignKey("productos_serial.id"), nullable=False)
    numero_serie: Mapped[str] = mapped_column(String(80), nullable=False)

    estado: Mapped[EstadoHerramienta] = mapped_column(
        SAEnum(EstadoHerramienta),
        default=EstadoHerramienta.EN_FRENTE,
        nullable=False
    )

    frente_actual_id: Mapped[Optional[int]] = mapped_column(ForeignKey("frentes.id"), nullable=True)
    trabajador_actual_id: Mapped[Optional[int]] = mapped_column(ForeignKey("trabajadores.id"), nullable=True)

    fecha_alta: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    nota: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)


class MovimientoHerramienta(Base):
    __tablename__ = "movimientos_herramienta"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    herramienta_id: Mapped[int] = mapped_column(ForeignKey("herramientas.id"), nullable=False)

    tipo: Mapped[TipoMovimientoHerramienta] = mapped_column(
        SAEnum(TipoMovimientoHerramienta),
        nullable=False
    )

    frente_origen_id: Mapped[Optional[int]] = mapped_column(ForeignKey("frentes.id"), nullable=True)
    frente_destino_id: Mapped[Optional[int]] = mapped_column(ForeignKey("frentes.id"), nullable=True)

    trabajador_origen_id: Mapped[Optional[int]] = mapped_column(ForeignKey("trabajadores.id"), nullable=True)
    trabajador_destino_id: Mapped[Optional[int]] = mapped_column(ForeignKey("trabajadores.id"), nullable=True)

    usuario: Mapped[Optional[str]] = mapped_column(String(160), nullable=True)
    folio_vale: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    nota: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)

    fecha: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
