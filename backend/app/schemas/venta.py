from datetime import datetime
from pydantic import BaseModel, ConfigDict


class VentaCreate(BaseModel):
    producto_id: int
    ubicacion_id: int
    cantidad: int


class VentaOut(BaseModel):
    id: int
    organizacion_id: int
    producto_id: int
    ubicacion_id: int
    cantidad: int
    precio_unitario: float
    total: float
    usuario_id: int
    fecha: datetime

    model_config = ConfigDict(from_attributes=True)
