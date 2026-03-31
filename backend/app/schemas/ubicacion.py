from pydantic import BaseModel
from typing import Optional


class UbicacionCreate(BaseModel):
    nombre: str
    tipo: str
    activo: Optional[bool] = True


class UbicacionUpdate(BaseModel):
    nombre: Optional[str] = None
    tipo: Optional[str] = None
    activo: Optional[bool] = None


class UbicacionOut(BaseModel):
    id: int
    organizacion_id: int
    nombre: str
    tipo: str
    activo: bool

    class Config:
        from_attributes = True
