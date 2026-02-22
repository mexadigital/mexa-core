from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class ProductoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    unidad: Optional[str] = None
    codigo: Optional[str] = None
    categoria: Optional[str] = None


class ProductoCreate(ProductoBase):
    pass


class ProductoOut(ProductoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    activo: bool = True
    creado_en: Optional[datetime] = None
    actualizado_en: Optional[datetime] = None
