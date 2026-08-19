from sqlalchemy import Column, Integer, String, DateTime, func

from app.db.base import Base


class Organizacion(Base):
    __tablename__ = "organizaciones"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, nullable=False, index=True)
    rfc = Column(String, unique=True, nullable=False, index=True)
    plan = Column(String, nullable=False, default="free")
    tipo = Column(String, nullable=False, default="control")

    # Identidad institucional usada por MEXA Escolar. Estos campos viven en
    # la organización para que una misma instalación pueda atender a varias
    # escuelas sin tener que cambiar el código ni la plantilla.
    cct = Column(String, nullable=True)
    domicilio = Column(String, nullable=True)
    telefono = Column(String, nullable=True)
    correo_institucional = Column(String, nullable=True)
    logo_url = Column(String, nullable=True)
    firmante_nombre = Column(String, nullable=True)
    firmante_cargo = Column(String, nullable=True)
    ciclo_escolar_actual = Column(String, nullable=True)
    color_primario = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
