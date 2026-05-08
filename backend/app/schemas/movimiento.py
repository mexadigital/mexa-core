from datetime import datetime
from pydantic import BaseModel


class MovimientoBase(BaseModel):
    producto_id: int
    ubicacion_id: int
    tipo: str
    cantidad: int
    usuario: str
    recibe: str | None = None
    empleado: str | None = None
    nota: str | None = None


class MovimientoCreate(MovimientoBase):
    pass


class MovimientoOut(MovimientoBase):
    id: int
    organizacion_id: int
    created_at: datetime

    class Config:
        from_attributes = True
