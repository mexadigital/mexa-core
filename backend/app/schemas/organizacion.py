from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class OrganizacionCreate(BaseModel):
    nombre: str
    rfc: str
    plan: str = "free"
    tipo: str = "control"


class OrganizacionOut(BaseModel):
    id: int
    nombre: str
    rfc: Optional[str] = None
    plan: Optional[str] = "free"
    tipo: Optional[str] = "control"
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
