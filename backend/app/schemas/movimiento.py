from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class MovimientoCreate(BaseModel):
    producto_id: int
    tipo: str
    cantidad: int
    usuario: str
    recibe: Optional[str] = None
    empleado: Optional[str] = None
    nota: Optional[str] = None


class MovimientoOut(BaseModel):
    id: int
    organizacion_id: int
    producto_id: int
    tipo: str
    cantidad: int
    usuario: str
    recibe: Optional[str] = None
    empleado: Optional[str] = None
    nota: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
