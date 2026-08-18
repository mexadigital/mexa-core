from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship

from app.db.base import Base


class GrupoEscolar(Base):
    __tablename__ = "grupos_escolares"
    __table_args__ = (
        UniqueConstraint(
            "organizacion_id",
            "nombre",
            "ciclo_escolar",
            name="uq_grupo_organizacion_nombre_ciclo",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    organizacion_id = Column(
        Integer,
        ForeignKey("organizaciones.id"),
        nullable=False,
        index=True,
    )
    nombre = Column(String, nullable=False, index=True)
    grado = Column(String, nullable=True)
    ciclo_escolar = Column(String, nullable=False)
    estado = Column(String, nullable=False, default="activo")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    alumnos = relationship("Alumno", back_populates="grupo")


class Alumno(Base):
    __tablename__ = "alumnos"
    __table_args__ = (
        UniqueConstraint(
            "organizacion_id",
            "matricula",
            name="uq_alumno_organizacion_matricula",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    organizacion_id = Column(
        Integer,
        ForeignKey("organizaciones.id"),
        nullable=False,
        index=True,
    )
    grupo_id = Column(
        Integer,
        ForeignKey("grupos_escolares.id"),
        nullable=False,
        index=True,
    )
    matricula = Column(String, nullable=False, index=True)
    nombre_completo = Column(String, nullable=False, index=True)
    telefono_tutor = Column(String, nullable=True)
    estado = Column(String, nullable=False, default="activo")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    grupo = relationship("GrupoEscolar", back_populates="alumnos")
    calificaciones = relationship("Calificacion", back_populates="alumno")
    solicitudes_constancia = relationship(
        "SolicitudConstancia", back_populates="alumno"
    )


class Materia(Base):
    __tablename__ = "materias"
    __table_args__ = (
        UniqueConstraint(
            "organizacion_id",
            "nombre",
            name="uq_materia_organizacion_nombre",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    organizacion_id = Column(
        Integer,
        ForeignKey("organizaciones.id"),
        nullable=False,
        index=True,
    )
    nombre = Column(String, nullable=False, index=True)
    clave = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Calificacion(Base):
    __tablename__ = "calificaciones"
    __table_args__ = (
        UniqueConstraint(
            "alumno_id",
            "materia_id",
            "periodo",
            name="uq_calificacion_alumno_materia_periodo",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    organizacion_id = Column(
        Integer,
        ForeignKey("organizaciones.id"),
        nullable=False,
        index=True,
    )
    alumno_id = Column(Integer, ForeignKey("alumnos.id"), nullable=False, index=True)
    materia_id = Column(Integer, ForeignKey("materias.id"), nullable=False, index=True)
    periodo = Column(String, nullable=False, index=True)
    valor = Column(Float, nullable=False)
    observaciones = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    alumno = relationship("Alumno", back_populates="calificaciones")
    materia = relationship("Materia")


class SolicitudConstancia(Base):
    __tablename__ = "solicitudes_constancia"
    __table_args__ = (
        UniqueConstraint(
            "organizacion_id",
            "folio",
            name="uq_constancia_organizacion_folio",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    organizacion_id = Column(
        Integer,
        ForeignKey("organizaciones.id"),
        nullable=False,
        index=True,
    )
    alumno_id = Column(Integer, ForeignKey("alumnos.id"), nullable=False, index=True)
    folio = Column(String, nullable=False, index=True)
    token_verificacion = Column(String, unique=True, nullable=False, index=True)
    tipo = Column(String, nullable=False, default="constancia_estudios")
    motivo = Column(String, nullable=True)
    destinatario = Column(String, nullable=True)
    medio_entrega = Column(String, nullable=False, default="digital")
    estado = Column(String, nullable=False, default="SOLICITADA", index=True)
    estado_pago = Column(String, nullable=False, default="PENDIENTE", index=True)
    monto = Column(Float, nullable=False, default=0.0)
    referencia_pago = Column(String, nullable=True)
    requiere_original = Column(Boolean, nullable=False, default=False)
    observaciones = Column(String, nullable=True)
    revisado_por_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    autorizado_por_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    entregado_por_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    revisado_at = Column(DateTime(timezone=True), nullable=True)
    autorizado_at = Column(DateTime(timezone=True), nullable=True)
    entregado_at = Column(DateTime(timezone=True), nullable=True)

    alumno = relationship("Alumno", back_populates="solicitudes_constancia")
    organizacion = relationship("Organizacion")
    revisado_por = relationship("Usuario", foreign_keys=[revisado_por_id])
    autorizado_por = relationship("Usuario", foreign_keys=[autorizado_por_id])
    entregado_por = relationship("Usuario", foreign_keys=[entregado_por_id])
