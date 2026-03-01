from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class ProductoBase(BaseModel):
    organizacion_id: int   # ✅ AGREGAR ESTO

    nombre: str
    codigo: Optional[str] = None
    tipo: str = "consumible"          # consumible / herramienta / epp
    cantidad: int = 0                 # stock
    ubicacion: Optional[str] = None
    precio: Optional[float] = None


class ProductoCreate(ProductoBase):
    pass


class ProductoOut(ProductoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: Optional[datetime] = None
