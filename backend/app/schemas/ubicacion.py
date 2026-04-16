from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UbicacionCreate(BaseModel):
    organizacion_id: int
    nombre: str
    tipo: str = "sucursal"


class UbicacionOut(BaseModel):
    id: int
    organizacion_id: int
    nombre: str
    tipo: str
    activo: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
