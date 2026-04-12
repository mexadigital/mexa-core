from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel, Field


class RequisicionDetalleCreate(BaseModel):
    producto_id: Optional[int] = None
    producto_nombre: str
    cantidad_solicitada: int = Field(gt=0)
    nota: Optional[str] = None


class RequisicionCreate(BaseModel):
    solicitante: str
    nota: Optional[str] = None
    extra_data: Optional[dict[str, Any]] = None
    detalles: list[RequisicionDetalleCreate]


class RequisicionDetalleOut(BaseModel):
    id: int
    producto_id: Optional[int] = None
    producto_nombre: str
    cantidad_solicitada: int
    cantidad_surtida: int
    estado: str
    nota: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class RequisicionOut(BaseModel):
    id: int
    organizacion_id: int
    folio: str
    solicitante: str
    estado: str
    nota: Optional[str] = None
    extra_data: Optional[dict[str, Any]] = None
    created_at: datetime
    detalles: list[RequisicionDetalleOut]

    model_config = {"from_attributes": True}
