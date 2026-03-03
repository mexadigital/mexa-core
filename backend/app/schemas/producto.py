from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ProductoBase(BaseModel):
    organizacion_id: int

    nombre: str
    codigo: Optional[str] = None
    tipo: str = "consumible"
    cantidad: int = 0
    ubicacion: Optional[str] = None
    precio: Optional[float] = None


class ProductoCreate(ProductoBase):
    pass


class ProductoOut(ProductoBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
