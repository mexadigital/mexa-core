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


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UsuarioMe(BaseModel):
    id: int
    organizacion_id: int
    nombre: str
    email: EmailStr
    rol: str
    activo: str

    class Config:
        from_attributes = True
