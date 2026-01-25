from pydantic import BaseModel, Field
from typing import List, Optional, Literal

Kind = Literal["HERRAMIENTA", "EPP", "CONSUMIBLE"]
Motive = Literal["PRESTAMO", "TRASPASO", "ENTREGA", "CONSUMO"]

class WorkerUpsert(BaseModel):
    employee_no: str = Field(min_length=1)
    name: str = Field(min_length=1)

class ValeItemCreate(BaseModel):
    kind: Kind
    item_name: str = Field(min_length=1)
    qty: int = Field(ge=1)
    origin_location: str = Field(min_length=1)  # SC-16, MC-06...
    motive: Motive
    note: Optional[str] = None

class ValeCreate(BaseModel):
    employee_no: str = Field(min_length=1)
    employee_name: Optional[str] = None  # si no existe en padrón, lo mandas aquí
    comment: Optional[str] = None
    signed_physical: bool = False
    safety_engineer: Optional[str] = None
    items: List[ValeItemCreate]

class ValeSummary(BaseModel):
    id: int
    employee_no: str
    employee_name: str
    status: str
    pending_tools: int
    created_at: str

class ValeDetail(BaseModel):
    id: int
    employee_no: str
    employee_name: str
    comment: Optional[str]
    signed_physical: bool
    safety_engineer: Optional[str]
    photo_path: Optional[str]
    status: str
    created_at: str
    closed_at: Optional[str]
    items: list

class ToolReturn(BaseModel):
    note: Optional[str] = None
