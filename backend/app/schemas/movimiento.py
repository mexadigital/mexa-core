from pydantic import BaseModel
from datetime import datetime


class MovimientoBase(BaseModel):
    organizacion_id: int
    producto_id: int
    tipo: str
    cantidad: int
    usuario: str


class MovimientoCreate(MovimientoBase):
    pass


class MovimientoOut(MovimientoBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
