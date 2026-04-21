from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ProductoBase(BaseModel):
    nombre: str
    codigo: str
    tipo: str = "consumible"
    cantidad: int = 0
    ubicacion: Optional[str] = None
    precio: Optional[float] = 0


class ProductoCreate(ProductoBase):
    pass


class ProductoUpdate(BaseModel):
    nombre: Optional[str] = None
    codigo: Optional[str] = None
    tipo: Optional[str] = None
    cantidad: Optional[int] = None
    ubicacion: Optional[str] = None
    precio: Optional[float] = None


class ProductoOut(BaseModel):
    id: int
    organizacion_id: int
    nombre: str
    codigo: str
    tipo: str
    cantidad: int
    ubicacion: Optional[str] = None
    precio: Optional[float] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
