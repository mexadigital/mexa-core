from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ConfiguracionEscolarUpdate(BaseModel):
    nombre: str = Field(min_length=2, max_length=160)
    cct: str | None = Field(default=None, max_length=40)
    domicilio: str | None = Field(default=None, max_length=300)
    telefono: str | None = Field(default=None, max_length=30)
    correo_institucional: str | None = Field(default=None, max_length=160)
    logo_url: str | None = Field(default=None, max_length=500)
    firmante_nombre: str | None = Field(default=None, max_length=160)
    firmante_cargo: str | None = Field(default=None, max_length=120)
    ciclo_escolar_actual: str | None = Field(default=None, max_length=30)
    color_primario: str | None = Field(default=None, pattern=r"^#[0-9A-Fa-f]{6}$")


class ConfiguracionEscolarOut(ConfiguracionEscolarUpdate):
    id: int

    class Config:
        from_attributes = True


class GrupoCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=50)
    grado: str | None = Field(default=None, max_length=80)
    ciclo_escolar: str = Field(min_length=4, max_length=30)


class GrupoUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=50)
    grado: str | None = Field(default=None, max_length=80)
    ciclo_escolar: str | None = Field(default=None, min_length=4, max_length=30)
    estado: Literal["activo", "inactivo"] | None = None


class GrupoOut(GrupoCreate):
    id: int
    organizacion_id: int
    estado: str
    created_at: datetime

    class Config:
        from_attributes = True


class AlumnoCreate(BaseModel):
    grupo_id: int
    matricula: str = Field(min_length=1, max_length=60)
    nombre_completo: str = Field(min_length=2, max_length=180)
    nombre_tutor: str | None = Field(default=None, max_length=180)
    telefono_tutor: str | None = Field(default=None, max_length=30)


class AlumnoUpdate(BaseModel):
    grupo_id: int | None = None
    matricula: str | None = Field(default=None, min_length=1, max_length=60)
    nombre_completo: str | None = Field(default=None, min_length=2, max_length=180)
    nombre_tutor: str | None = Field(default=None, max_length=180)
    telefono_tutor: str | None = Field(default=None, max_length=30)
    estado: Literal["activo", "inactivo"] | None = None


class AlumnoOut(AlumnoCreate):
    id: int
    organizacion_id: int
    estado: str
    created_at: datetime

    class Config:
        from_attributes = True


class MateriaCreate(BaseModel):
    nombre: str
    clave: str | None = None


class MateriaOut(MateriaCreate):
    id: int
    organizacion_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class CalificacionCreate(BaseModel):
    alumno_id: int
    materia_id: int
    periodo: str
    valor: float = Field(ge=0, le=10)
    observaciones: str | None = None


class CalificacionOut(CalificacionCreate):
    id: int
    organizacion_id: int
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class MateriaCalificacionOut(BaseModel):
    materia_id: int
    materia: str
    valor: float | None


class BoletaOut(BaseModel):
    alumno_id: int
    matricula: str
    alumno: str
    grupo: str
    ciclo_escolar: str
    periodo: str
    calificaciones: list[MateriaCalificacionOut]
    promedio: float | None


EstadoConstancia = Literal[
    "PAGO_PENDIENTE",
    "SOLICITADA",
    "EN_REVISION",
    "AUTORIZADA",
    "LISTA_PARA_RECOGER",
    "ENTREGADA",
    "CANCELADA",
]


class ConstanciaCreate(BaseModel):
    alumno_id: int
    tipo: str = "constancia_estudios"
    motivo: str | None = None
    destinatario: str | None = None
    medio_entrega: Literal["digital", "recoger_original", "ambos"] = "digital"
    monto: float = Field(default=0, ge=0)
    observaciones: str | None = None


class PagoConstanciaUpdate(BaseModel):
    estado_pago: Literal["PENDIENTE", "PAGADO", "EXENTO", "RECHAZADO"]
    referencia_pago: str | None = None


class ConstanciaOut(BaseModel):
    id: int
    organizacion_id: int
    alumno_id: int
    folio: str
    tipo: str
    motivo: str | None
    destinatario: str | None
    medio_entrega: str
    estado: EstadoConstancia
    estado_pago: str
    monto: float
    referencia_pago: str | None
    requiere_original: bool
    observaciones: str | None
    revisado_por_id: int | None
    autorizado_por_id: int | None
    entregado_por_id: int | None
    created_at: datetime
    updated_at: datetime | None
    revisado_at: datetime | None
    autorizado_at: datetime | None
    entregado_at: datetime | None

    class Config:
        from_attributes = True


class VerificacionConstanciaOut(BaseModel):
    valida: bool
    folio: str
    escuela: str
    cct: str | None = None
    tipo: str
    alumno: str
    matricula: str
    grupo: str
    ciclo_escolar: str
    fecha_emision: datetime
    estado: str
