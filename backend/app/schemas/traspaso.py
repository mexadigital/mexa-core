from datetime import datetime
from pydantic import BaseModel, ConfigDict


class TraspasoCreate(BaseModel):
    producto_id: int
    cantidad: int
    ubicacion_origen_id: int
    ubicacion_destino_id: int


class TraspasoOut(BaseModel):
    id: int
    organizacion_id: int
    producto_id: int
    ubicacion_origen_id: int
    ubicacion_destino_id: int
    cantidad: int
    usuario_id: int
    fecha: datetime

    model_config = ConfigDict(from_attributes=True)
