from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint

from app.db.base import Base


class ParkingCliente(Base):
    __tablename__ = "parking_clientes"

    id = Column(Integer, primary_key=True, index=True)
    organizacion_id = Column(Integer, nullable=True, index=True)
    nombre = Column(String(150), nullable=True)
    telefono = Column(String(40), nullable=True)
    placa = Column(String(30), nullable=True, index=True)
    tipo_vehiculo = Column(String(30), nullable=True)
    distinguido = Column(Boolean, default=False, nullable=False)
    activo = Column(Boolean, default=True, nullable=False)
    notas = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


class ParkingTarifa(Base):
    __tablename__ = "parking_tarifas"

    id = Column(Integer, primary_key=True, index=True)
    organizacion_id = Column(Integer, nullable=True, index=True)
    nombre = Column(String(80), nullable=False)
    tipo_vehiculo = Column(String(30), nullable=False, index=True)
    precio_hora = Column(Numeric(10, 2), nullable=False)
    tolerancia_minutos = Column(Integer, default=5, nullable=False)
    activa = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


class ParkingTurno(Base):
    __tablename__ = "parking_turnos"

    id = Column(Integer, primary_key=True, index=True)
    organizacion_id = Column(Integer, nullable=True, index=True)
    usuario_id = Column(Integer, nullable=True, index=True)
    nombre_operador = Column(String(150), nullable=True)
    apertura_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    cierre_at = Column(DateTime(timezone=True), nullable=True)
    fondo_inicial = Column(Numeric(10, 2), default=0, nullable=False)
    efectivo_cierre = Column(Numeric(10, 2), nullable=True)
    estado = Column(String(20), default="abierto", nullable=False, index=True)
    nota = Column(Text, nullable=True)


class ParkingMovimiento(Base):
    __tablename__ = "parking_movimientos"

    id = Column(Integer, primary_key=True, index=True)
    organizacion_id = Column(Integer, nullable=True, index=True)
    turno_id = Column(Integer, ForeignKey("parking_turnos.id"), nullable=True, index=True)
    cliente_id = Column(Integer, ForeignKey("parking_clientes.id"), nullable=True, index=True)
    placa = Column(String(30), nullable=True, index=True)
    tipo_vehiculo = Column(String(30), nullable=False, index=True)
    modelo = Column(String(120), nullable=True)
    color = Column(String(60), nullable=True)
    entrada_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)
    salida_real_at = Column(DateTime(timezone=True), nullable=True)
    cierre_sistema_at = Column(DateTime(timezone=True), nullable=True)
    minutos_cobrados = Column(Integer, default=0, nullable=False)
    importe = Column(Numeric(10, 2), default=0, nullable=False)
    estado = Column(String(30), default="dentro", nullable=False, index=True)
    motivo_sin_estacionarse = Column(String(250), nullable=True)
    nota = Column(Text, nullable=True)
    creado_por = Column(String(150), nullable=True)


class ParkingBano(Base):
    __tablename__ = "parking_banos"

    id = Column(Integer, primary_key=True, index=True)
    organizacion_id = Column(Integer, nullable=True, index=True)
    turno_id = Column(Integer, ForeignKey("parking_turnos.id"), nullable=True, index=True)
    movimiento_id = Column(Integer, ForeignKey("parking_movimientos.id"), nullable=True, index=True)
    tipo_cliente = Column(String(30), default="externo", nullable=False)
    importe = Column(Numeric(10, 2), default=5, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)
    nota = Column(Text, nullable=True)


class ParkingCorte(Base):
    __tablename__ = "parking_cortes"

    id = Column(Integer, primary_key=True, index=True)
    organizacion_id = Column(Integer, nullable=True, index=True)
    turno_id = Column(Integer, ForeignKey("parking_turnos.id"), nullable=False, index=True)
    total_estacionamiento = Column(Numeric(12, 2), default=0, nullable=False)
    total_banos = Column(Numeric(12, 2), default=0, nullable=False)
    total_efectivo = Column(Numeric(12, 2), default=0, nullable=False)
    total_otros = Column(Numeric(12, 2), default=0, nullable=False)
    total = Column(Numeric(12, 2), default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    nota = Column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint("turno_id", name="uq_parking_corte_turno"),
    )
