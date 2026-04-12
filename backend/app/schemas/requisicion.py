from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field


class RequisicionDetalleCreate(BaseModel):
    producto_id: int
    producto_nombre: str
    cantidad_solicitada: int = Field(gt=0)
    nota: Optional[str] = None


class RequisicionCreate(BaseModel):
    solicitante: str
    nota: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = {}
    detalles: List[RequisicionDetalleCreate]


class RequisicionDetalleSurtir(BaseModel):
    detalle_id: int
    cantidad_surtida: int = Field(ge=0)


class RequisicionSurtir(BaseModel):
    detalles: List[RequisicionDetalleSurtir]
    nota: Optional[str] = None


class RequisicionDetalleOut(BaseModel):
    id: int
    producto_id: int
    producto_nombre: str
    cantidad_solicitada: int
    cantidad_surtida: int
    estado: str
    nota: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class RequisicionOut(BaseModel):
    id: int
    organizacion_id: int
    folio: str
    solicitante: str
    estado: str
    nota: Optional[str] = None
    extra_data: Dict[str, Any]
    created_at: datetime
    detalles: List[RequisicionDetalleOut]

    class Config:
        from_attributes = True
