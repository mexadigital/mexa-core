from pydantic import BaseModel
from typing import List
from datetime import datetime


class VentaItemCreate(BaseModel):
    producto_id: int
    cantidad: int


class VentaCreate(BaseModel):
    productos: List[VentaItemCreate]


class VentaDetalleOut(BaseModel):
    producto_id: int
    cantidad: int
    precio_unitario: float
    subtotal: float

    model_config = {
        "from_attributes": True
    }


class VentaOut(BaseModel):
    id: int
    organizacion_id: int
    usuario_id: int
    total: float
    created_at: datetime
    detalles: List[VentaDetalleOut]

    model_config = {
        "from_attributes": True
    }
