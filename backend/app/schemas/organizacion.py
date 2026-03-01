from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class OrganizacionCreate(BaseModel):
    nombre: str
    rfc: Optional[str] = None
    plan: str = "free"


class OrganizacionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    rfc: Optional[str] = None
    plan: str
    created_at: datetime
