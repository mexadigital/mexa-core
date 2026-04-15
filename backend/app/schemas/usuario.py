from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UsuarioCreate(BaseModel):
    organizacion_id: int
    nombre: str
    email: EmailStr
    password: str
    rol: str = "usuario"


class UsuarioLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UsuarioOut(BaseModel):
    id: int
    organizacion_id: int
    nombre: str
    email: EmailStr
    rol: str
    activo: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UsuarioMe(BaseModel):
    id: int
    organizacion_id: int
    nombre: str
    email: EmailStr
    rol: str
    activo: str
    organizacion_nombre: str
    organizacion_tipo: str

    class Config:
        from_attributes = True
