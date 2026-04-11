from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class MovimientoCreate(BaseModel):
    producto_id: int
    tipo: Literal["entrada", "salida"]
    cantidad: int

    # Campos opcionales tipo vale
    recibe: str | None = None
    empleado: str | None = None
    nota: str | None = None


class MovimientoOut(BaseModel):
    id: int
    organizacion_id: int
    producto_id: int
    tipo: str
    cantidad: int
    usuario: str

    recibe: str | None = None
    empleado: str | None = None
    nota: str | None = None

    created_at: datetime

    class Config:
        from_attributes = True
