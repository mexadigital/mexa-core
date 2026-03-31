from pydantic import BaseModel


class InventarioOut(BaseModel):
    producto_id: int
    ubicacion_id: int
    cantidad: int

    class Config:
        from_attributes = True
