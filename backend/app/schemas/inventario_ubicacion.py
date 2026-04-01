from pydantic import BaseModel, ConfigDict


class InventarioUbicacionAsignar(BaseModel):
    producto_id: int
    ubicacion_id: int
    cantidad: int


class InventarioUbicacionOut(BaseModel):
    id: int
    organizacion_id: int
    producto_id: int
    ubicacion_id: int
    cantidad: int

    model_config = ConfigDict(from_attributes=True)
