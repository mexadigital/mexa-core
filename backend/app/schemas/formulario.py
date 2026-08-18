from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


TipoCampo = Literal["texto", "numero", "fecha", "telefono", "seleccion", "parrafo"]


class CampoCreate(BaseModel):
    clave: str = Field(min_length=1, max_length=60, pattern=r"^[a-z0-9_]+$")
    etiqueta: str = Field(min_length=1, max_length=120)
    tipo: TipoCampo = "texto"
    obligatorio: bool = False
    orden: int = 0
    opciones: str | None = None

    @field_validator("opciones")
    @classmethod
    def validar_opciones(cls, value: str | None):
        if value is None:
            return value
        limpio = ",".join(item.strip() for item in value.split(",") if item.strip())
        return limpio or None


class CampoOut(CampoCreate):
    id: int
    formulario_id: int

    class Config:
        from_attributes = True


class FormularioCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=120)
    descripcion: str | None = Field(default=None, max_length=300)


class FormularioOut(FormularioCreate):
    id: int
    organizacion_id: int
    estado: str
    created_at: datetime
    campos: list[CampoOut] = Field(default_factory=list)

    class Config:
        from_attributes = True


class ValorEntrada(BaseModel):
    campo_id: int
    valor: str | None = None


class RegistroCreate(BaseModel):
    valores: list[ValorEntrada]


class ValorOut(BaseModel):
    campo_id: int
    clave: str
    etiqueta: str
    valor: str | None


class RegistroOut(BaseModel):
    id: int
    formulario_id: int
    formulario: str
    folio: str
    estado: str
    created_at: datetime
    valores: list[ValorOut]
