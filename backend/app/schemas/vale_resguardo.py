from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ValeResguardoDetalleCreate(BaseModel):
    herramienta_nombre: str
    item_code: Optional[str] = None
    medida_size: Optional[str] = None
    unidad: Optional[str] = None
    marca: Optional[str] = None
    modelo: Optional[str] = None
    serie: Optional[str] = None
    cantidad_entregada: int = 1
    observacion: Optional[str] = None


class ValeResguardoCreate(BaseModel):
    numero_vale_fisico: Optional[str] = None

    empleado_recibe: str
    numero_empleado: Optional[str] = None
    puesto: Optional[str] = None
    area_frente: Optional[str] = None

    ubicacion_origen: Optional[str] = None
    ubicacion_fisica_vale: Optional[str] = "Carpeta A"
    estado_archivo_fisico: Optional[str] = "pendiente_archivar"

    foto_url: Optional[str] = None
    nota: Optional[str] = None

    detalles: List[ValeResguardoDetalleCreate] = Field(default_factory=list)


class ValeResguardoDetalleOut(BaseModel):
    id: int
    herramienta_nombre: str
    item_code: Optional[str]
    medida_size: Optional[str]
    unidad: Optional[str]
    marca: Optional[str]
    modelo: Optional[str]
    serie: Optional[str]
    cantidad_entregada: int
    cantidad_devuelta: int
    estado: str
    observacion: Optional[str]

    class Config:
        from_attributes = True


class ValeResguardoOut(BaseModel):
    id: int
    folio_sistema: str
    numero_vale_fisico: Optional[str]

    empleado_recibe: str
    numero_empleado: Optional[str]
    puesto: Optional[str]
    area_frente: Optional[str]

    ubicacion_origen: Optional[str]
    ubicacion_fisica_vale: Optional[str]
    estado_archivo_fisico: Optional[str]

    foto_url: Optional[str]
    estado_vale: str
    nota: Optional[str]

    usuario_creador: Optional[str]

    fecha_entrega: datetime
    fecha_cierre: Optional[datetime]

    detalles: List[ValeResguardoDetalleOut] = Field(default_factory=list)

    class Config:
        from_attributes = True


class DevolucionDetalle(BaseModel):
    detalle_id: int
    cantidad_devuelta: int
    observacion: Optional[str] = None


class DevolucionVale(BaseModel):
    devoluciones: List[DevolucionDetalle] = Field(default_factory=list)


class CambiarArchivoFisico(BaseModel):
    ubicacion_fisica_vale: str
    estado_archivo_fisico: str = "archivado"


class AgregarDetalleVale(BaseModel):
    herramienta_nombre: str
    item_code: Optional[str] = None
    medida_size: Optional[str] = None
    unidad: Optional[str] = None
    marca: Optional[str] = None
    modelo: Optional[str] = None
    serie: Optional[str] = None
    cantidad_entregada: int = 1
    observacion: Optional[str] = None
