from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MovimientoCreate(BaseModel):
    organizacion_id: int
    producto_id: int
    tipo: str          # "entrada" | "salida"
    cantidad: int
    usuario: str
    nota: Optional[str] = None

class MovimientoOut(BaseModel):
    id: int
    organizacion_id: int
    producto_id: int
    tipo: str
    cantidad: int
    usuario: str
    nota: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
