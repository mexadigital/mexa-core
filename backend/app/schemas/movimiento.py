from pydantic import BaseModel
from datetime import datetime
from typing import Literal


class MovimientoCreate(BaseModel):
    producto_id: int
    tipo: Literal["entrada", "salida"]
    cantidad: int


class MovimientoOut(BaseModel):
    id: int
    organizacion_id: int
    producto_id: int
    tipo: str
    cantidad: int
    usuario: str
    created_at: datetime

    class Config:
        from_attributes = True
