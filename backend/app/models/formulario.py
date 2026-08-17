from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship

from app.db.base import Base


class Formulario(Base):
    """Definición reutilizable de un formato creado por una organización."""

    __tablename__ = "formularios"
    __table_args__ = (
        UniqueConstraint(
            "organizacion_id",
            "nombre",
            name="uq_formulario_organizacion_nombre",
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
    descripcion = Column(String, nullable=True)
    estado = Column(String, nullable=False, default="activo")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    campos = relationship(
        "CampoFormulario",
        back_populates="formulario",
        cascade="all, delete-orphan",
        order_by="CampoFormulario.orden",
    )
    registros = relationship("RegistroFormulario", back_populates="formulario")


class CampoFormulario(Base):
    """Una pregunta/campo perteneciente a un formulario."""

    __tablename__ = "campos_formulario"
    __table_args__ = (
        UniqueConstraint(
            "formulario_id",
            "clave",
            name="uq_campo_formulario_clave",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    formulario_id = Column(
        Integer,
        ForeignKey("formularios.id"),
        nullable=False,
        index=True,
    )
    clave = Column(String, nullable=False)
    etiqueta = Column(String, nullable=False)
    tipo = Column(String, nullable=False, default="texto")
    obligatorio = Column(Boolean, nullable=False, default=False)
    orden = Column(Integer, nullable=False, default=0)
    opciones = Column(Text, nullable=True)

    formulario = relationship("Formulario", back_populates="campos")


class RegistroFormulario(Base):
    """Una respuesta completa capturada usando un formulario."""

    __tablename__ = "registros_formulario"

    id = Column(Integer, primary_key=True, index=True)
    organizacion_id = Column(
        Integer,
        ForeignKey("organizaciones.id"),
        nullable=False,
        index=True,
    )
    formulario_id = Column(
        Integer,
        ForeignKey("formularios.id"),
        nullable=False,
        index=True,
    )
    creado_por_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    folio = Column(String, nullable=False, index=True)
    estado = Column(String, nullable=False, default="capturado")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    formulario = relationship("Formulario", back_populates="registros")
    valores = relationship(
        "ValorRegistro",
        back_populates="registro",
        cascade="all, delete-orphan",
    )


class ValorRegistro(Base):
    """Valor de un campo dentro de un registro."""

    __tablename__ = "valores_registro"
    __table_args__ = (
        UniqueConstraint(
            "registro_id",
            "campo_id",
            name="uq_valor_registro_campo",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    registro_id = Column(
        Integer,
        ForeignKey("registros_formulario.id"),
        nullable=False,
        index=True,
    )
    campo_id = Column(
        Integer,
        ForeignKey("campos_formulario.id"),
        nullable=False,
        index=True,
    )
    valor = Column(Text, nullable=True)

    registro = relationship("RegistroFormulario", back_populates="valores")
    campo = relationship("CampoFormulario")
